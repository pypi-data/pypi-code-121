from monai.inferers import sliding_window_inference
from monai.transforms import AsDiscrete, BatchInverseTransform
from monai.transforms.utils import allow_missing_keys_mode
from monai.data import ArrayDataset, DataLoader, CacheDataset, Dataset
import torch
import numpy as np
from PIL import Image
from skimage.measure import regionprops, label, regionprops_table, find_contours
from scipy.spatial import ConvexHull
import pandas as pd
import math
from torchcontrib.optim import SWA
from torchmetrics import JaccardIndex
from monai.transforms import Zoom, CenterScaleCrop

def predict( model
           , data_val
           , trans_val
           , list_data_names
           , metric
           , roi_size
           , postprocessing_list
           , device
           , caching_factor
           , invert_trans_val
           , zoom_factor
           ):
    val_ds = CacheDataset( data=data_val
                         , transform=trans_val
                         , cache_rate = caching_factor
                         , num_workers=0
                         )
    val_loader = DataLoader( dataset=val_ds
                           , batch_size=1
                           , num_workers=0
                           , shuffle=False
                           , pin_memory=torch.cuda.is_available()
                           )
    metric_list = []
    list_predictions = []
    model.eval()
    dict_predictions = {}
    dict_metrics = {}
    with torch.no_grad():
        metric_sum = 0.0
        metric_count = 0
        metric_val = None
        for i, val_data in enumerate(val_loader):
            val_labels = None
            val_outputs = None
            val_images = val_data["img"].to(device, dtype=torch.float)
            if "seg" in val_data.keys():
                val_labels = val_data["seg"].to(device, dtype=torch.float)
            sw_batch_size = 1
            val_outputs = sliding_window_inference(val_images, roi_size, sw_batch_size, model)
            val_outputs = postprocessing_list(val_outputs)
            list_predictions.append(val_outputs)
            if "seg" in val_data.keys(): 
                val_labels = (val_labels > 0.5)
                value = metric(y_pred=val_outputs, y=val_labels)
                IoU = JaccardIndex(num_classes=2)
                IoU_value = IoU(val_outputs.cpu(), val_labels.cpu())
                dict_metrics[list_data_names[i]] = value[0][0].cpu().detach().numpy()
                metric_count += len(value)
                metric_sum += value.item() * len(value)
                metric_val = metric_sum / metric_count
            batch_inverter = BatchInverseTransform(invert_trans_val, val_loader)
            #print(val_data)
            segs_dict = {"label": val_outputs,
                        "label_transforms": val_data["img_transforms"]}
            with allow_missing_keys_mode(invert_trans_val):
                val_outputs = batch_inverter(segs_dict)
            #print(val_outputs[0]["label"])
            #prediction_mask = val_outputs.cpu().data.numpy()[0, 0, :, :] * 255
            #prediction_mask = val_outputs[0]["label"].cpu().data.numpy()[0, :, :] * 255
            prediction_mask = val_outputs[0]["label"]
            zoom_array = Zoom(zoom = 1/zoom_factor)
            zoom_result = zoom_array(prediction_mask)
            centerscale_crop = CenterScaleCrop(roi_scale=1/zoom_factor)
            result = centerscale_crop(zoom_result)
            dict_predictions[list_data_names[i]] = result.cpu().data.numpy()[0, :, :] * 255
        if metric_val is not None:
            print("metric: {:.4f}".format(metric_val))
            print("IoU: {}".format(IoU_value))
    dict_metrics["average"] = metric_val
    return dict_predictions, dict_metrics


def train(model
          , swa_model
          , data_train
          , trans_train
          , data_val
          , trans_val
          , num_epochs
          , batch_size
          , val_int
          , loss
          , opt
          , metric
          , postprocessing_list
          , device
          , caching_factor
          ):
    train_ds = CacheDataset( data=data_train
                           , transform=trans_train
                           , cache_rate = caching_factor
                           , num_workers=8
                           )
    val_ds = CacheDataset( data = data_val
                         , transform = trans_val
                         , cache_rate = caching_factor
                         , num_workers=8
                        )
    train_loader = DataLoader(dataset=train_ds
                              , batch_size=batch_size
                              , num_workers=1
                              , shuffle=True
                              , pin_memory=torch.cuda.is_available()
                              )
    val_loader = DataLoader(dataset=val_ds
                            , batch_size=1
                            , num_workers=4
                            , shuffle=True
                            , pin_memory=torch.cuda.is_available()
                            )

    step_losses = []
    epoch_metrics = []
    total_step = 0
    best_metric_model = 0
    best_metric_swa = 0
    best_model = None
    best_model_swa = None
    if swa_model == None:
        swa_model = torch.optim.swa_utils.AveragedModel(model)
    # scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max = num_epochs)
    swa_start = int((2. / 3) * num_epochs)
    swa_scheduler = torch.optim.swa_utils.SWALR(opt, swa_lr=0.05)
    
    for epoch in range(num_epochs):
        scheduler = torch.optim.lr_scheduler.LambdaLR( opt
                                                     , lr_lambda=lambda epoch: (1 - epoch / num_epochs) ** 0.9
                                                     )
        print("-" * 10)
        print(f"epoch {epoch + 1}/{num_epochs}")
        model.train()
        epoch_loss = 0
        step = 0
        for batch in train_loader:
            step += 1
            bimages = batch["img"].to(device, dtype=torch.float)
            bsegs = batch["seg"].to(device, dtype=torch.float)
            opt.zero_grad()
            prediction = model(bimages)
            loss_train = loss(prediction, bsegs)
            loss_train.backward()
            opt.step()
            epoch_loss += loss_train.item()
            epoch_len = len(train_ds) // train_loader.batch_size
            print(f"{step}/{epoch_len+1}, train_loss: {loss_train.item():.4f}")
        epoch_loss /= step
        print(f"epoch {epoch + 1} average loss: {epoch_loss:.4f}")
        if epoch > swa_start:
            swa_model.update_parameters(model)
            swa_scheduler.step()
        else:
            scheduler.step()
        if epoch % val_int == 0:
            model.eval()
            with torch.no_grad():
                metric_sum = 0.0
                metric_count = 0
                metric_sum_swa = 0.0
                metric_count_swa = 0
                for i, val_data in enumerate(val_loader):
                    val_images, val_labels = val_data["img"].to(device, dtype=torch.float), val_data["seg"].to(device,
                                                                                                               dtype=torch.float)
                    sw_batch_size = 1
                    val_labels = (val_labels > 0.5)
                    #roi_size = val_labels.size()[-2:]
                    roi_size = (512, 512)
                    val_outputs = sliding_window_inference(val_images, roi_size, sw_batch_size, model)
                    val_outputs = postprocessing_list(val_outputs)
                    value = metric(y_pred=val_outputs, y=val_labels)
                    if math.isnan(value):
                        continue
                    metric_count += len(value)
                    metric_sum += value.item() * len(value)
                    metric_val = metric_sum / metric_count
                    val_outputs_swa = sliding_window_inference(val_images, roi_size, sw_batch_size, swa_model)
                    val_outputs_swa = postprocessing_list(val_outputs_swa)
                    value_swa = metric(y_pred=val_outputs_swa, y=val_labels)
                    metric_count_swa += len(value_swa)
                    metric_sum_swa += value_swa.item() * len(value_swa)
                    metric_val_swa = metric_sum_swa / metric_count_swa
                print("metric model: {:.4f}".format(metric_val))
                print("metric swa model: {:.4f}".format(metric_val_swa))
                if metric_val > best_metric_model or metric_val_swa > best_metric_swa:
                    best_metric_model = metric_val
                    best_model = model
                if metric_val_swa > best_metric_swa:
                    best_metric_swa = metric_val_swa
                    best_model_swa = swa_model
    del train_ds
    del train_loader
    del val_ds
    del val_loader
    return best_model, best_model_swa, loss, opt


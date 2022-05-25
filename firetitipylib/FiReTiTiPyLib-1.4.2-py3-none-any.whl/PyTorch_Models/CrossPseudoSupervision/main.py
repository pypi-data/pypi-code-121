import json, sys, argparse, torch, math, statistics, os, gc, numpy as np
from pathlib import Path

from PIL.Image import Image
from torch import optim
from torch.utils.data import DataLoader
import torchvision.transforms.functional as TF
import torch.nn.functional as F

from FiReTiTiPyLib.PyTorch_Models.CrossPseudoSupervision import losses, metrics
from FiReTiTiPyLib.PyTorch_Models.CrossPseudoSupervision.mask_gen import BoxMaskGenerator
from FiReTiTiPyLib.PyTorch_Models.CrossPseudoSupervision.utils import lamdba_scaling, poly_lr_linear_warmup, detach_to_numpy
from smallunet import SmallUNet
from utils import Dotdict
from FiReTiTiPyLib.FiReTiTiPyTorchLib.Segmentation_Datasets import UnsupervisedSegmentationDataset


def main():
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description='EM Segmentation')
        # Required
        parser.add_argument('--train_image_dir', required=True, type=str, default=None, help='directory containing the training images (labeled and unlabeled)')
        parser.add_argument('--train_mask_dir', required=True, type=str, default=None, help='directory containing the training masks')
        parser.add_argument('--out_dir', required=True, type=str, default=None, help='directory to place the segmentation outputs in')
        parser.add_argument('--dim_crop', type=str, default=2048)
        parser.add_argument('--start_channels', type=int, default=8)
        parser.add_argument('--net_input_size', type=int, default=512)
        parser.add_argument('--batch_size', type=int, default=20)
        parser.add_argument('--num_crops_per_image', type=int, default=64)
        parser.add_argument('--num_of_epochs', type=int, default=500)
        parser.add_argument('--base_learning_rate', type=float, default=0.001)
        parser.add_argument('--normalize', action="store_true")
        parser.add_argument('--no_normalize', dest="normalize", action="store_false")
        parser.set_defaults(normalize=True)
        parser.add_argument('--downsize', action="store_true")
        parser.add_argument('--no_downsize', dest="downsize", action="store_false")
        parser.set_defaults(downsize=True)
        parser.add_argument('--cps_weight', type=float, default=1.0)
        parser.add_argument('--keep_empty_output_prob', type=float, default=0.001)

        cfg_params = parser.parse_args().__dict__
    else:
        with open("cfg.json") as jsf:
            cfg_params = json.load(jsf)
    cfg_params = Dotdict(cfg_params)
    print(cfg_params)
    print("Starting training", flush=True)
    train_model(cfg_params)


def train_model(params):
    model_dir = os.path.join(params.out_dir, "models")
    Path(model_dir).mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SmallUNet(1, 1, params.start_channels).train().to(device)
    model2 = SmallUNet(1, 1, params.start_channels).train().to(device)
    half_batch_size, diff = (params.batch_size // 2 + 1, 1) if params.batch_size % 2 != 0 else (params.batch_size // 2, 0)
    d_train = UnsupervisedSegmentationDataset(params, params.train_image_dir, params.train_mask_dir, train=True)
    train_loader = DataLoader(d_train, half_batch_size, pin_memory=True, shuffle=True)
    optimizer = optim.Adam(model.parameters(), lr=params.base_learning_rate)
    optimizer2 = optim.Adam(model2.parameters(), lr=params.base_learning_rate)
    base_lr = params.base_learning_rate
    best_dice = 0
    iter = 0
    max_iter = len(train_loader) * params.num_of_epochs
    boxmix_gen = BoxMaskGenerator(prop_range=(0.25, 0.5), random_aspect_ratio=True, prop_by_area=True, within_bounds=True, invert=True)

    for epoch_num in range(params.num_of_epochs):
        to_log = {}
        losses_val, dices_val = [], []
        losses_train, cps1_, cps2_, seg1, seg2, dices_train, dices_train2 = [], [], [], [], [], [], []
        # l_images for labeled images, ul_images for unlabeled images
        for i_batch, (l_images, targets, ul_images) in enumerate(train_loader):
            optimizer.zero_grad()
            optimizer2.zero_grad()
            if diff > 0:
                ul_images = ul_images[-1]

            split_size_l = int(l_images.size(0) / 2) if l_images.size(0) % 2 == 0 else int(l_images.size(0) // 2 + 1)
            split_size_u = int(ul_images.size(0) / 2) if ul_images.size(0) % 2 == 0 else int(ul_images.size(0) // 2 + 1)
            l_1, l_2 = torch.split(l_images, split_size_l, dim=0)
            ul_1, ul_2 = torch.split(ul_images, split_size_u, dim=0)
            if l_1.size(0) != l_2.size(0):
                l_1 = l_1[:-1]
            if ul_1.size(0) != ul_2.size(0):
                ul_1 = ul_1[:-1]
            ul_1, ul_2 = torch.cat((l_1, ul_1), dim=0), torch.cat((l_2, ul_2), dim=0)
            batch_mix_masks = boxmix_gen.generate_params(n_masks=ul_1.size(0), mask_shape=(ul_1.size(2), ul_1.size(3)))
            batch_mix_masks = torch.as_tensor(batch_mix_masks).type(torch.float32).to(device, non_blocking=True)
            l_batch, targets = l_images.to(device, non_blocking=True), targets[0].to(device, non_blocking=True)
            ul_1, ul_2 = ul_1.to(device, non_blocking=True), ul_2.to(device, non_blocking=True)
            unsup_imgs_mixed = ul_1 * (1 - batch_mix_masks) + ul_2 * batch_mix_masks
            with torch.no_grad():
                # Estimate the pseudo-label with branch#1 & supervise branch#2
                logits_u0_tea_1 = model(ul_1)
                logits_u1_tea_1 = model(ul_2)
                logits_u0_tea_1 = logits_u0_tea_1.detach()
                logits_u1_tea_1 = logits_u1_tea_1.detach()
                # Estimate the pseudo-label with branch#2 & supervise branch#1
                logits_u0_tea_2 = model2(ul_1)
                logits_u1_tea_2 = model2(ul_2)
                logits_u0_tea_2 = logits_u0_tea_2.detach()
                logits_u1_tea_2 = logits_u1_tea_2.detach()

            # Mix predictions using same mask
            # It makes no difference whether we do this with logits or probabilities as
            # the mask pixels are either 1 or 0
            logits_cons_tea_1 = logits_u0_tea_1 * (1 - batch_mix_masks) + logits_u1_tea_1 * batch_mix_masks
            ps_label_1 = torch.where(logits_cons_tea_1>0.5,1,0)
            ps_label_1 = ps_label_1.long()
            logits_cons_tea_2 = logits_u0_tea_2 * (1 - batch_mix_masks) + logits_u1_tea_2 * batch_mix_masks
            ps_label_2 = torch.where(logits_cons_tea_2>0.5,1,0)
            ps_label_2 = ps_label_2.long()

            # Get student#1 prediction for mixed image
            logits_cons_stu_1 = model(unsup_imgs_mixed)
            # Get student#2 prediction for mixed image
            logits_cons_stu_2 = model2(unsup_imgs_mixed)
            cps1 = losses.dice_loss(logits_cons_stu_1, ps_label_2)
            cps2 = losses.dice_loss(logits_cons_stu_2, ps_label_1)
            cps_loss = cps1 + cps2
            cps_loss *= lamdba_scaling(epoch_num, params.cps_weight)

            # Supervision loss
            outputs_sup, outputs_sup2 = model(l_batch),  model2(l_batch)
            loss_dice = losses.dice_loss(outputs_sup.squeeze(), targets.squeeze() == 1)
            loss_dice2 = losses.dice_loss(outputs_sup2.squeeze(), targets.squeeze() == 1)
            loss_dice_total = loss_dice + loss_dice2
            loss = cps_loss + loss_dice_total
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            torch.nn.utils.clip_grad_norm_(model2.parameters(), 1.0)

            optimizer.step()
            optimizer2.step()

            cps1_.append(cps1.item())
            cps2_.append(cps2.item())
            losses_train.append(loss.item())
            dices_train.append(loss_dice.item())
            dices_train2.append(loss_dice2.item())

            # update lr
            lr_ = poly_lr_linear_warmup(base_lr, iter, max_iter)
            for param_group in optimizer.param_groups:
                param_group['lr'] = lr_
            for param_group in optimizer2.param_groups:
                param_group['lr'] = lr_
            iter += 1
        model.eval()
        with torch.no_grad():
            for i_batch, (images, targets, _) in enumerate(train_loader):
                l_batch, targets = images.to(device), targets[0].to(device)
                outputs_sup = model(l_batch)
                dc = metrics.dice(torch.where(outputs_sup.squeeze() > 0.5, 1, 0), targets)
                dices_val.append(dc.item())
            dice_val = statistics.mean(dices_val)
            # save model
            if dice_val > best_dice:
                best_dice = dice_val
                to_log["best_dice"] = best_dice
                # save model
                torch.save({
                    "epoch": epoch_num,
                    "state_dict": model.state_dict(),
                }, os.path.join(model_dir, "model_best_dice.pt"))
        model.train()

    # Eval
    dir_out = os.path.join(params.out_dir, "images")
    Path(dir_out).mkdir(parents=True, exist_ok=True)
    gc.collect()
    checkpoint = torch.load(os.path.join(model_dir, "model_best_dice.pt"), map_location=device)
    model = SmallUNet(1, 1, params.start_channels).to(device)
    model.load_state_dict(checkpoint["state_dict"])
    model = model.eval()
    if params.normalize:
        mean, std = d_train.get_norm_values()
    all_images_path = d_train.unsupervised_image_paths
    all_images_path.extend(d_train.image_paths)
    for img_path in all_images_path:
        img = Image.open(img_path)
        img = TF.to_tensor(img).unsqueeze(0)
        if params.normalize:
            img = TF.normalize(img, mean=mean, std=std)

        mask_pred = sliding_window(img, model, params, device)
        out_file_name = os.path.join(dir_out, os.path.basename(img_path))
        log_mask = Image.fromarray(detach_to_numpy(mask_pred.squeeze()).astype(np.uint8) * 255)
        log_mask.save(out_file_name)


def sliding_window(x, model, config, device):
    # dim_crop is kernel size
    if config.downsize:
        kernel_size = config.dim_crop
        stride = config.dim_crop // 4
    else:
        kernel_size = config.net_input_size
        stride = config.net_input_size // 4

    # pad
    pad_h = stride - (x.size(2) - kernel_size) % stride
    pad_w = stride - (x.size(3) - kernel_size) % stride
    x_padded = F.pad(x, (pad_w // 2,
                         pad_w - pad_w // 2,
                         pad_h // 2,
                         pad_h - pad_h // 2),
                     mode="reflect")
    H, W = x_padded.size(2), x_padded.size(3)
    # unfold
    patches = x_padded.unfold(2, kernel_size, stride).unfold(3, kernel_size, stride)
    patches = patches.contiguous().view(patches.size(0), -1, kernel_size, kernel_size)  # [1, nb_patches_all, config.dim_crop, config.dim_crop]
    patches = patches.permute(1, 0, 2, 3).contiguous()  # [nb_patches_all, 1, kernel_size, kernel_size]
    # downsize if done during training
    if config.downsize:
        patches = torch.nn.functional.interpolate(input=patches,
                                                  size=config.net_input_size,
                                                  mode="bilinear")  # [nb_patches_all, 1, dimensions_input, dimensions_input]

    # apply model to every patch
    batch_size = config.batch_size
    if torch.cuda.device_count() > 1:
        batch_size = batch_size * torch.cuda.device_count()
    outs = []
    for i in range(0, patches.size(0), batch_size):
        ins = patches[i:i + batch_size].to(device)
        outs.append(detach_to_numpy(model(ins)))

    segmentation_masks = torch.tensor(np.concatenate(outs, axis=0)).to(device)  # [nb_patches_all, nbclasses, dimensions_input, dimensions_input]

    # Upsample if we downsized
    if config.downsize:
        segmentation_masks = torch.nn.functional.interpolate(input=segmentation_masks, size=kernel_size, mode="bilinear")

    # fold back together
    results = segmentation_masks.permute(1, 0, 2, 3)  # [nclasses, nb_patches_all, kernel_size, kernel_size]
    patches = results.contiguous().view(1, 1, -1, kernel_size * kernel_size)  # [B, C, nb_patches_all, kernel_size*kernel_size]
    patches = patches.permute(0, 1, 3, 2)  # [B, C, kernel_size*kernel_size, nb_patches_all]
    patches = patches.contiguous().view(patches.size(0), 1 * kernel_size * kernel_size,-1)  # [B, C*prod(kernel_size), L] as expected by Fold
    output = F.fold(patches, output_size=(H, W), kernel_size=kernel_size, stride=stride)
    # Fold sums overlapping patches, so we need to divide each pixel by the number of patches it was in
    counter = F.fold(torch.ones_like(patches), output_size=(H, W), kernel_size=kernel_size, stride=stride)
    averaged_output = output / counter

    # Crop back to original size
    final = averaged_output[:, :, pad_h // 2:-(pad_h - pad_h // 2), pad_w // 2:-(pad_w - pad_w // 2)]
    mask = torch.where(final > 0.5, 1, 0)
    return mask


main()

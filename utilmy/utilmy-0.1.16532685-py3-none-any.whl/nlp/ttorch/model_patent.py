"""#


# %% [code] {"execution":{"iopub.status.busy":"2022-04-23T10:46:44.345202Z","iopub.execute_input":"2022-04-23T10:46:44.345798Z","iopub.status.idle":"2022-04-23T10:46:45.889496Z","shell.execute_reply.started":"2022-04-23T10:46:44.34576Z","shell.execute_reply":"2022-04-23T10:46:45.888609Z"}}
!pip uninstall -q -y transformers

https://www.kaggle.com/code/brookm291/uspppm-baseline-training-223109/edit



"""
import sys
sys.path.append("../input/torch-components-library/torch-components-main")
sys.path.append("../input/transformers/src")

import transformers
import torch
from torch import nn, optim
from torch.nn import functional as F
from torch.utils.data import DataLoader
from torch.optim import lr_scheduler
from torch.cuda.amp import GradScaler, autocast
from transformers import AutoModel, AutoTokenizer, AutoConfig
from torch_components import Configuration, Timer, Averager
from torch_components.callbacks import EarlyStopping, ModelCheckpoint
from torch_components.utils import seed_everything, get_lr, get_optimizer, get_scheduler, get_batch
from torch_components.import_utils import wandb_run_exists
from sklearn.model_selection import StratifiedGroupKFold
from tqdm.notebook import tqdm
from IPython.display import display
from datetime import timedelta
import scipy
import pandas as pd
import numpy as np
import warnings
import wandb
import os
import shutil
import gc
from kaggle_secrets import UserSecretsClient



# %% [markdown]
# # Utilities

# %% [code] {"execution":{"iopub.status.busy":"2022-04-23T10:46:45.924141Z","iopub.execute_input":"2022-04-23T10:46:45.924663Z","iopub.status.idle":"2022-04-23T10:46:45.934368Z","shell.execute_reply.started":"2022-04-23T10:46:45.924625Z","shell.execute_reply":"2022-04-23T10:46:45.93371Z"}}
def make_directory(directory, overwriting=False):
    if not os.path.exists(directory):
        os.mkdir(directory)
    else:
        if overwriting:
            shutil.rmtree(directory)
            os.mkdir(directory)

            
def create_folds(data_frame, targets, groups, folds=5, seed=42, shuffle=True, fold_column="fold"):
    cv_strategy = StratifiedGroupKFold(n_splits=folds, random_state=seed, shuffle=shuffle)
    folds = cv_strategy.split(X=data_frame, y=targets, groups=groups)
    for fold, (train_indexes, validation_indexes) in enumerate(folds):
        data_frame.loc[validation_indexes, fold_column] =  int(fold+1)
        
    data_frame[fold_column] = data_frame[fold_column].astype(int)
    
    return data_frame

# %% [code] {"execution":{"iopub.status.busy":"2022-04-23T10:46:45.936147Z","iopub.execute_input":"2022-04-23T10:46:45.936682Z","iopub.status.idle":"2022-04-23T10:46:45.987774Z","shell.execute_reply.started":"2022-04-23T10:46:45.936635Z","shell.execute_reply":"2022-04-23T10:46:45.987047Z"}}
def training_loop(train_loader, 
                  model,
                  optimizer,
                  scheduler=None,
                  scheduling_after="step",
                  epochs=1,
                  validation_loader=None, 
                  gradient_accumulation_steps=1, 
                  gradient_scaling=False,
                  gradient_norm=1,
                  validation_steps=100, 
                  amp=False,
                  recalculate_metrics_at_end=True, 
                  return_validation_outputs=True,
                  debug=True, 
                  verbose=1, 
                  device="cpu", 
                  time_format="{hours}:{minutes}:{seconds}", 
                  logger="print"):
    
    training_steps = len(train_loader) * epochs
    
    if isinstance(validation_steps, float):
        validation_steps = int(training_steps * validation_steps)
    elif validation_steps == "epoch":
        validation_steps = len(train_loader)
    
    scaler = GradScaler() if gradient_scaling else None
    
    
    if wandb_run_exists():
        wandb.define_metric("train/loss vs epoch", step_metric="epoch")
    
    if debug:
        print(f"Auto Mixed Precision: {amp}")
        print(f"Gradient norm: {gradient_norm}")
        print(f"Gradient scaling: {gradient_scaling}")
        print(f"Gradient accumulation steps: {gradient_accumulation_steps}")
        print(f"Validation steps: {validation_steps}")
        print(f"Device: {device}")
        print()
        
    
    if wandb_run_exists():
        print(f"Weights & Biases Run: {wandb.run.get_url()}", end="\n"*2)
        
    passed_steps = 1
    train_loss, train_metrics = Averager(), Averager()
    best_validation_loss, best_validation_metrics, best_validation_outputs = None, None, None
    
    if device is not None:
        model.to(device)
    
    model.zero_grad()
    total_time = timedelta(seconds=0)
    for epoch in range(1, epochs+1):
        if logger == "tqdm":
            train_loader = tqdm(iterable=train_loader, 
                                total=len(train_loader),
                                colour="#000",
                                bar_format="{l_bar} {bar} {n_fmt}/{total_fmt} - remain: {remaining}{postfix}")
            
            train_loader.set_description_str(f"Epoch {epoch}/{epochs}")
        else:
            print(f"\nEpoch {epoch}/{epochs}", end="\n"*2)
            

        timer = Timer(time_format)
        epoch_train_loss, epoch_train_metrics = Averager(), Averager()
        steps = len(train_loader)
        for step, batch in enumerate(train_loader, 1):
            batch_size = len(batch)
            batch_loss, batch_metrics = training_step(batch=batch, 
                                                      model=model, 
                                                      optimizer=optimizer,
                                                      gradient_norm=gradient_norm,
                                                      gradient_accumulation_steps=gradient_accumulation_steps, 
                                                      amp=amp, 
                                                      scaler=scaler, 
                                                      device=device)
            
            train_loss.update(batch_loss, n=batch_size)
            train_metrics.update(batch_metrics, n=batch_size)
            epoch_train_loss.update(batch_loss, n=batch_size)
            epoch_train_metrics.update(batch_metrics, n=batch_size)
            
            if (passed_steps % gradient_accumulation_steps) == 0:
                optimization_step(model=model, optimizer=optimizer, scaler=scaler)
                

            lr = get_lr(optimizer, only_last=True)
            if scheduling_after == "step":
                scheduling_step(scheduler)
            
                
            logs = {"train/loss": train_loss.average, 
                    "train/loss vs batch": batch_loss, "lr": lr}
            
            for metric in batch_metrics:
                metric = metric.strip().lower()
                logs.update({f"train/{metric}": train_metrics.average[metric], 
                             f"train/{metric} vs batch": batch_metrics[metric]})
                
            if wandb_run_exists():
                wandb.log(logs, step=passed_steps) 
            
            if logger == "tqdm":
                train_loader.set_postfix_str(f"loss: {epoch_train_loss.average:.4}"
                                             f"{format_metrics(epoch_train_metrics.average)}")
            else:
                 if step % verbose == 0 or step == steps:
                    elapsed, remain = timer(step/steps)
                    print(f"{step}/{steps} - "
                          f"remain: {remain} - "
                          f"loss: {epoch_train_loss.average:.4}"
                          f"{format_metrics(epoch_train_metrics.average)}")
                    
            
            if validation_loader is not None:
                if (passed_steps % validation_steps) == 0:
                    print()
                    validation_loss, validation_metrics, validation_outputs = validation_loop(loader=validation_loader, 
                                                                                              model=model, 
                                                                                              gradient_accumulation_steps=gradient_accumulation_steps,
                                                                                              amp=amp, 
                                                                                              return_outputs=True, 
                                                                                              verbose=verbose, 
                                                                                              recalculate_metrics_at_end=True, 
                                                                                              device=device, 
                                                                                              logger=logger)
                    
                    
                    
                    logs = {"validation/loss": validation_loss, 
                            "train/loss vs validation steps": train_loss.average}
    
                    for metric, value in validation_metrics.items():
                        metric = metric.strip().lower()
                        logs.update({f"validation/{metric}": value, 
                                     f"train/{metric} vs validation steps": train_metrics.average[metric]})
                    
                    if wandb_run_exists():
                        wandb.log(logs, step=passed_steps)
                    
                    is_checkpoint_saved = model_checkpointing(loss=validation_loss, 
                                                              metrics=validation_metrics,
                                                              model=model, 
                                                              optimizer=optimizer, 
                                                              scheduler=scheduler, 
                                                              step=passed_steps, 
                                                              previous_loss=best_validation_loss, 
                                                              previous_metrics=validation_metrics)
                    
                    if is_checkpoint_saved:
                        best_validation_loss = validation_loss
                        best_validation_metrics = validation_metrics
                        best_validation_outputs = validation_outputs
                    
                    scheduling_step(scheduler, loss=validation_loss)
                    
                    print()
            
            passed_steps += 1
        
        if scheduling_after == "epoch":
            scheduling_step(scheduler)
        
            
        if logger == "tqdm":
            elapsed, remain = timer(1/1)

        epoch_elapsed_seconds = timer.elapsed_time.total_seconds()
        total_time += timedelta(seconds=epoch_elapsed_seconds)
        
        
        logs = {"train/loss vs epoch": epoch_train_loss.average, 
                "epoch": epoch}
        
        for metric, value in train_metrics.average.items():
            metric = metric.strip().lower()
            logs.update({f"train/{metric} vs epoch": value})
            
            if wandb_run_exists():
                wandb.define_metric(f"train/{metric} vs epoch", step_metric="epoch")
        
        if wandb_run_exists():
            wandb.log(logs, step=passed_steps)
            
        if logger == "tqdm":
            train_loader.close()

    
    if debug:
        print(f"\nResults", end="\n"*2)

        print(f"Training loss: {train_loss.average}{format_metrics(train_metrics.average)}")
        print(f"Validation loss: {best_validation_loss}{format_metrics(best_validation_metrics)}")
        print(f"Total time: {Timer.format_time(total_time, time_format=time_format)}")
    
    if validation_loader is not None:
        if return_validation_outputs:
            return (train_loss.average, train_metrics.average), (best_validation_loss, best_validation_metrics, best_validation_outputs)

        return (train_loss.average, train_metrics.average), (best_validation_loss, best_validation_metrics)

    return (train_loss.average, train_metrics.average)
    

    
def validation_loop(loader, 
                    model, 
                    gradient_accumulation_steps=1,
                    amp=False, 
                    return_outputs=True, 
                    recalculate_metrics_at_end=True, 
                    verbose=1, 
                    device="cpu", 
                    time_format="{hours}:{minutes}:{seconds}",
                    logger="print"):
    
    model.eval()
    loss, metrics = Averager(), Averager()
    timer = Timer(time_format)
    outputs, targets = [], []
    steps = len(loader)
    
    if logger == "tqdm":
        loader = tqdm(iterable=loader, 
                      total=len(loader),
                      colour="#000",
                      bar_format="{l_bar} {bar} {n_fmt}/{total_fmt} - remain: {remaining}{postfix}")
            
        loader.set_description_str("[Validation]")
    
    for step, batch in enumerate(loader, 1):
        with torch.no_grad():
            with autocast(enabled=amp):
                batch_loss, batch_outputs = calculate_loss(batch=batch, model=model, return_outputs=True, device=device)
                
                if gradient_accumulation_steps > 1:
                    batch_loss /= gradient_accumulation_steps
                
                loss.update(batch_loss.item(), n=len(batch))
                
                batch_targets = get_targets(batch)
                batch_metrics = calculate_metrics(predictions=batch_outputs, targets=batch_targets, device=device)
                metrics.update(batch_metrics, n=len(batch))
                
                if isinstance(batch_targets, dict):
                    targets.append(batch_targets)
                else:
                    targets.extend(batch_targets.to("cpu").tolist())
                
                outputs.extend(batch_outputs.to("cpu").tolist())
                
                
                if step == steps and recalculate_metrics_at_end:
                    outputs = torch.tensor(outputs)
                    targets = torch.tensor(targets)
                        
                    metrics = Averager(calculate_metrics(predictions=outputs, targets=targets))
                
                if logger == "tqdm":
                    loader.set_postfix_str(f"loss: {loss.average:.4}"
                                           f"{format_metrics(metrics.average)}")
                else:
                    if step % verbose == 0 or step == steps:
                        elapsed, remain = timer(step/steps)

                        print(f"[Validation] "
                              f"{step}/{steps} - "
                              f"remain: {remain} - "
                              f"loss: {loss.average:.4}"
                              f"{format_metrics(metrics.average)}")
                    
    if not recalculate_metrics_at_end: 
        outputs = torch.tensor(outputs)
        
    if logger == "tqdm":
        loader.close()
        
    return (loss.average, metrics.average, outputs) if return_outputs else (loss.average, metrics.average)


def format_metrics(metrics, sep=" - ", add_sep_to_start=True):
    if metrics != {}:
        string = sep.join([f"{k.strip().lower()}: {v:.4}" for k, v in metrics.items()])
        return sep + string if add_sep_to_start else string 
    else:
        return ""

    
def training_step(batch, 
                  model, 
                  optimizer, 
                  gradient_norm=1.0, 
                  amp=False, 
                  gradient_accumulation_steps=1, 
                  scaler=None, 
                  device="cpu"):
    
    model.train()
    with autocast(enabled=amp):
        loss, outputs = calculate_loss(batch=batch, model=model, return_outputs=True, device=device)
        targets = get_targets(batch)
        metrics = calculate_metrics(predictions=outputs, targets=targets, device=device)
        
        if gradient_accumulation_steps > 1:
            loss /= gradient_accumulation_steps
        
        if scaler is not None:
            scaler.scale(loss).backward()
        else:
            loss.backward()
            
    if gradient_norm > 0:
        if scaler is not None:
            scaler.unscale_(optimizer)
                            
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=gradient_norm)
        
    return loss.detach(), metrics


def optimization_step(model, optimizer, scaler=None):                        
    if scaler is not None:
        scaler.step(optimizer)
        scaler.update()
    else:
        optimizer.step()
        
    model.zero_grad()
        

def scheduling_step(scheduler=None, loss=None):
    if scheduler is not None:
        if isinstance(scheduler, lr_scheduler.ReduceLROnPlateau):
            scheduler.step(loss)
        else:
            scheduler.step()

# %% [code] {"execution":{"iopub.status.busy":"2022-04-23T10:46:45.991015Z","iopub.execute_input":"2022-04-23T10:46:45.991214Z","iopub.status.idle":"2022-04-23T10:46:46.003716Z","shell.execute_reply.started":"2022-04-23T10:46:45.99119Z","shell.execute_reply":"2022-04-23T10:46:46.002913Z"}}
def calculate_loss(batch, model, return_outputs=True, device="cpu"):
    input_ids, attention_mask, targets = batch
    
    input_ids = input_ids.to(device).long()
    attention_mask = attention_mask.to(device).long()
    targets = targets.to(device).float()
    
    outputs = model(input_ids, attention_mask)
    outputs = outputs.sigmoid().squeeze(dim=-1)
    loss = F.mse_loss(outputs, targets, reduction="mean")
        
    return (loss, outputs) if return_outputs else loss


def calculate_metrics(predictions, targets, device="cpu"):
    predictions = predictions.sigmoid().detach().view(-1).to("cpu").float().numpy()
    targets = targets.view(-1).to("cpu").float().numpy()
    
    return dict(pearson=scipy.stats.pearsonr(predictions, targets)[0])


def get_targets(batch):
    *_, targets = batch
    return targets


def model_checkpointing(loss, metrics, model, optimizer=None, scheduler=None, step=None, previous_loss=None, previous_metrics=None):
    is_saved_checkpoint = model_checkpoint(value=loss, 
                                           model=model, 
                                           optimizer=optimizer, 
                                           scheduler=scheduler, 
                                           step=step)
    return is_saved_checkpoint

# %% [markdown]
# # Dataset

# %% [code] {"execution":{"iopub.status.busy":"2022-04-23T10:46:46.006196Z","iopub.execute_input":"2022-04-23T10:46:46.006907Z","iopub.status.idle":"2022-04-23T10:46:46.018619Z","shell.execute_reply.started":"2022-04-23T10:46:46.006794Z","shell.execute_reply":"2022-04-23T10:46:46.017875Z"}}
class DynamicPadding:
    def __init__(self, tokenizer, max_length=None, padding=True, pad_to_multiple_of=None, return_tensors="pt"):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.padding = padding
        self.pad_to_multiple_of = pad_to_multiple_of
        self.return_tensors = return_tensors
    
    def __call__(self, tokenized):
        max_length = max(len(_["input_ids"]) for _ in tokenized)
        max_length = min(max_length, self.max_length) if self.max_length is not None else max_length
                
        padded = self.tokenizer.pad(encoded_inputs=tokenized,
                                    max_length=max_length,
                                    padding=self.padding, 
                                    pad_to_multiple_of=self.pad_to_multiple_of, 
                                    return_tensors=self.return_tensors)
        
        return padded
    
    
    
class Collator:
    def __init__(self, return_targets=True, **kwargs):
        self.dynamic_padding = DynamicPadding(**kwargs)
        self.return_targets = return_targets
    
    def __call__(self, batch):
        all_tokenized, all_targets = [], []
        for sample in batch:
            if self.return_targets:
                tokenized, target = sample
                all_targets.append(target)
            else:
                tokenized = sample
                
            all_tokenized.append(tokenized)
        
        tokenized = self.dynamic_padding(all_tokenized)
        
        input_ids = torch.tensor(tokenized.input_ids)
        attention_mask = torch.tensor(tokenized.attention_mask)
        
        if self.return_targets:
            all_targets = torch.tensor(all_targets)
        
            return input_ids, attention_mask, all_targets
        
        return input_ids, attention_mask

# %% [code] {"execution":{"iopub.status.busy":"2022-04-23T10:46:46.019794Z","iopub.execute_input":"2022-04-23T10:46:46.020109Z","iopub.status.idle":"2022-04-23T10:46:46.031358Z","shell.execute_reply.started":"2022-04-23T10:46:46.020074Z","shell.execute_reply":"2022-04-23T10:46:46.030611Z"}}
class Dataset:
    def __init__(self, texts, pair_texts, tokenizer, contexts=None, sep=None, targets=None, max_length=128):
        self.texts = texts
        self.pair_texts = pair_texts
        self.contexts = contexts
        self.targets = targets
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.sep = sep if sep is not None else self.tokenizer.sep_token
        
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, index):
        text = self.texts[index].lower()
        pair_text = self.pair_texts[index].lower()
        
        if self.contexts is not None:
            context = self.contexts[index].lower()
            text = text + self.sep + context
        
        tokenized = self.tokenizer(text=text, 
                                   text_pair=pair_text, 
                                   add_special_tokens=True,
                                   #max_length=self.max_length,
                                   #padding="max_length",
                                   truncation=True,
                                   return_attention_mask=True,
                                   return_token_type_ids=False,
                                   return_offsets_mapping=False)
        
        
        if self.targets is not None:
            target = self.targets[index]
            
            return tokenized, target
            
        return tokenized

# %% [markdown]
# # Model

# %% [code] {"execution":{"iopub.status.busy":"2022-04-23T10:46:46.032705Z","iopub.execute_input":"2022-04-23T10:46:46.033398Z","iopub.status.idle":"2022-04-23T10:46:46.048295Z","shell.execute_reply.started":"2022-04-23T10:46:46.033361Z","shell.execute_reply":"2022-04-23T10:46:46.047631Z"}}
class Model(nn.Module):
    def __init__(self, model_path="microsoft/deberta-base", config_path=None, config_updates={}, reinitialization_layers=0):
        super(Model, self).__init__()
        if config_path is None:
            self.config = AutoConfig.from_pretrained(model_path)
        else:
            self.config = AutoConfig.from_pretrained(config_path)
        
        self.config.output_hidden_states = True
        self.config.update(config_updates)
        
        if config_path is None:
            self.model = AutoModel.from_pretrained(model_path, config=self.config)
        else:
            self.model = AutoModel.from_config(self.config)
                
                
        #self.reinit_layers(n=reinitialization_layers, layers=self.model.encoder.layer, std=self.config.initializer_range)

        self.head = nn.Linear(in_features=self.config.hidden_size, out_features=1)
        self.init_weights(self.head, std=self.config.initializer_range)
    
    
    def reinit_layers(self, layers, n=0, std=0.02):
        if n > 0:
            for layer in layers[-n:]:
                for name, module in layer.named_modules():
                    self.init_weights(module, std=std)
            
            print(f"Reinitializated last {n} layers.")
                
    
    def init_weights(self, module, std=0.02):
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None:
                 module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
    
    
    def forward(self, input_ids, attention_mask=None):
        transformer_outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
        features = transformer_outputs.hidden_states[-1]
        features = features[:, 0, :]
        outputs = self.head(features)
        return outputs




def test_run():
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    WANDB = True
    DEBUG = False

    os.environ["TOKENIZERS_PARALLELISM"] = "true"
    os.environ["EXPERIMENT_NAME"] = "none"
    os.environ["WANDB_PROJECT"] = "uspppm"
    os.environ["WANDB_ENTITY"] = "uspppm"
    os.environ["WANDB_SILENT"] = "true"
        
    user_secrets = UserSecretsClient()

    if WANDB:
        wandb_secret_name = "wandb_api_key"
        wandb_key = user_secrets.get_secret(wandb_secret_name)
        wandb.login(key=wandb_key)
        
    warnings.simplefilter("ignore")

    # %% [markdown]
    # # Configuration

    # %% [code] {"execution":{"iopub.status.busy":"2022-04-23T10:46:45.905382Z","iopub.execute_input":"2022-04-23T10:46:45.905931Z","iopub.status.idle":"2022-04-23T10:46:45.921769Z","shell.execute_reply.started":"2022-04-23T10:46:45.905895Z","shell.execute_reply":"2022-04-23T10:46:45.920828Z"}}
    pathes = Configuration(train="../input/us-patent-phrase-to-phrase-matching/train.csv", 
                          test="../input/us-patent-phrase-to-phrase-matching/test.csv",
                          sample_submission="../input/us-patent-phrase-to-phrase-matching/sample_submission.csv",
                          cpc_codes="../input/cpc-codes/titles.csv")

    config = Configuration(model=dict(model_path="distilbert-base-uncased", reinitialization_layers=0), 
                          optimizer=dict(name="AdamW", 
                                          parameters=dict(lr=2e-5, weight_decay=0.0)),
                          
                          scheduler=dict(name="get_cosine_with_hard_restarts_schedule_with_warmup", 
                                          parameters=dict(num_cycles=2, last_epoch=-1)),
                          warmup=0.1,
                          scheduling_after="step",
                          seed=42,
                          max_length=75,
                          batch_size=32,
                          epochs=2,
                          num_workers=4,
                          pin_memory=True,
                          folds=5, 
                          validation_steps=500, 
                          gradient_accumulation_steps=1,
                          gradient_norm=1.0,
                          gradient_scaling=True,
                          delta=1e-4,
                          verbose=250,
                          save_model=True,
                          device=DEVICE,
                          output_directory="./",
                          cv_monitor_value="pearson",
                          amp=True, 
                          debug=True)

    seed_everything(config.seed)


    # %% [code] {"execution":{"iopub.status.busy":"2022-04-23T10:46:46.05111Z","iopub.execute_input":"2022-04-23T10:46:46.051409Z","iopub.status.idle":"2022-04-23T10:46:46.698977Z","shell.execute_reply.started":"2022-04-23T10:46:46.051372Z","shell.execute_reply":"2022-04-23T10:46:46.698196Z"}}
    cpc_codes = pd.read_csv(pathes.cpc_codes)
    train = pd.read_csv(pathes.train)
    train = train.merge(cpc_codes, left_on="context", right_on="code")

    if DEBUG:
        display(train)

    # %% [markdown]
    # # Cross-Validation split

    # %% [code] {"execution":{"iopub.status.busy":"2022-04-23T10:46:46.700406Z","iopub.execute_input":"2022-04-23T10:46:46.700663Z","iopub.status.idle":"2022-04-23T10:46:47.136207Z","shell.execute_reply.started":"2022-04-23T10:46:46.700628Z","shell.execute_reply":"2022-04-23T10:46:47.1354Z"}}
    train["score_bin"] = pd.cut(train["score"], bins=5, labels=False)

    train = create_folds(data_frame=train, 
                        targets=train["score_bin"].values,
                        groups=train["anchor"].values,
                        folds=config.folds, 
                        seed=config.seed, 
                        shuffle=True)

    if config.debug:
        folds_samples_count = train.groupby('fold').size()
        display(folds_samples_count)

    # %% [markdown]
    # # Tokenizer

    # %% [code] {"execution":{"iopub.status.busy":"2022-04-23T10:46:47.137674Z","iopub.execute_input":"2022-04-23T10:46:47.137932Z","iopub.status.idle":"2022-04-23T10:46:50.345253Z","shell.execute_reply.started":"2022-04-23T10:46:47.137898Z","shell.execute_reply":"2022-04-23T10:46:50.344487Z"}}
    tokenizer = AutoTokenizer.from_pretrained(config.model.model_path)
    tokenizer_path = os.path.join(config.output_directory, "tokenizer/")
    tokenizer_files = tokenizer.save_pretrained(tokenizer_path)

    # %% [markdown]
    # # Cross-Validation

    # %% [code] {"execution":{"iopub.status.busy":"2022-04-23T10:46:50.34689Z","iopub.execute_input":"2022-04-23T10:46:50.347139Z","iopub.status.idle":"2022-04-23T10:50:09.101579Z","shell.execute_reply.started":"2022-04-23T10:46:50.347106Z","shell.execute_reply":"2022-04-23T10:50:09.100535Z"}}
    if WANDB:
        experiment_name = os.environ.get("EXPERIMENT_NAME")
        group = experiment_name if experiment_name != "none" else wandb.util.generate_id()

    cv_scores = []
    oof_data_frame = pd.DataFrame()
    for fold in range(1, config.folds + 1):
        print(f"Fold {fold}/{config.folds}", end="\n"*2)
        fold_directory = os.path.join(config.output_directory, f"fold_{fold}")    
        make_directory(fold_directory)
        model_path = os.path.join(fold_directory, "model.pth")
        model_config_path = os.path.join(fold_directory, "model_config.json")
        checkpoints_directory = os.path.join(fold_directory, "checkpoints/")
        make_directory(checkpoints_directory)
        
        collator = Collator(tokenizer=tokenizer, max_length=config.max_length)
        
        train_fold = train[~train["fold"].isin([fold])]
        train_dataset = Dataset(texts=train_fold["anchor"].values, 
                                pair_texts=train_fold["target"].values,
                                contexts=train_fold["title"].values,
                                targets=train_fold["score"].values, 
                                max_length=config.max_length,
                                sep=tokenizer.sep_token,
                                tokenizer=tokenizer)
        
        train_loader = DataLoader(dataset=train_dataset, 
                                  batch_size=config.batch_size, 
                                  num_workers=config.num_workers,
                                  pin_memory=config.pin_memory,
                                  collate_fn=collator,
                                  shuffle=True, 
                                  drop_last=False)
        
        print(f"Train samples: {len(train_dataset)}")
        
        validation_fold = train[train["fold"].isin([fold])]
        validation_dataset = Dataset(texts=validation_fold["anchor"].values, 
                                    pair_texts=validation_fold["target"].values,
                                    contexts=validation_fold["title"].values,
                                    targets=validation_fold["score"].values,
                                    max_length=config.max_length,
                                    sep=tokenizer.sep_token,
                                    tokenizer=tokenizer)
        
        validation_loader = DataLoader(dataset=validation_dataset, 
                                      batch_size=config.batch_size*2, 
                                      num_workers=config.num_workers,
                                      pin_memory=config.pin_memory,
                                      collate_fn=collator,
                                      shuffle=True, 
                                      drop_last=False)
        
        print(f"Validation samples: {len(validation_dataset)}")
        
        model = Model(**config.model)
        
        if not os.path.exists(model_config_path): 
            model.config.to_json_file(model_config_path)
        
        model_parameters = model.parameters()
        optimizer = get_optimizer(**config.optimizer, model_parameters=model_parameters)
        
        training_steps = len(train_loader) * config.epochs
        
        if "scheduler" in config:
            config.scheduler.parameters.num_training_steps = training_steps
            config.scheduler.parameters.num_warmup_steps = training_steps * config.get("warmup", 0)
            scheduler = get_scheduler(**config.scheduler, optimizer=optimizer, from_transformers=True)
        else:
            scheduler = None
            
        model_checkpoint = ModelCheckpoint(mode="min", 
                                          delta=config.delta, 
                                          directory=checkpoints_directory, 
                                          overwriting=True, 
                                          filename_format="checkpoint.pth", 
                                          num_candidates=1)


        if WANDB:
            wandb.init(group=group, name=f"fold_{fold}", config=config)
        
        (train_loss, train_metrics), (validation_loss, validation_metrics, validation_outputs) = training_loop(model=model, 
                                                                                                              optimizer=optimizer, 
                                                                                                              scheduler=scheduler,
                                                                                                              scheduling_after=config.scheduling_after,
                                                                                                              train_loader=train_loader,
                                                                                                              validation_loader=validation_loader,
                                                                                                              epochs=config.epochs, 
                                                                                                              gradient_accumulation_steps=config.gradient_accumulation_steps, 
                                                                                                              gradient_scaling=config.gradient_scaling, 
                                                                                                              gradient_norm=config.gradient_norm, 
                                                                                                              validation_steps=config.validation_steps, 
                                                                                                              amp=config.amp,
                                                                                                              debug=config.debug, 
                                                                                                              verbose=config.verbose, 
                                                                                                              device=config.device, 
                                                                                                              recalculate_metrics_at_end=True, 
                                                                                                              return_validation_outputs=True, 
                                                                                                              logger="tqdm")
        
        if WANDB:
            wandb.finish()
        
        if config.save_model:
            model_state = model.state_dict()
            torch.save(model_state, model_path)
            print(f"Model's path: {model_path}")
        
        validation_fold["prediction"] = validation_outputs.to("cpu").numpy()
        oof_data_frame = pd.concat([oof_data_frame, validation_fold])
        
        cv_monitor_value = validation_loss if config.cv_monitor_value == "loss" else validation_metrics[config.cv_monitor_value]
        cv_scores.append(cv_monitor_value)
        
        del model, optimizer, validation_outputs, train_fold, validation_fold
        torch.cuda.empty_cache()
        gc.collect()
        
        print(end="\n"*6)
        
    cv_scores = np.array(cv_scores)
    print(f"CV scores: {cv_scores} ")
    print(f"CV mean: {cv_scores.mean()}")
    print(f"CV std: {cv_scores.std()}")

    oof_data_frame.to_pickle("oof.pkl")
    np.save("cv_scores.npy", cv_scores)
    configuration_path = config.to_json("configuration.json")

    # %% [code]

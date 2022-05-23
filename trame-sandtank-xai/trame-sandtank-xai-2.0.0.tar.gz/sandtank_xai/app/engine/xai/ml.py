import os
from argparse import ArgumentParser
import numpy as np

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split

import pytorch_lightning as pl

# Add xaitk-saliency required imports
from smqtk_classifier import ClassifyImage
from xaitk_saliency.impls.gen_image_classifier_blackbox_sal.rise import RISEStack
from xaitk_saliency.impls.gen_image_classifier_blackbox_sal.slidingwindow import (
    SlidingWindowStack,
)

from captum.attr import (
    GradientShap,
    DeepLift,
    DeepLiftShap,
    IntegratedGradients,
    LayerConductance,
    NeuronConductance,
    NoiseTunnel,
    LayerActivation,
    Saliency,
)

from parflow.tools.io import read_pfb as pfb2np

_ref_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "refs")
_perm_file_path = os.path.abspath(os.path.join(_ref_directory, "perm.pfb"))
_init_press_file_path = os.path.abspath(os.path.join(_ref_directory, "Init_press.pfb"))

INPUT_PERM = pfb2np(_perm_file_path)
INPUT_PRESSURE = pfb2np(_init_press_file_path)

AI_MAP = {}

XAI_MAP = {
    "GradientShap": GradientShap,
    "DeepLift": DeepLift,
    "DeepLiftShap": DeepLiftShap,
    "IntegratedGradients": IntegratedGradients,
    "LayerConductance": LayerConductance,
    "NeuronConductance": NeuronConductance,
    "NoiseTunnel": NoiseTunnel,
    "LayerActivation": LayerActivation,
    "Saliency": Saliency,
    "SlidingWindow": SlidingWindowStack,
    "RISE": RISEStack,
}


class ClfModel(ClassifyImage):
    def __init__(self, model, xy):
        self.model = model
        self.xy = xy

    def get_labels(self):
        return ["output"]

    def classify_images(self, image_iter):
        for img in image_iter:
            inp = torch.Tensor(img).permute(2, 0, 1).unsqueeze(0)
            out = self.model(inp)[0, self.xy[1], self.xy[0]].detach().numpy()
            yield dict(zip(self.get_labels(), [out]))

    def get_config(self):
        return {}


class XAI:
    def __init__(self, model):
        self.model = model
        self.xai_baseline = torch.zeros(1, 2, 50, 102)
        self.xayMethods = {}
        self.xai_usage = {
            "GradientShap": self.xai_gradient_shap,
            "DeepLift": self.xai_deep_lift,
            "IntegratedGradients": self.xai_integrated_gradients,
            "SlidingWindow": self.xai_sliding_window,
            "RISE": self.xai_rise,
            "Saliency": self.xai_saliency,
            "conv2d_conductance": self.xai_conv2d,
            "conv2d_activation": self.xai_conv2d_activation,
            "relu_conductance": self.xai_relu,
            "relu_activation": self.xai_relu_activation,
            "maxpool_conductance": self.xai_maxpool,
            "maxpool_activation": self.xai_maxpool_activation,
            "dropout_conductance": self.xai_dropout,
            "dropout_activation": self.xai_dropout_activation,
        }

    def get_xai(self, method, **kwargs):
        if method in self.xayMethods:
            return self.xayMethods[method]

        key = method if method in XAI_MAP else method.split("::")[0]
        if key == "SlidingWindow":
            xai = SlidingWindowStack((10, 10), (4, 4), threads=6)
        elif key == "RISE":
            xai = RISEStack(100, 8, 0.5, seed=0, threads=6, debiased=False)
        else:
            xai = XAI_MAP[key](self.model, **kwargs)

        self.xayMethods[method] = xai
        return xai

    def xai_gradient_shap(self, inputs, xy):
        xai = self.get_xai("GradientShap")
        output = xai.attribute(inputs, self.xai_baseline, target=(xy[1], xy[0])).view(
            2, -1
        )
        return 2, output, [102, 50]

    def xai_deep_lift(self, inputs, xy):
        xai = self.get_xai("DeepLift")
        output = xai.attribute(inputs, self.xai_baseline, target=(xy[1], xy[0])).view(
            2, -1
        )
        return 2, output, [102, 50]

    def xai_integrated_gradients(self, inputs, xy):
        xai = self.get_xai("IntegratedGradients")
        output = xai.attribute(inputs, self.xai_baseline, target=(xy[1], xy[0])).view(
            2, -1
        )
        return 2, output, [102, 50]

    def xai_sliding_window(self, inputs, xy):
        xai = self.get_xai("SlidingWindow")
        output = torch.Tensor(
            xai(inputs[0].permute(1, 2, 0).numpy(), ClfModel(self.model, xy))
        )
        return 1, output, [102, 50]

    def xai_rise(self, inputs, xy):
        xai = self.get_xai("RISE")
        output = torch.Tensor(
            xai(inputs[0].permute(1, 2, 0).numpy(), ClfModel(self.model, xy))
        )
        return 1, output, [102, 50]

    def xai_saliency(self, inputs, xy):
        xai = self.get_xai("Saliency")
        output = xai.attribute(inputs, target=(xy[1], xy[0])).view(2, -1)
        return 2, output, [102, 50]

    def xai_conv2d(self, inputs, xy):
        xai = self.get_xai("LayerConductance::conv2d", layer=self.model.xai_layers[0])
        output = xai.attribute(inputs, target=(xy[1], xy[0])).view(8, -1)
        return 8, output, [102, 50]

    def xai_conv2d_activation(self, inputs, xy):
        xai = self.get_xai("LayerActivation::conv2d", layer=self.model.xai_layers[0])
        output = xai.attribute(inputs).view(8, -1)
        return 8, output, [102, 50]

    def xai_relu(self, inputs, xy):
        xai = self.get_xai("LayerConductance::relu", layer=self.model.xai_layers[1])
        output = xai.attribute(inputs, target=(xy[1], xy[0])).view(8, -1)
        return 8, output, [102, 50]

    def xai_relu_activation(self, inputs, xy):
        xai = self.get_xai("LayerActivation::relu", layer=self.model.xai_layers[1])
        output = xai.attribute(inputs).view(8, -1)
        return 8, output, [102, 50]

    def xai_maxpool(self, inputs, xy):
        xai = self.get_xai("LayerConductance::maxpool", layer=self.model.xai_layers[2])
        output = xai.attribute(inputs, target=(xy[1], xy[0])).view(8, -1)
        return 8, output, [51, 25]

    def xai_maxpool_activation(self, inputs, xy):
        xai = self.get_xai("LayerActivation::maxpool", layer=self.model.xai_layers[2])
        output = xai.attribute(inputs).view(8, -1)
        return 8, output, [51, 25]

    def xai_dropout(self, inputs, xy):
        nb_c, out, size = self.xai_maxpool(inputs, xy)
        mask = torch.randn(8, 25 * 51) > 0.5
        out = out.masked_fill(mask, 0)
        return nb_c, out, size

    def xai_dropout_activation(self, inputs, xy):
        nb_c, out, size = self.xai_maxpool_activation(inputs, xy)
        mask = torch.randn(8, 25 * 51) > 0.5
        out = out.masked_fill(mask, 0)
        return nb_c, out, size

    # def xai_dense(self, input, xy):
    #     self.model.xai_layers[3].weight.shape

    def run_xai(self, method, inputs, xy):
        nb_channels, arrays, size = self.xai_usage[method](inputs, xy)
        result = []

        for channel in range(nb_channels):
            array = arrays[channel]
            result.append(
                {
                    "values": array.flatten().tolist(),
                    "range": [float(torch.min(array)), float(torch.max(array))],
                    "size": size,
                }
            )

        return result

    def get_weights(self, out_channel_idx):
        if out_channel_idx < 0:
            return None

        weights = self.model.xai_layers[0].weight[out_channel_idx]
        bias = self.model.xai_layers[0].bias[out_channel_idx]
        result = []
        for channel in range(2):
            array = weights[channel]
            result.append(
                {
                    "id": out_channel_idx,
                    "values": array.flatten().tolist(),
                    "range": [float(torch.min(array)), float(torch.max(array))],
                    "size": [3, 3],
                    "bias": float(bias),
                }
            )

        return result

    def get_dense_weights(self, i, j):
        idx = i + j * 102
        output = self.model.xai_layers[3].weight[idx].view(8, -1)
        result = []
        for channel in range(8):
            array = output[channel]
            result.append(
                {
                    "values": array.flatten().tolist(),
                    "range": [float(torch.min(array)), float(torch.max(array))],
                    "size": [51, 25],
                }
            )

        return result


class Float32_clamp_scaling_x_bc:
    def __init__(self, src_range=[0, 50], dst_range=[-1, 1], height=50):
        self.height = height
        self.dst_range = dst_range
        in_delta = src_range[1] - src_range[0]
        self.in_min = src_range[0]
        self.in_max = src_range[1]
        self.out_min = dst_range[0]
        self.out_max = dst_range[1]
        out_delta = dst_range[1] - dst_range[0]
        self.out_scale = out_delta / in_delta
        self.bc_left = np.empty(height, dtype=np.float32)
        self.bc_right = np.empty(height, dtype=np.float32)

    def set_left(self, value):
        for i in range(self.height):
            if i < value:
                self.bc_left[i] = self.dst_range[1]
            else:
                self.bc_left[i] = self.dst_range[0]

    def set_right(self, value):
        for i in range(self.height):
            if i < value:
                self.bc_right[i] = self.dst_range[1]
            else:
                self.bc_right[i] = self.dst_range[0]

    def convert(self, array):
        in_shape = array.shape

        # convert 3D => 2D
        if len(in_shape) == 3:
            in_shape = (in_shape[0], in_shape[2])
            array = array.reshape(in_shape)

        out_shape = (in_shape[0], in_shape[1] + 2)
        out = np.empty(out_shape, dtype=np.float32)
        # print(f'in shape {in_shape} => out shape {out_shape} => real {out.shape}')
        for z in range(in_shape[0]):
            for x in range(in_shape[1]):
                value = array[z, x]
                if value < self.in_min:
                    out[z, x + 1] = self.out_min
                elif value > self.in_max:
                    out[z, x + 1] = self.out_max
                else:
                    out[z, x + 1] = (
                        value - self.in_min
                    ) * self.out_scale + self.out_min

        # Add BCs
        for i in range(self.height):
            out[i, 0] = self.bc_left[i]
            out[i, out_shape[1] - 1] = self.bc_right[i]

        return out


def clean_pressure(array):
    shape = array.shape
    for j in range(shape[0]):
        for i in range(1, shape[1] - 1):
            array[j, i] = min(1, max(-1, array[j, i]))
            v = array[j, i]
            if INPUT_PRESSURE[j, 0, i - 1] < -100:
                array[j, i] = -1
            elif v > -0.9 and v < -0.75:
                array[j, i] = -0.75

    return array


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------


def load_ml_model(model_type, model_filepath):
    if model_type in AI_MAP:
        return AI_MAP[model_type](model_filepath)

    print(f"Could not find {model_type} in {AI_MAP.keys()}")


# -----------------------------------------------------------------------------
# RegressionPressure*
# -----------------------------------------------------------------------------


class RegressionPressureModel(pl.LightningModule):
    def __init__(self, grid_shape=(50, 1, 100), learning_rate=1e-3, use_dropout=False):
        super().__init__()
        self.save_hyperparameters()

        self.height = grid_shape[0]
        self.width = grid_shape[2] + 2  # Add left/right BC

        self.use_dropout = use_dropout
        self.criterion = nn.L1Loss()

        c2d_channels_in = 2
        c2d_height_in = self.height
        c2d_width_in = self.width
        c2d_channels_out = 8  # reduce it as I was going out of memory (11GB)
        c2d_kernel = 3
        c2d_stride = 1
        c2d_padding = 1  # validate equation above
        c2d_dilation = 1  # default
        c2d_height_out = (
            c2d_height_in + 2 * c2d_padding - c2d_dilation * (c2d_kernel - 1) - 1
        ) / c2d_stride + 1
        c2d_width_out = (
            c2d_width_in + 2 * c2d_padding - c2d_dilation * (c2d_kernel - 1) - 1
        ) / c2d_stride + 1
        # ---
        c2d = torch.nn.Conv2d(
            in_channels=c2d_channels_in,
            out_channels=c2d_channels_out,
            kernel_size=c2d_kernel,
            stride=c2d_stride,
            padding=c2d_padding,
            dilation=c2d_dilation,
        ).float()
        relu = torch.nn.ReLU()
        # ---
        mp2d_kernel = 2
        mp2d_stride = 2
        mp2d_padding = 0  # default 0
        mp2d_dilation = 1  # default 1
        mp2d_height_out = (
            c2d_height_out + (2 * mp2d_padding) - mp2d_dilation * (mp2d_kernel - 1) - 1
        ) / mp2d_stride + 1
        mp2d_width_out = (
            c2d_width_out + (2 * mp2d_padding) - mp2d_dilation * (mp2d_kernel - 1) - 1
        ) / mp2d_stride + 1
        # ---
        mp2d = torch.nn.MaxPool2d(kernel_size=mp2d_kernel, stride=mp2d_stride)
        # ---
        self.layer = torch.nn.Sequential(c2d, relu, mp2d)
        # ---
        self.drop_out = torch.nn.Dropout()
        # ---
        l1_in = int(c2d_channels_out * mp2d_height_out * mp2d_width_out)
        l1_out = int(round(0.5 * l1_in))
        self.dense = torch.nn.Linear(l1_in, l1_out).float()
        # --
        l2_in = l1_out
        l2_out = int(6 * c2d_height_in * c2d_width_in)  # Keep left/right BC
        self.out = torch.nn.Linear(l2_in, l2_out).float()

        # xai layer exposition
        self.xai_layers = [self.layer[0], self.layer[1], self.layer[2], self.dense]
        self.xai_layers_shapes = [
            (8, 50, 102),
            (8, 50, 102),
            (8, 25, 51),
            (1, 50, 102),
        ]

    def forward(self, x):
        x = self.layer(x)
        x = x.view(x.size(0), -1)
        if self.use_dropout:
            x = self.drop_out(x)
        x = self.dense(x)
        x = x.view((x.size(0), self.height, self.width))
        return x

    def training_step(self, batch, batch_idx):
        x = batch["inputs"]
        y = batch["labels"]
        y_hat = self(x)
        loss = self.criterion(y_hat, y)
        self.log("training_loss", loss, on_step=True)
        return loss

    def validation_step(self, batch, batch_idx):
        x = batch["inputs"]
        y = batch["labels"]
        y_hat = self(x)
        val_loss = self.criterion(y_hat, y)
        self.log("validation_loss", val_loss, on_step=True)
        return val_loss

    def test_step(self, batch, batch_idx):
        x = batch["inputs"]
        y = batch["labels"]
        y_hat = self(x)
        loss = self.criterion(y_hat, y)
        return loss

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.hparams.learning_rate)
        return optimizer

    @staticmethod
    def add_model_specific_args(parent_parser):
        parser = ArgumentParser(parents=[parent_parser], add_help=False)
        parser.add_argument("--learning_rate", type=float, default=0.0001)
        return parser

    def inspect_layers(self):
        results = []
        results.append(
            {
                "name": "Sequential Conv2d",
                "weight": list(self.layer[0].weight.shape),
                "bias": list(self.layer[0].bias.shape),
            }
        )
        results.append(
            {
                "name": "Dense",
                "weight": list(self.dense.weight.shape),
                "bias": list(self.dense.bias.shape),
            }
        )
        return results


class RegressionPressure:
    def __init__(self, file_path):
        self.model = RegressionPressureModel.load_from_checkpoint(
            checkpoint_path=file_path
        )
        self.model.use_dropout = False
        self.model.freeze()
        #
        self.time = 1
        self.left = 25
        self.right = 25
        self.press_transform = Float32_clamp_scaling_x_bc(
            src_range=[-30, 50], dst_range=[-1, 1], height=50
        )
        self.perm_transform = Float32_clamp_scaling_x_bc(
            src_range=[0, 1], dst_range=[-1, 1], height=50
        )
        self.inputs = None
        # XAI
        self.xai = XAI(self.model)

    def set_bc(self, left, right, time=1):
        self.left = left
        self.press_transform.set_left(left)
        self.perm_transform.set_left(left)

        self.right = right
        self.press_transform.set_right(right)
        self.perm_transform.set_right(right)

        self.time = time

    def permeability(self):
        shape = INPUT_PERM.shape
        perm = self.perm_transform.convert(INPUT_PERM)
        # perm = INPUT_PERM

        return {
            "values": perm.flatten().tolist(),
            "range": [float(np.amin(perm)), float(np.amax(perm))],
            "size": [shape[2] + 2, shape[0]],
        }

    def pressure(self):
        shape = INPUT_PERM.shape
        press = self.press_transform.convert(INPUT_PRESSURE)

        return {
            "values": press.flatten().tolist(),
            "range": [float(np.amin(press)), float(np.amax(press))],
            "size": [shape[2] + 2, shape[0]],
        }

    def predict(self):
        shape = INPUT_PERM.shape
        perm = self.perm_transform.convert(INPUT_PERM)
        press = self.press_transform.convert(INPUT_PRESSURE)

        for t in range(self.time):
            self.inputs = torch.tensor(
                np.concatenate((perm, press), axis=None).reshape(
                    (1, 2, shape[0], shape[2] + 2)
                ),
                dtype=torch.float,
            )
            output = clean_pressure(
                self.model(self.inputs).view((shape[0], shape[2] + 2))
            )

            # Override BC
            for j in range(shape[0]):
                output[j, 0] = 1 if j < self.left else -1
                output[j, shape[2] + 2 - 1] = 1 if j < self.right else -1

            press = output

        return {
            "values": output.flatten().tolist(),
            "range": [float(torch.min(output)), float(torch.max(output))],
            "size": [shape[2] + 2, shape[0]],
        }

    def explain(self, method, xy):
        return self.xai.run_xai(method, self.inputs, xy)

    def get_weights(self, idx):
        return self.xai.get_weights(idx)

    def get_dense_weights(self, i=0, j=0):
        return self.xai.get_dense_weights(i, j)


AI_MAP["RegressionPressure"] = RegressionPressure


def remove_b_conditions(result):
    (width, height) = result["size"]
    values = np.array(result["values"]).reshape((height, width))
    for b_condition in [0, -1]:
        values = np.delete(values, b_condition, 1)

    result["values"] = values.flatten().tolist()
    result["size"][0] = result["size"][0] - 2
    return result

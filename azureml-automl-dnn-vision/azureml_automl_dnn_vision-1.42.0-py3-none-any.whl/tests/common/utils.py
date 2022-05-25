import numpy as np
import os
import json
import onnx
import onnxruntime as ort
import torch
import torchvision.transforms as transforms
import mlflow
from pytest import skip

import azureml.automl.core.shared.constants as shared_constants
from azureml.automl.dnn.vision.common.constants import CommonSettings
from azureml.automl.dnn.vision.common.mlflow.mlflow_model_wrapper import MLFlowImagesModelWrapper
from azureml.automl.dnn.vision.common.model_export_utils import _get_scoring_method, _get_mlflow_signature


data_folder = 'classification_data/images'


def _to_numpy(tensor):
    return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()


def check_exported_onnx_model(onnx_model_path, wrapper, input, device, get_torch_outputs_fn,
                              is_norm=False, check_output_parity=True):
    onnx_model = onnx.load(onnx_model_path)
    onnx.checker.check_model(onnx_model)

    ort_session = ort.InferenceSession(onnx_model_path)

    ort_img = input
    torch_img = input
    if is_norm:
        ort_img = input * 255.
        torch_img = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])(input.squeeze(0))
        torch_img = torch_img.unsqueeze(0)

    ort_inputs = {ort_session.get_inputs()[0].name: _to_numpy(ort_img)}
    ort_outs = ort_session.run(None, ort_inputs)
    torch_outs = get_torch_outputs_fn(wrapper, torch_img, device)

    # compare ONNX Runtime and PyTorch results
    if check_output_parity:
        try:
            torch.testing.assert_allclose(_to_numpy(torch_outs), ort_outs[0], rtol=1e-03, atol=1e-05)
        except AssertionError:
            raise


def check_exported_onnx_od_model(onnx_model_path, wrapper, input, device, get_torch_outputs_fn,
                                 number_of_classes, is_norm=False, check_output_parity=True):
    onnx_model = onnx.load(onnx_model_path)
    onnx.checker.check_model(onnx_model)

    ort_session = ort.InferenceSession(onnx_model_path)

    ort_img = input
    torch_img = input
    if is_norm:
        ort_img = input * 255.

    ort_inputs = {ort_session.get_inputs()[0].name: _to_numpy(ort_img)}
    ort_output_indices = {output.name: i for i, output in enumerate(ort_session.get_outputs())}
    score_index = ort_output_indices["scores"]
    label_index = ort_output_indices["labels"]

    ort_outs = ort_session.run(None, ort_inputs)
    torch_outs = get_torch_outputs_fn(wrapper, torch_img, device)

    def filter_top_outputs(outputs, label_index, score_index):
        max_label_outputs = 5
        result = []
        for label in range(number_of_classes):
            label_outputs = [[] for i in range(len(outputs))]
            label_output_index = outputs[label_index] == label
            for i in range(len(outputs)):
                label_outputs[i] = outputs[i][label_output_index]
            top_output_index = np.argsort(label_outputs[score_index], kind="stable")[::-1][:max_label_outputs]
            for i in range(len(outputs)):
                label_outputs[i] = label_outputs[i][top_output_index]
                if i < len(result):
                    result[i] = np.concatenate([result[i], label_outputs[i]])
                else:
                    result.append(label_outputs[i])
        return result

    # compare ONNX Runtime and PyTorch results
    if check_output_parity:
        outputs, _ = torch.jit._flatten(torch_outs)
        outputs = list(map(_to_numpy, outputs))
        # Check only top outputs for each label as the order of outputs in torch and onnx
        # outputs are out of order in cases like retinanet.
        outputs = filter_top_outputs(outputs, label_index, score_index)
        ort_outs = filter_top_outputs(ort_outs, label_index, score_index)
        for i in range(0, len(outputs)):
            try:
                torch.testing.assert_allclose(outputs[i], ort_outs[i], rtol=1e-03, atol=1e-05)
            except AssertionError:
                raise


def mock_prepare_model_export(run, output_dir, task_type="", model_settings={},
                              save_as_mlflow=False, is_yolo=False):

    # Ensures prepare_model_export is called
    os.makedirs(shared_constants.OUTPUT_PATH, exist_ok=True)
    checkpoint = torch.load(os.path.join(output_dir, shared_constants.PT_MODEL_FILENAME),
                            map_location='cpu')
    torch.save(checkpoint, shared_constants.PT_MODEL_PATH)
    mock_mlflow_model_export(output_dir, task_type, model_settings,
                             save_as_mlflow, is_yolo)


def mock_mlflow_model_export(output_dir, task_type, model_settings,
                             save_as_mlflow=False, is_yolo=False):

    # mock for Mlflow model generation
    model_file = os.path.join(output_dir, shared_constants.PT_MODEL_FILENAME)
    settings_file = os.path.join(output_dir, shared_constants.MLFlowLiterals.MODEL_SETTINGS_FILENAME)
    remote_path = os.path.join(output_dir, shared_constants.MLFLOW_OUTPUT_PATH)

    with open(settings_file, 'w') as f:
        json.dump(model_settings, f)

    conda_env = {
        'channels': ['conda-forge', 'pytorch'],
        'dependencies': [
            'python=3.7',
            'numpy==1.18.5',
            'pytorch==1.7.1',
            'torchvision==0.8.2',
            {'pip': ['azureml-automl-dnn-vision']}
        ],
        'name': 'azureml-automl-dnn-vision-env'
    }

    mlflow_model_wrapper = MLFlowImagesModelWrapper(
        model_settings=model_settings,
        task_type=task_type,
        scoring_method=_get_scoring_method(task_type)
    )
    print("Saving mlflow model at {}".format(remote_path))
    mlflow.pyfunc.save_model(path=remote_path,
                             python_model=mlflow_model_wrapper,
                             artifacts={"model": model_file, "settings": settings_file},
                             conda_env=conda_env,
                             signature=_get_mlflow_signature(task_type))


def delete_model_weights():
    model_dir = CommonSettings.TORCH_HUB_CHECKPOINT_DIR
    for f in os.listdir(model_dir):
        os.remove(os.path.join(model_dir, f))

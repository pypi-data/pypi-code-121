from modelify.core.frameworks import Frameworks, is_framework_supported
from onnxmltools import convert
from modelify.utils import  create_folder, serialize, save_onnx_model, save_onnx_model_catboost, save_onnx_model_pytorch, save_config
from modelify.inputs import ModelifyInputs, Image
from modelify.app.model import Model
from modelify.utils.constants import APP_FOLDER
from modelify.version import VERSION
import warnings

class ModelInference:
    def __init__(self, model, framework:Frameworks, inputs: ModelifyInputs, target_opset=9):
        self.model = model
        if not isinstance(inputs, ModelifyInputs):
            raise Exception("Model inference object requires Modeliy Inputs; Tabular or Image")
        if not is_framework_supported(framework):
            raise Exception(f"framework is not valid, expected frameworks {[n.value for n in Frameworks]}")
        self.framework = framework
        self.inputs = inputs
        self.preprocess = None
        self.postprocess = None
        self.target_opset =  target_opset
        self.exported = False

        create_folder() ## create app folder 
        # TODO : delete if folder exist

    def export_model(self):
        warnings.filterwarnings("ignore")
        if not self.exported:
            if self.framework == Frameworks.SKLEARN:
                initial_type = self.inputs.convert_onnx()
                model = convert.convert_sklearn(self.model, initial_types=initial_type, target_opset=self.target_opset)
                save_onnx_model(model)
            elif self.framework == Frameworks.LIGHTGBM:
                initial_type = self.inputs.convert_onnx()
                model = convert.convert_lightgbm(self.model, initial_types=initial_type, target_opset=self.target_opset)
                save_onnx_model(model)
            elif self.framework == Frameworks.H2O:
                initial_type = self.inputs.convert_onnx()
                model = convert.convert_h2o(self.model, initial_types=initial_type, target_opset=self.target_opset)
                save_onnx_model(model)
            elif self.framework == Frameworks.KERAS:
                model = convert.convert_keras(self.model)
                save_onnx_model(model)
            elif self.framework == Frameworks.XGBOOST:
                initial_type = self.inputs.convert_onnx()
                model = convert.convert_xgboost(self.model, initial_types=initial_type, target_opset=self.target_opset)
                save_onnx_model(model)
            elif self.framework == Frameworks.CATBOOST: # built in
                save_onnx_model_catboost(self.model)
            elif self.framework == Frameworks.PYTORCH: # built in
                save_onnx_model_pytorch(self.model, self.inputs)
            else:
                raise Exception("The framework you entered is not supported. Supported frameworks :")
        
        self.exported = True 


        # seriliaze functions
        if self.preprocess is not None:
            serialize(self.preprocess, 'preprocess')
    
        if self.postprocess is not None:
            serialize(self.postprocess, 'postprocess')
    
    def get_model_config(self):
        config_metadata = dict()
        # export configs
        input_list = self.inputs.to_list()
        config_metadata["inputs"] = input_list
        config_metadata['input_type'] =  self.inputs.type
        config_metadata['sdk_version'] = VERSION

        if self.preprocess is not None:
            config_metadata["preprocess"] = True
        else:
            config_metadata["preprocess"] = False
        if self.postprocess is not None:
            config_metadata["postprocess"] = True
        else:
            config_metadata["postprocess"] = False

        return config_metadata

    def get_base_upload_types(self):
        base =  {"MODEL": True, "CONFIG": True, "PREPROCESS": False, "POSTPROCESS": False}
        if self.preprocess is not None:
            base["PREPROCESS"] = True
        if self.postprocess is not None:
            base["POSTPROCESS"] = True
        return base

    def test(self):
        if self.inputs.sample is None:
            raise Exception("You should add sample to Input. use add_sample function")
        self.export_model()
        model = Model(modelify_path=APP_FOLDER, preprocess=self.preprocess, postprocess=self.postprocess)

        if isinstance(self.inputs, Image) and self.preprocess:
            sample_input = self.inputs.get_input_for_model(preprocess=True)
        else:
            sample_input = self.inputs.get_input_for_model()

        output = model.run(sample_input)
        return output


from mlplatform_lib.predefinedai.pre_check_predefinedai import PreCheckPredefinedAI
from mlplatform_lib.predefinedai.predefinedai_template_test import PredefinedAITemplateTest

import pytest


@pytest.mark.usefixtures("get_server_config_path")
def test_pre_check_hyperdata(get_server_config_path):
    server_config_path = get_server_config_path
    pre_check_base = PreCheckPredefinedAI(server_config_path=server_config_path)
    pre_check_base.run()


@pytest.mark.usefixture("get_server_config_path", "get_predefinedai_image_config_path")
def test_predefinedai_template_test(get_server_config_path, get_predefinedai_image_config_path):
    server_config_path = get_server_config_path
    image_config_path = get_predefinedai_image_config_path
    predefinedai_template_test = PredefinedAITemplateTest(
        server_config_path=server_config_path, image_config_path=image_config_path
    )
    predefinedai_template_test.run()

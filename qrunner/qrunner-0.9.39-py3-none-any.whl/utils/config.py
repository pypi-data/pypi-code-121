import os
import json
import yaml


local_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.dirname(local_path)


class Config:
    def __init__(self):
        self.file_path = os.path.join(root_path, 'running', 'conf.yml')
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.yaml_data = yaml.load(f.read(), Loader=yaml.FullLoader)

    def get_all(self):
        return self.yaml_data

    def get_item(self, module, key):
        return self.yaml_data[module][key]

    def set_item(self, module, key, value):
        self.yaml_data[module][key] = value
        with open(self.file_path, 'w', encoding="utf-8") as f:
            yaml.dump(self.yaml_data, f)


conf = Config()


if __name__ == '__main__':
    conf.get_all()
    conf.set_item('common', 'platform', 'android')
    conf.set_item('common', 'platform', 'ios')
    print(conf.get_item('app', 'android_alert'))
    print(conf.get_item('common', 'platform'))




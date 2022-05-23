import yaml

with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

import yaml
import argparse

parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
            '--config_file', type=str,
            help="config_file")
parser.add_argument(
            '--misprediction', type=str,
            help="misprediction")
parsed = parser.parse_args()


def set_state(config_file, misprediction):
    with open(config_file) as f:
        doc = yaml.load(f)

    doc['loaders']['val_method']['type'] = "slding_window"
    doc['loaders']['val_method']['saliency'] = "True"
    doc['loaders']['val_method']['misprediction'] = misprediction

    with open(config_file, 'w') as f:
        yaml.dump(doc, f)


if __name__ == '__main__':
    parsed = parser.parse_args()
    config_file = parsed.config_file
    misprediction = parsed.cmisprediction
    set_state(config_file, misprediction)

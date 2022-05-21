__version__ = '0.0.24'  # print(ultralytics.__version__)

from .main import connect_to_hub, train_model
from .yolov5_utils.general import PREFIX, check_requirements, colorstr, emojis, is_colab


def checks(verbose=True):
    # Check system software and hardware
    from .yolov5_wrapper import clone_yolo

    clone_yolo()

    print('Checking setup...')

    import os
    import shutil

    from .yolov5_utils.torch_utils import select_device  # imports

    check_requirements(('psutil', 'IPython'))
    import psutil
    from IPython import display  # to display images and clear console output

    if is_colab():
        shutil.rmtree('sample_data', ignore_errors=True)  # remove colab /sample_data directory

    if verbose:
        # System info
        # gb = 1 / 1000 ** 3  # bytes to GB
        gib = 1 / 1024 ** 3  # bytes to GiB
        ram = psutil.virtual_memory().total
        total, used, free = shutil.disk_usage("/")
        display.clear_output()
        s = f'({os.cpu_count()} CPUs, {ram * gib:.1f} GB RAM, {(total - free) * gib:.1f}/{total * gib:.1f} GB disk)'
    else:
        s = ''

    select_device(newline=False, version=__version__)
    print(emojis(f'Setup complete ✅ {s}'))


def login(api_key=''):
    # Login to Ultralytics HUB
    connect_to_hub(api_key, verbose=True)


def start(key=''):
    # Start training models with Ultralytics HUB
    # Test usage: from src.ultralytics import start; start('API_KEY')
    import getpass

    s = emojis(f'{PREFIX}Invalid API key ⚠️\n')  # error string
    if not key:
        key = getpass.getpass('Enter model key: ')
    assert '.' in key, s
    api_key, model_key = key.split('.')
    assert len(api_key) and len(model_key), s

    # key = 'ac0ab020186aeb50cc4c2a5272de17f58bbd2c0.RqFCDNBxgU4mOLmaBrcd'  # example
    # api_key='ac0ab020186aeb50cc4c2a5272de17f58bbd2c0', model_key='RqFCDNBxgU4mOLmaBrcd'  # example
    train_model(api_key=api_key, model_key=model_key)

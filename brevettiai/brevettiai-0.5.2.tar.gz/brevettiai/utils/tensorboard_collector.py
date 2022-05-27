"""
Tool to collect and show Tensorboard for multiple models
Call with model ids or an application id to select data to show in Tensorboard
"""
import argparse
import json
import os
import re
import tempfile
import time

import pandas as pd
import tensorflow as tf
from tensorboard import program
from tensorboard.plugins.hparams import api as hp
from tqdm import tqdm

from brevettiai.platform import PlatformAPI

type_mapper = {
    type(None): lambda x: "None",
    list: str,
}


def tensorboard_name(model_name, run_id):
    """Generate name for tensorboard log"""
    return re.sub(r'[\\/*?:"<>|]', "", f"{model_name} {run_id}").rstrip()


def _flatten_and_escape_params(obj):
    normalized = pd.json_normalize(obj).iloc[0].to_dict()
    safe = {k: type_mapper.get(type(v), lambda x: x)(v) for k, v in normalized.items()}
    return safe


def _get_models(model_ids, web: PlatformAPI = None):
    """Retrieve models from web ids sorted by creation"""
    models = web.get_model()
    models = sorted((m for m in models if m.id in model_ids), key=lambda m: m.created, reverse=True)
    return models


def application_tensorboard(application, web: PlatformAPI = None, logdir=None):
    """Start tensorboard with models on application"""
    web = web or PlatformAPI()
    if isinstance(application, str):
        application = web.get_application(application)
    models = _get_models(model_ids=application.model_ids, web=web)
    model_tensorboard(models, web=web, logdir=logdir)


def _get_model_safe(web, *args, **kwargs):
    try:
        return web.get_model(*args, **kwargs)
    except Exception:
        print(f"Skipping {args}")
        return None


def model_tensorboard(models: list, web: PlatformAPI = None, logdir=None):
    """Start tensorboard with specified models"""
    web = web or PlatformAPI()

    # If model is string use it as id to get model
    models = [_get_model_safe(web, model) if isinstance(model, str) else model for model in models]
    models = list(filter(None, models))

    if logdir is None:
        with tempfile.TemporaryDirectory() as tmpdir:
            start_tensorboard(models, web, tmpdir)
    else:
        start_tensorboard(models, web, logdir)


def download_tfevents(web, model, modeldir):
    """Download tfevents for tensorboard from model to modeldir"""
    # Add tensorboard logs from main artifact dir
    artifacts = web.get_artifacts(model, prefix="events.out.tfevents", add_prefix=True)
    for artifact in artifacts:
        if artifact.size < 100e6:
            dst = os.path.join(modeldir, artifact.name)
            web.download_url(artifact.link, dst)
        else:
            print(f"Skipping: {artifact.link}")

    # Add tensorboard logs from artifacts/tensorboard
    artifacts = web.get_artifacts(model, prefix="tensorboard/", recursive=True, add_prefix=True)
    for artifact in artifacts:
        if artifact.size < 100e6:
            dst = os.path.join(modeldir, *artifact.name.split("/")[1:])
            web.download_url(artifact.link, dst)
        else:
            print(f"Skipping: {artifact.link}")


def filter_and_write_hparam(hparam_list):
    # Filter nonunique hparams
    df = pd.DataFrame((p["hparam"] for p in hparam_list))
    nonunique = df.columns[df.nunique() == 1]
    if not df.columns.isin(nonunique).all():
        df = df.drop(nonunique, axis=1)

    # Log hparams
    for (ix, hparam), info in zip(df.iterrows(), hparam_list):
        with tf.summary.create_file_writer(info["logdir"], filename_suffix="output_hparam").as_default():
            hp.hparams(hparam.to_dict(), trial_id=info["trial_id"])


def start_tensorboard(models, web, logdir):
    print("Cleaning output.json hparams")
    for root, folder, files in os.walk(logdir):
        for file in files:
            if file.endswith("output_hparam"):
                os.remove(os.path.join(root, file))

    tb = program.TensorBoard()
    tb.configure(argv=[None, '--logdir', logdir])
    url = tb.launch()
    print(f"Tensorflow listening on {url}")

    hparam_list = []
    for model in tqdm(models):
        output_files = web.get_artifacts(model, prefix="output.json")
        if len(output_files) == 0:
            print(f"skipping {model.name}")
            continue

        output = json.loads(web.download_url(output_files[0].link))
        run_id = output.get("job", {}).get("run_id", model.created)

        logname = tensorboard_name(model.name, run_id)
        modeldir = os.path.join(logdir, logname)

        # Add Hyper parameters
        try:
            hparam_list.append({
                "hparam": _flatten_and_escape_params(output.get("job", output.get("config"))["settings"]),
                "logdir": modeldir,
                "trial_id": logname
            })
        except Exception:
            print("Warning: error extracting parameters from", model.name)

        download_tfevents(web, model, modeldir)

    filter_and_write_hparam(hparam_list)

    if not os.listdir(logdir):
        print("No tensorboards found")
    else:
        while True:
            time.sleep(1000)


def main(target, logdir=None):
    """ Run Tensorboard collector"""
    web = PlatformAPI()

    # default logdir if caching is active
    if logdir is None:
        logdir = os.path.join(web.io.cache_root, "tensorboard")

    if len(target) == 1:
        try:
            web.get_model(target[0])
        except PermissionError:
            application = web.get_application(target[0])
            if application:
                application_tensorboard(application, web=web, logdir=logdir)
                quit()

    model_tensorboard(target, web=web, logdir=logdir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--logdir', help="logdir to use for tensorboard", default=None)
    parser.add_argument('target', nargs='+', help="Application id or space separated model ids")
    arg = parser.parse_args()

    main(arg.target, arg.logdir)

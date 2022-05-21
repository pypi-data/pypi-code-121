import json
import time

import requests

from .config import HUB_API_ROOT
from .yolov5_utils.general import LOGGER, PREFIX, threaded, emojis


class HUBLogger:
    api_url = HUB_API_ROOT + "model-checkpoint"

    def __init__(self, model_id, auth):
        self.model_id = model_id
        self.payload = {"modelId": model_id, **auth.get_auth_string()}
        self.rate_limit = 60.0  # minimum seconds between checkpoint uploads
        self.t = time.time()  # last upload time
        self.keys = [
            'train/box_loss',
            'train/obj_loss',
            'train/cls_loss',  # train loss
            'metrics/precision',
            'metrics/recall',
            'metrics/mAP_0.5',
            'metrics/mAP_0.5:0.95',  # metrics
            'val/box_loss',
            'val/obj_loss',
            'val/cls_loss',  # val loss
            'x/lr0',
            'x/lr1',
            'x/lr2']  # metrics keys

    def on_fit_epoch_end(self, *args, **kwargs):
        # Upload metrics after val end
        vals, epoch = args[:2]
        metrics = json.dumps({k: round(float(v), 5) for k, v in zip(self.keys, vals)})  # json string
        self._upload_metrics(epoch, metrics)

    def on_model_save(self, *args, **kwargs):
        # Upload checkpoints with rate limiting
        last, epoch, final_epoch, best_fitness, fi = args[:5]
        is_best = best_fitness == fi
        if (time.time() - self.t) > self.rate_limit:
            LOGGER.info(f"{PREFIX}Uploading checkpoint {self.model_id}")
            self._upload_model(epoch, last, is_best)
            self.t = time.time()

    def on_pretrain_routine_end(self, *args, **kwargs):
        # Tell HUB that training has started
        data = {**self.payload, "type": "initial"}
        self.post(data, {"void": None})  # KNOWN ISSUE https://github.com/ultralytics/hub-pip-package/issues/10
        LOGGER.info(emojis(f"{PREFIX}View model at https://hub.ultralytics.com/models/{self.model_id} 🚀"))

    def on_train_end(self, *args, **kwargs):
        # Upload final model and metrics with exponential standoff
        last, best, plots, epoch, results = args[:5]
        LOGGER.info(emojis(f"{PREFIX}Training completed successfully ✅"))
        LOGGER.info(f"{PREFIX}Uploading final {self.model_id}")
        self._upload_model(epoch, best, map=results[3], final=True)  # results[3] is mAP0.5:0.95
        LOGGER.info(emojis(f"{PREFIX}View model at https://hub.ultralytics.com/models/{self.model_id} 🚀"))

    # Internal functions ---
    def _upload_metrics(self, epoch, metrics):
        data = {**self.payload, "epoch": epoch, "metrics": metrics, "type": "metrics"}
        self.post(data, {"void": None})

    def _upload_model(self, epoch, weights, is_best=False, map=0.0, final=False):
        with open(weights, "rb") as f:
            if final:
                data = {**self.payload, "epoch": epoch, "type": "final", "map": map}
                self.post(data, {"best.pt": f.read()}, retry=10, timeout=3600)
            else:
                data = {**self.payload, "epoch": epoch, "type": "epoch", "isBest": bool(is_best)}
                self.post(data, {"last.pt": f.read()})

    @threaded
    def post(self, data, files, retry=3, timeout=30):
        # requests.post with exponential standoff retries up to timeout(seconds)
        t0 = time.time()
        for i in range(retry + 1):
            r = requests.post(self.api_url, data=data, files=files)
            if r.status_code == 200 or (time.time() - t0) > timeout:
                return
            if i == 0:
                LOGGER.warning(f"{PREFIX}sync failure {r.status_code} {r.reason}... retrying {retry}x up to {timeout}s")
            time.sleep(2 ** i)  # exponential standoff

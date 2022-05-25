class BatchIds(object):
    def __init__(self):
        self.ids = list()
        self.map = {}


class StorageMeta(object):
    def __init__(self, validation_split=0, validation_tag="v"):
        self.sequence_number = 0
        self._validation_split = validation_split
        self._validation_tag = validation_tag

        self._val_cadence = None
        if self._validation_split > 0:
            self._val_cadence = int(100 // (self._validation_split * 100))

        self.train = BatchIds()
        self.validation = BatchIds()

    def _get_paths(self, validation=False):
        val_tag = "" if not validation else self._validation_tag
        filename = f"ID{val_tag}_{self.sequence_number}"
        return filename

    def get_ids(self, validation):
        return self.train.ids if not validation else self.validation.ids

    def get_map(self, validation):
        return self.train.map if not validation else self.validation.map

    def save(self):
        if self._val_cadence and self.sequence_number % self._val_cadence == 0:
            filename = self._get_paths(validation=True)
            self.validation.ids.append(self.sequence_number)
            self.validation.map[self.sequence_number] = filename
            self.sequence_number += 1
        else:
            filename = self._get_paths()
            self.train.ids.append(self.sequence_number)
            self.train.map[self.sequence_number] = filename
            self.sequence_number += 1

        return filename

    def get_meta_params(self):
        params = {
            'train_ids': self.train.ids,
            'train_map': self.train.map,
            'val_ids': self.validation.ids,
            'val_map': self.validation.map,
        }
        return params

    def set_meta_params(self, params):
        params["train_map"] = {int(k): v for k, v in params["train_map"].items()}
        params["val_map"] = {int(k): v for k, v in params["val_map"].items()}

        self.train.ids = params["train_ids"]
        self.train.map = params["train_map"]
        self.validation.ids = params["val_ids"]
        self.validation.map = params["val_map"]

    def load(self, batch_id, validation=False):
        filename = self.get_map(validation)[batch_id]
        return filename

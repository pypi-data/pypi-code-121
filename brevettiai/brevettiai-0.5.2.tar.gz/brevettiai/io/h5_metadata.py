import h5py
import json


def set_metadata(h5_path, metadata):
    if not isinstance(metadata, str):
        try:
            metadata = metadata.json()
        except AttributeError:
            metadata = json.dumps(metadata)
    with h5py.File(h5_path, mode='a') as f:
        f.attrs['metadata'] = metadata


def extract_metadata(file_obj: h5py.File = None):
    if "metadata" in file_obj.attrs:
        return json.loads(file_obj.attrs['metadata'])
    else:
        return {}


def get_metadata(h5_path):
    with h5py.File(h5_path, mode='r') as f:
        return extract_metadata(f)


def save_model(path, model, metadata):
    assert path.endswith(".h5")
    retval = model.save(path)
    set_metadata(path, metadata)
    return retval
from multiprocessing import cpu_count, Pool, current_process, Manager, get_context
import os
import h5py
import shutil
from time import time
from h5mapper import *


class MPITest(TypedFile):
    x = VShape(Image())


if __name__ == '__main__':
    container = "container-test"
    mode = 'w'
    if os.path.exists(container):
        shutil.rmtree(container)
        os.makedirs(container, exist_ok=True)
    else:
        os.makedirs(container, exist_ok=True)
    f = {}
    targets = Manager().dict()


    def func(source):
        i = current_process().ident
        if i not in f:
            target = f"{container}/pid_{i}.h5"
            targets[i] = target
            f[i] = MPITest(target, "w", keep_open=True)
        f[i].add(source, f[i].load(source))
        f[i].flush()

    fw = FileWalker(r'.jpeg$', '../vigan')
    now = time()
    with get_context('fork').Pool(16) as p:
        p.map(func, list(fw), 16)

    master = MPITest(f"{container}/master.h5", 'w').handle()
    targets = dict(targets)

    now2 = time()
    print("COPY!", now2 - now)
    src_ds = {}
    for k, v in targets.items():
        sub = h5py.File(v)
        links = []

        def add_link(name, obj):
            if isinstance(obj, h5py.Dataset):
                links.append(obj.name)

        sub.visititems(add_link)
        # sub.close()
        for l in links:
            # master[str(k) + l] = h5py.ExternalLink(v, l)
            src_ds.setdefault(l, []).append(sub[l])
        master.flush()

    now = time()
    print("VDS", now - now2)
    for key, datasets in src_ds.items():
        layout = h5py.VirtualLayout((sum(ds.shape[0] for ds in datasets), *datasets[0].shape[1:]), datasets[0].dtype)
        offset = 0
        for ds in datasets:
            layout[offset:offset + ds.shape[0]] = h5py.VirtualSource(ds)
            offset += ds.shape[0]
        master.create_virtual_dataset(key, layout)
        master.flush()
    now2 = time()
    print("CLOSE", now2 - now)
    master.close()
    # now2 = time()
    print("Open", now2 - now)

    now = time()
    print("DONE", now - now2)
    f = MPITest(f"{container}/master.h5", 'r', keep_open=True)
    f.info()
    print(len(f.index), f.get(list(f.index.keys())[0]))


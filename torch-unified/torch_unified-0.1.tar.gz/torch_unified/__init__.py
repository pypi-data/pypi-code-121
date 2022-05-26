import torch

if torch.cuda.is_available():
    import _torch_unified_gpu
    empty_unified = _torch_unified_gpu.empty_unified

else:
    def empty_unified(*args, **kwargs):
        raise NotImplementedError("Unified memory model only available when cuda support is enabled.")

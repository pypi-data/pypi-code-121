#!/usr/bin/env python3
import torch
if torch.cuda.device_count() > 0:
    print(f"Current device:".ljust(20) + f"{torch.cuda.current_device()}")
    print(f"CUDA device count:".ljust(20) + f"{torch.cuda.device_count()}")
    print(f"CUDA device name:".ljust(20) + f"{torch.cuda.get_device_name(0)}")
    print(f"CUDA available:".ljust(20) + f"{torch.cuda.is_available()}")
else:
    print("No CUDA device.")
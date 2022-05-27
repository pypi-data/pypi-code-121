import os
from pathlib import Path

WORK_DIR = os.path.expanduser('~/HybridGarden')
MODELS_DIR = os.path.expanduser('~/HybridGarden/models')
METADATA_DIR = os.path.expanduser('~/HybridGarden/metadata')
REPORTS_DIR = os.path.expanduser('~/HybridGarden/reports')

if not (os.path.isdir(WORK_DIR) or os.path.isdir(MODELS_DIR) or os.path.isdir(METADATA_DIR)):
    
    try:
        Path(WORK_DIR).mkdir(parents=True, exist_ok=True)
        print(u"Созданы рабочие папки проекта:")
        print("Working directory:", WORK_DIR)
        Path(MODELS_DIR).mkdir(parents=True, exist_ok=True)
        print("Models directory:", MODELS_DIR)
        Path(METADATA_DIR).mkdir(parents=True, exist_ok=True)
        print("Metadata directory:", METADATA_DIR)
        Path(REPORTS_DIR).mkdir(parents=True, exist_ok=True)
        print("Reports directory:", REPORTS_DIR)
    except:
        "Could not create working directory!"   

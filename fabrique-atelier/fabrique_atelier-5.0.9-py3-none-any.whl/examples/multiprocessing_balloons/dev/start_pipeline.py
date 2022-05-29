import sys
import json

sys.path.append('..')
from pipeline import pipeline, colors

binary_messages = [json.dumps({'color': colors[k % len(colors)]}).encode() for k in range(20)]

pipeline.start_emulation(binary_messages)
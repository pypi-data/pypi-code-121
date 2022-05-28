# 2022.2.21
import json, sys, time, fire, os

def run(infile):
	with open("frame.json", 'a+') as fw:
		try:
			arr = [json.loads(line.strip()) for line in open(infile,'r').readlines() ]
			word = infile.split('.')[0]
			fw.write(f"{word}\t{json.dumps(arr)}\n")
		except Exception as e:
			print("ex:", e, infile)

if __name__ == '__main__':
	fire.Fire(run)

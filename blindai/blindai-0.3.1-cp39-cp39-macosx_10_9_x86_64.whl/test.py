from blindai.client import BlindAiClient, ModelDatumType

client = BlindAiClient()

client.connect_server(addr="159.8.110.148", policy="policy.toml",
simulation=False, certificate='host_server.pem')

client.upload_model(model="./COVID-Net-CXR-2.onnx", shape=(1,480,480,3), dtype=ModelDatumType.F32, sign=True)

flattened_image = []
with open("flattened-image.txt") as image:
    lines =  image.read()
    lines = lines.strip().split(',')
    flattened_image = list(map(lambda a: float(a), lines))

output = client.run_model(flattened_image, sign=True)

print(output.output)
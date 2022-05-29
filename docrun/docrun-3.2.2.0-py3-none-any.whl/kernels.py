import json
import jupyter_client

print(json.dumps( jupyter_client.kernelspec.find_kernel_specs() ) )

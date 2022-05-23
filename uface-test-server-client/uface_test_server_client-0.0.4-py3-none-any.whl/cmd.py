import inference_stub
import argparse

def model_speed_test():
    args_parser=argparse.ArgumentParser()
    args_parser.add_argument("ip",type=str,help="consul ip")
    args_parser.add_argument("--port",type=int,default=8500, help="consul port, default is 8500")
    args_parser.add_argument("model_name",type=str,required=True,help="model's name")
    args_parser.add_argument("model_version",type=str,required=True,help="model's version")
    args_parser.add_argument("model_backend",type=str,required=True,help="model's backend")
    args_parser.add_argument("--run_times",type=int,default=1,required=False,help="how many times to run")
    args_parser.add_argument("--batch",type=int,default=1,required=False,help="batch size")
    args_parser.add_argument("--request_id",type=str,default="speed_test",required=False,help="request id")
    args=args_parser.parse_args()
    stub = inference_stub.InferenceStub(ip=args.ip,port=args.port)
    response = stub.model_speed_test_sync(model_name=args.model_name,model_version=args.model_version,
                               backend=args.backend,request_id=args.request_id,run_times=args.run_times,
                               batch=args.batch)
    print(response)


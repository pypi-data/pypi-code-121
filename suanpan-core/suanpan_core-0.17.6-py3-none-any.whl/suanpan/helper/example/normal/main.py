import suanpan
from suanpan.app import app
from suanpan.app.arguments import Folder, String


@app.input(Folder(key="inputData1"))
@app.output(Folder(key="outputData1"))
@app.param(String(key="param1"))
def test(context):
    args = context.args
    print(args.inputData1)
    print(args.outputData1)
    print(args.param1)
    return args.inputData1


if __name__ == "__main__":
    suanpan.run(test)

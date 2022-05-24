import inspect
from unitgrade.utils import hide, methodsWithDecorator
import os
import importlib


def remove_hidden_methods(ReportClass, outfile=None):
    # Given a ReportClass, clean out all @hidden tests from the imports of that class.
    file = ReportClass()._file()
    with open(file, 'r') as f:
        source = f.read().splitlines()

    lines_to_rem = []

    for Q,_ in ReportClass.questions:
        ls = list(methodsWithDecorator(Q, hide))
        print("hide decorateed is", ls)
        for f in ls:
            s, start = inspect.getsourcelines(f)
            end = len(s) + start
            lines_to_rem += list(range(start-1, end-1))

    source = list([l for k, l in enumerate(source) if k not in lines_to_rem])
    source = "\n".join(source)

    if outfile == None:
        outfile = file[:-3] + "_nohidden.py"

    if os.path.exists(outfile) and os.path.samefile(file, outfile):
        raise Exception("Similar file paths identified!")
    with open(outfile, 'w') as f:
        f.write(source)

    module_name = ReportClass.__module__
    module_name.find(".")
    module_name = module_name[:module_name.rfind(".")] + "." + os.path.basename(outfile)[:-3]

    module = importlib.import_module(module_name)

    HiddenReportClass = getattr(module, ReportClass.__name__)
    return outfile, HiddenReportClass

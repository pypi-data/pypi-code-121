import __init__
import unittest
from TDhelper.generic.recursion import recursion,recursionCall

@recursion
def fibonacci(i,step,**kwargs):
    i+=step if step else 1
    if i>=3000:
        kwargs["break"] = False
        return i,kwargs
    return fibonacci(i,step,**kwargs)

@recursion
def layers(item, **kwargs):
    print(item,kwargs,"\r\n")
    if "children" in item:
        for o in item["children"]:
            recursionCall(layers,kwargs["limit"],o, **kwargs)
        kwargs["break"] = False
    else:
        kwargs["break"]= False
    return item, kwargs

class TestReflect(unittest.TestCase):

    def test_recursion_fibonacci_call(self):
        b=recursionCall(fibonacci,100,1,1,**{})
        print("end",b,"\r\n")

    def test_recursion_more_layer_call(self):
        b = recursionCall(
                layers,
                2,
                {
                    "name": "a",
                    "children": [
                        {
                            "name": "b",
                            "children": [
                                {"name": "c", "children": [{"name": "d"}]},
                                {"name": "e", "children": [{"name": "f"}]},
                            ],
                        },
                        {
                            "name": "g",
                            "children": [
                                {"name": "h", "children": [{"name": "i"}]},
                                {"name": "j", "children": [{"name": "k","children":[
                                    {"name": "l","children":[
                                        {"name": "m","children":[
                                            {"name": "n","children":[
                                                {"name": "o","children":[
                                                    {"name": "p","children":[
                                                        {"name": "q","children":[
                                                            {"name": "r","children":[
                                                                {"name": "s","children":[
                                                                    {"name": "t","children":[
                                                                        {"name": "u","children":[
                                                                            {"name": "v","children":[
                                                                                {"name": "w","children":[
                                                                                    {"name": "x","children":[
                                                                                        {"name": "y","children":[
                                                                                            {"name": "z"}
                                                                                        ]}
                                                                                    ]}
                                                                                ]}
                                                                            ]}
                                                                        ]}
                                                                    ]}
                                                                ]}
                                                            ]}
                                                        ]}
                                                    ]}
                                                ]}
                                            ]}
                                        ]}
                                    ]}
                                ]}]},
                            ],
                        },
                    ],
                },
                **{}
            )

if __name__ == "__main__":
    unittest.main()
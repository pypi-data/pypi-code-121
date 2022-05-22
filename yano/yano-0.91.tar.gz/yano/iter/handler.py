from .helper import remove_const_features, train_test_split, shuffle, crossvalidate, normalize, asfloat, asint


class handler(object):
    def __init__(self, child, mods=None):
        self.child = child
        if mods is None:
            mods = []
        self.mods = mods
        self.args={}
        self.order=["d","x","y","train","testx","testy","folds"]


    def assertmod(self, mod):
        if mod not in self.mods:
            self.mods.append(mod)
    def fixmods(self):
        for zw in ["split","nonconst","split","crossval","normalize_zscore","normalize_minmax", "asfloat", "asint", "cut"]:
            if zw in self.mods:
                self.assertmod("dxy")
        if "listfold" in self.mods:
            self.assertmod("crossval")
        assert not ("crossval" in self.mods and "split" in self.mods), "test-train split and cross-validation are not mutually exclusive"

    def yield_order(self, q):
        ret=[]
        for key in self.order:
            if key in q:
                ret.append(q[key])
        return ret

    def __iter__(self):
        self.fixmods()
        for i,d in enumerate(self.child):
            if "cut" in self.mods:
                cut=self.args["cut"]["kwargs"]["maxima"]
                if i>=cut:break

            ac={"d":d}
            if "dxy" in self.mods:
                ac["x"],ac["y"]=ac["d"].getxy()

            if "asint" in self.mods:
                ac["x"]=asint(ac["x"])
                ac["y"]=asint(ac["y"])

            if "asfloat" in self.mods:
                ac["x"]=asfloat(ac["x"])
                ac["y"]=asfloat(ac["y"])

            if "nonconst" in self.mods:
                ac["x"]=remove_const_features(ac["x"])

            if "split" in self.mods:
                ac["train"],ac["testx"],ac["testy"]=train_test_split(ac["x"],ac["y"],*self.args["split"]["args"],**self.args["split"]["kwargs"])
                del ac["x"]
                del ac["y"]

            if "crossval" in self.mods:
                ac["folds"]=crossvalidate(ac["x"],ac["y"],*self.args["crossval"]["args"],**self.args["crossval"]["kwargs"])
                del ac["x"]
                del ac["y"]

            if "shuffle" in self.mods:
                try:
                    seed=self.args["shuffle"]["kwargs"]["seed"]
                    callab=lambda x,y=None: shuffle(x,y,seed=seed)
                except KeyError:
                    callab=shuffle
                
                if "split" in self.mods:
                    ac["train"]=callab(ac["train"])
                    ac["testx"],ac["testy"]=callab(ac["testx"],ac["testy"])
                elif "crossval" in self.mods:
                    ac["folds"]=((callab(x),*callab(tx,ty)) for x,tx,ty in ac["folds"])

                else:
                    ac["x"],ac["y"]=shuffle(ac["x"],ac["y"],seed=self.args["shuffle"]["kwargs"]["seed"])

            if "normalize_zscore" in self.mods:
                if "split" in self.mods:
                    ac["train"],ac["testx"]=normalize(ac["train"],ac["testx"],"zscore")
                elif "crossval" in self.mods:
                    ac["folds"]=((*normalize(x,tx,"zscore"),ty) for x,tx,ty in ac["folds"])
                else:
                    ac["x"]=normalize(ac["x"],method="zscore")
            if "normalize_minmax" in self.mods:
                if "split" in self.mods:
                    ac["train"],ac["testx"]=normalize(ac["train"],ac["testx"],"minmax")
                elif "crossval" in self.mods:
                    ac["folds"]=((*normalize(x,tx,"minmax"),ty) for x,tx,ty in ac["folds"])
                else:
                    ac["x"]=normalize(ac["x"],method="minmax")


            yield self.yield_order(ac)

def arg_dic(*args,**kwargs):
    return {"args":[*args],"kwargs":{**kwargs}}

def adaptive(zw, mod, *args, **kwargs):
    if type(zw) is handler:
        zw.mods.append(mod)
        zw.args[mod]=arg_dic(*args,**kwargs)
        return zw
    else:
        ret= handler(zw, [mod])
        ret.args[mod]=arg_dic(*args,**kwargs)
        return ret





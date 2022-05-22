from ..utils import run_algo, eval_func, test_algo, test_algo_n
from ..data.iterate import load_dataset
from ..stats import Stats, average_stats, negative_infinity, maximum_stats

import numpy as np
import json

from ..helper import adaptricallable


class Logger(object):

    def __init__(self, algos, algo_names=None, verbose=0, addfeat=False):

        assert type(algos) == dict or (not algo_names is None and type(algos)==list), "algos must be a list, or algo_names must be provided"

        if type(algos) == dict:
            self.algos = list(algos.values())
            self.algo_names = list(algos.keys())
        else:
            self.algos = algos
            self.algo_names = algo_names

        self.verbose = verbose

        self.datasets=[]
        self.results=[]
        self.addfeat=addfeat

    def add_run(self,dataset, results, verbose=None):
        if verbose is None:
            verbose = self.verbose
        
        if any([zw.isnan() for zw in results]):
            if verbose>0:
                print(f"Some results are NaN, skipping {dataset}")
            return
        self.datasets.append(dataset)
        self.results.append(results)

    def save(self, path):
        with open(path, 'w') as f:
            json.dump({'datasets':[zw.name() for zw in self.datasets], 'results':[[zw.to_list() for zw in zx] for zx in self.results],'algo_names':self.algo_names}, f, indent=2)

    def load(self,path):
        with open(path, 'r') as f:
            d = json.load(f)
        self.datasets = [load_dataset(zw) for zw in d['datasets']]
        self.results = [[Stats(zw) for zw in zx] for zx in d['results']]
        self.algo_names = d['algo_names']
        self.algos=[None for _ in self.algo_names]

    def run_on(self, d, x, tx, ty, n=10, verbose=None):
        if verbose is None:
            verbose = self.verbose
        if verbose>0:
            print("Running on dataset:", d)

        lis=[]
        for algo, nam in zip(self.algos, self.algo_names):

            results = test_algo_n(algo, x, tx, ty, n=n)
            if verbose>1:
                print(f"Results of {nam}: {results.shortstr()}")
            lis.append(results)
        self.add_run(d, lis,verbose=verbose)

    def run_cross(self, d, folds, verbose=None):
        if verbose is None:
            verbose = self.verbose
        if verbose>0:
            print("Running on dataset:", d)

        lis=[]
        for algo, nam in zip(self.algos, self.algo_names):
            results=[]
            for x,tx,ty in folds:
                qual = test_algo(algo, x, tx, ty)
                results.append(qual)
            results=Stats(results)
            if verbose>1:
                print(f"Results of {nam}: {results.shortstr()}")
            lis.append(results)
        self.add_run(d, lis, verbose=verbose)




    def run_on_all(self, iterable, *args, **kwargs):
        for zw in iterable:
            self.run_on(*zw, *args, **kwargs)

    def _sort(self, addmean=True):
        """helper function to sort stuff before showing it. Just to look nicer"""
        algo_names = self.algo_names
        datasets = self.datasets
        results = self.results
        means=np.array([[zw.mean() for zw in zx] for zx in results])
        i_algo_names = [i for i,zw in enumerate(algo_names)]
        i_datasets = [i for i,zw in enumerate(datasets)]

        score_dataset=np.mean(means, axis=1)
        score_algo=np.mean(means, axis=0)

        i_algo_names.sort(key=lambda x: -score_algo[x])
        i_datasets.sort(key=lambda x: score_dataset[x])

        algo_names = [algo_names[i] for i in i_algo_names]
        datasets = [datasets[i] for i in i_datasets]
        results = [[results[i][j] for j in i_algo_names] for i in i_datasets]

        if addmean:
            datasets.append("")
            datasets.append("Average")
            toa1=["" for _ in algo_names]
            toa2=[average_stats([zw[i] for zw in results]) for i in range(len(algo_names))]
            results.append(toa1)
            results.append(toa2)

        return algo_names, datasets, results



    def show(self, addfeat=None):
        if addfeat is None:
            addfeat=self.addfeat

        try:
            from tabulate import tabulate
        except ImportError:
            print("tabulate not installed, cannot show results!")
            return

        algo_names, datasets, results = self._sort()

        headers = ['Dataset'] + algo_names
        rows = []
        def trafo_to_str(q):
            return adaptricallable(q, "mediumstr")()

        for d, r in zip(datasets, results):
            rows.append([adaptricallable(d,"name_and_feat" if addfeat else "name")()] + [trafo_to_str(zw) for zw in r])
        print(tabulate(rows, headers=headers))


    def to_latex(self, addfeat=None):
        if addfeat is None:
            addfeat=self.addfeat
        try:
            from tabulate import tabulate
        except ImportError:
            print("tabulate not installed, cannot show results!")
            return
        algo_names, datasets, results = self._sort()
        headers = ['Dataset'] + algo_names
        rows = []
        vals = []
        def trafo_to_str(q):
            return adaptricallable(q, "mediumstr")()

        for d, r in zip(datasets, results):
            rows.append([adaptricallable(d,"name_and_feat" if addfeat else "name")()] + [trafo_to_str(zw) for zw in r])
            if type(r[0]) is str:
                vals.append([negative_infinity() for _ in range(len(r)+1)])
 
            else:    
                vals.append([negative_infinity()]+ [zw for zw in r])

        #print(vals)
        #print(len(vals))
        #print(len(vals[0]))
        #exit()

        maximas=[maximum_stats(zw) for zw in vals]
        maximas=[[trafo_to_str(zw) for zw in zx] for zx in maximas]

        def boldspace(s, keys=None):
            s=s.strip()
            if keys is None:
                keys = ["+"]
            key=keys[0]
            if key in s:
                bef=s[:s.index(key)]
                aft=s[s.index(key):]
                s=f"\\textbf{{{bef}}} {aft}"
            
            if len(keys)>1:
                return boldspace(s, keys=keys[1:])
            else:
                if "\\textbf" in s:
                    return s
                else:
                    return f"\\textbf{{{s}}}"

        def latexify(s, bold=False):
            if bold:
                return latexify(boldspace(s))
            return "$"+str(s).replace("_","\_").replace("+-"," \\pm ")+"$"#not the best solution
        rows = [[latexify(zw, zw in maxima) for zw in zx] for zx,maxima in zip(rows,maximas)]
        return tabulate(rows, headers=headers, tablefmt="latex_raw")
















import wrapper as pyw
import sys

r=3
n=3
env = pyw.fm_init( n)
pyw.isTest = True

A = pyw.ShowCoalitions( env)
print( "Fuzzy measure wrt n=3 criteria has ",env.m," parameters ordered like this (binary order)")
print( A)
pyw.fm_free( env);

ti=1
n=4
env = pyw.fm_init( n);
size, v = pyw.generate_fm_2additive_concave( ti,n, env)
print( "2-additive concave FM in Mobius and its length (n=4)")
print( v)
print("has ", size, " nonzero parameters ")

print("A convex FM in cardinality ordering ")
A = pyw.ShowCoalitionsCard( env)
print( A)

size, v = pyw.generate_fmconvex_tsort( ti, n, n-1 , 1000, 8, 1, env)
print( v)
print("has ", size, " nonzero parameters ")

vb = pyw.ConvertCard2Bit( v, env)

print("a convex FM in binary ordering ")
A = pyw.ShowCoalitions( env)
print( A)
print( vb)

r = pyw.IsMeasureSupermodular( vb, env)
print( "Is it convex (test)?", r)
r = pyw.IsMeasureAdditive( vb, env)
print("Is it additive (test)?", r)

mc = pyw.export_maximal_chains( n, vb, env)
print( "Export maximal chains ")
print( mc)

x = [0.2,0.1,0.6,0.2]
z = pyw.Choquet( x, vb, env)
print( "Choquet integral of ",x, " is ",z)

z = pyw.Sugeno( x, vb, env)
print("Sugeno integral of ",x,  " is ",z)


###
# Test generated wrapper
###

# Test wrapper for:
#    double py_ChoquetKinter(double* x, double* v, int kint, struct fm_env* env)
x = [0.2,0.5,0.4]
v = [0,0.3,0.5,0.6,0.4,0.8,0.7,1]
kint = 2
r = pyw.ChoquetKinter( x, v, kint, env)
print( "Choquet integral of: ", kint, x, v)
print( "equals: ", r)

# Test wrapper for:
#    double py_Orness(double* Mob, struct fm_env* env)
v = [0,0.3,0.5,0.6,0.4,0.8,0.7,1]
r = pyw.Orness(v, env)
print( "orness value of the Choquet integral wrt fuzzy measure v: ", v)
print( "equals: ", r)

# Test wrapper for:
#    void py_NonmodularityIndexKinteractive(double* v, double* out_w, int kint,  struct fm_env* env)
kint = 2
v = [0,0.3,0.5,0.6,0.4,0.8,0.7,1]
pnm = pyw.NonmodularityIndexKinteractive( v, kint, env)
print( "nonmodularity indices of k-interactive fuzzy measure v: ", kint, v)
print( "equals: ", pnm)


# Test wrapper for:
#    double py_min_subset(double* x, int n, int_64 S)
x = [0,0.3,0.5,0.6,0.7,0.8,0.85,0.9]
n = len( x)
S = 6
min = pyw.min_subset( x, n, S)
print( "x: ", x)
print( "n: ", n)
print( "S: ", S)
print( "min: ", min)


# Test wrapper for:
#    double py_max_subset(double* x, int n, int_64 S)
# pyw.max_subset(x, n, S)
x = [0,0.3,0.5,0.6,0.7,0.8,0.85,0.9]
n = len( x)
S = 5
max = pyw.max_subset( x, n, S)
print( "x: ", x)
print( "n: ", n)
print( "S: ", S)
print( "max: ", max)

# Test wrapper for:
#    double py_min_subsetC(double* x, int n, int_64 S, struct fm_env* env)
x = [0,0.3,0.5]
n = len( x)
S = 3
min = pyw.min_subsetC( x, n, S, env)
print( "x: ", x)
print( "n: ", n)
print( "S: ", S)
print( "min: ", min)

# Test wrapper for:
#    double py_max_subsetNegC(double* x, int n, int_64 S, struct fm_env* env)
x = [0,0.3,0.5]
n = len( x)
S = 3
max = pyw.max_subsetNegC( x, n, S, env)
print( "x: ", x)
print( "n: ", n)
print( "S: ", S)
print( "max: ", max)

# Test wrapper for:
#    int py_SizeArraykinteractive(int n, int k, struct fm_env* env)
n = 3
k = 1
s = pyw.SizeArraykinteractive(n, k, env)
print( "n: ", n)
print( "k: ", k)
print( "size: ", s)

# Test wrapper for:
#    int py_IsSubsetC(int i, int j, struct fm_env* env)
i = 2
j = 1
s = pyw.IsSubsetC(n, k, env)
print( "i: ", i)
print( "j: ", j)
print( "size: ", s)

# Test wrapper for:
#    int py_IsElementC(int i, int j, struct fm_env* env)
i = 2
j = 1
s = pyw.IsElementC(n, k, env)
print( "i: ", i)
print( "j: ", j)
print( "size: ", s)

# Test wrapper for:
#    void py_ExpandKinteractive2Bit(double* out_dest, double* src, struct fm_env* env, int kint, int arraysize)
src = [0.0340916, 0.01109779, 0.07918582,0.7,1]
kint = 1
dest = pyw.ExpandKinteractive2Bit(src, env, kint)
print( "src: ", src)
print( "kint: ", kint)
print( "dest: ", dest)

# Test wrapper for:
#    void py_ExpandKinteractive2Bit_m(double* out_dest, double* src, struct fm_env* env, int kint, int arraysize, double* out_VVC)
src = [0.0340916, 0.01109779, 0.07918582,0.7,1]
kint = 1
dest, VVC = pyw.ExpandKinteractive2Bit_m(src, env, kint)
print( "src: ", src)
print( "kint: ", kint)
print( "dest: ", dest)
print( "VVC: ", VVC)

# Test wrapper for:
#    void py_Shapley(double* v, double* out_x, struct fm_env* env)
# pyw.Shapley(v, env)
v = [0,0.3,0.5,0.6,0.4,0.8,0.7,1]
x = pyw.Shapley( v, env)
print( "v: ", v)
print( "x: ", x)

# Test wrapper for:
#    void py_Banzhaf(double* v, double* out_B, struct fm_env* env)
v =[0.0,0.3,0.5,-0.2,0.4,0.1,-0.2,0.1]
x = pyw.Banzhaf(v, env)
print( "v: ", v)
print( "x: ", x)


# Test wrapper for:
#    void py_ShapleyMob(double* Mob, double* out_x, struct fm_env* env)
Mob = [0.0,0.3,0.5,-0.2,0.4,0.1,-0.2,0.1]
x = pyw.ShapleyMob( Mob, env)
print( "Mob: ", Mob)
print( "x: ", x)


# Test wrapper for:
#    void py_BanzhafMob(double* Mob, double* out_B, struct fm_env* env)
Mob = [0.0,0.3,0.5,-0.2,0.4,0.1,-0.2,0.1]
x = pyw.BanzhafMob(Mob, env)
print( "Mob: ", Mob)
print( "x: ", x)

# Test wrapper for:
#    double py_ChoquetMob(double* x, double* Mob, struct fm_env* env)
x =[0.6,0.3,0.8]
Mob = [0.0,0.3,0.5,-0.2,0.4,0.1,-0.2,0.1]
c = pyw.ChoquetMob(x, Mob, env)
print( "Mob: ", Mob)
print( "x: ", x)
print( "Choquet integral: ", c )

# Test wrapper for:
#    void py_ConstructLambdaMeasure(double* singletons, double* out_lambdax, double* out_v, struct fm_env* env)
singletons = [0, 0.3, 0.5]
lambdax, v = pyw.ConstructLambdaMeasure(singletons, env)
print( "singletons: ", singletons)
print( "lambdax, v: ", lambdax, v)

# Test wrapper for:
#    void py_ConstructLambdaMeasureMob(double* singletons, double* out_lambdax, double* out_Mob, struct fm_env* env)
singletons = [0, 0.3, 0.5]
lambdax, Mob = pyw.ConstructLambdaMeasureMob(singletons, env)
print( "singletons: ", singletons)
print( "lambdax, Mob: ", lambdax, Mob)

# Test wrapper for:
#    void py_dualm(double* v, double* out_w, struct fm_env* env)
v =[0,0.3,0.5,0.6,0.4,0.8,0.7,1]
w = pyw.dualm(v, env)
print( "v: ", v)
print( "w: ", w)

# Test wrapper for:
#    void py_dualmMob(double* v, double* out_w, struct fm_env* env)
Mob = [0.0,0.3,0.5,-0.2,0.4,0.1,-0.2,0.1]
w = pyw.dualmMob(Mob, env)
print( "Mob: ", Mob)
print( "w: ", w)

# Test wrapper for:
#    double py_Entropy(double* v, struct fm_env* env)
v = [0,0.3,0.5,0.6,0.4,0.8,0.7,1]
r = pyw.Entropy(v, env)
print( "v: ", v)
print( "r: ", r)

# Test wrapper for:
#    void py_FuzzyMeasureFit(int datanum, int additive, struct fm_env* env, double* out_v, double* dataset)
datanum = 10
additive = 2
res, dataset = pyw.FuzzyMeasureFit(datanum, additive, env, dataset = None)
print( "datanum: ", datanum)
print( "additive: ", additive)
print( "dataset: ", dataset)
print( "res: ", res)

# Test wrapper for:
#    void py_FuzzyMeasureFitMob(int datanum, int additive, struct fm_env* env, double* out_v, double* dataset)
datanum = 10
additive = 3
res, dataset = pyw.FuzzyMeasureFitMob(datanum, additive, env, dataset = None)
print( "datanum: ", datanum)
print( "additive: ", additive)
print( "dataset: ", dataset)
print( "res: ", res)

# Test wrapper for:
#    void py_FuzzyMeasureFitKtolerant(int datanum, int additive, struct fm_env* env, double* out_v, double* dataset)
datanum = 10
additive = 2
res, dataset = pyw.FuzzyMeasureFitKtolerant(datanum, additive, env, dataset = None)
print( "datanum: ", datanum)
print( "additive: ", additive)
print( "dataset: ", dataset)
print( "res: ", res)

# Test wrapper for:
#    void py_FuzzyMeasureFitLPKmaxitive(int datanum, int additive, struct fm_env* env, double* out_v, double* dataset)
datanum = 10
additive = 2
res, dataset = pyw.FuzzyMeasureFitLPKmaxitive(datanum, additive, env, dataset = None)
print( "datanum: ", datanum)
print( "additive: ", additive)
print( "dataset: ", dataset)
print( "res: ", res)

# Test wrapper for:
#    void py_FuzzyMeasureFitLPKinteractive(int datanum, int additive, struct fm_env* env, double* out_v, double* dataset, double* K)
datanum = 10
additive = 2
K = 0.5
v, dataset = pyw.FuzzyMeasureFitLPKinteractive(datanum, additive, env, K, dataset = None)
print( "datanum: ", datanum)
print( "additive: ", additive)
print( "K: ", K)
print( "dataset: ", dataset)
print( "v: ", v)


# Test wrapper for:
#    void py_FuzzyMeasureFitLPKinteractiveMaxChains(int datanum, int additive, struct fm_env* env, double* out_v, double* dataset, double* K)
datanum = 10
additive = 2
K = 0.5
v, dataset = pyw.FuzzyMeasureFitLPKinteractiveMaxChains(datanum, additive, env, K, dataset = None)
print( "datanum: ", datanum)
print( "additive: ", additive)
print( "K: ", K)
print( "dataset: ", dataset)
print( "v: ", v)

# Test wrapper for:
#    void py_FuzzyMeasureFitLPKinteractiveAutoK(int datanum, int additive, struct fm_env* env, double* out_v, double* dataset, double* K, int* maxiters)
datanum = 10
additive = 2
K = 0.5
maxiters = [100]
v, dataset = pyw.FuzzyMeasureFitLPKinteractiveAutoK(datanum, additive, env, K, maxiters, dataset = None)
print( "datanum: ", datanum)
print( "additive: ", additive)
print( "K: ", K)
print( "maxiters: ", maxiters)
print( "dataset: ", dataset)
print( "v: ", v)

# Test wrapper for:
#    void py_FuzzyMeasureFitLPKinteractiveMarginal(int datanum, int additive, struct fm_env* env, double* out_v, double* dataset, double* K, int submod)
datanum = 10
additive = 2
K = 0.5
submod = 1
v, dataset = pyw.FuzzyMeasureFitLPKinteractiveMarginal(datanum, additive, env,  K, submod, dataset = None)
print( "datanum: ", datanum)
print( "additive: ", additive)
print( "submod: ", submod)
print( "K: ", K)
print( "dataset: ", dataset)
print( "v: ", v)

# Test wrapper for:
#    void py_FuzzyMeasureFitLPKinteractiveMarginalMaxChain(int datanum, int additive, struct fm_env* env, double* out_v, double* dataset, double* K, int* maxiters, int submod)
datanum = 10
additive = 2
K = 0.5
submod = 1
v, dataset = pyw.FuzzyMeasureFitLPKinteractiveMarginalMaxChain(datanum, additive, env, K, maxiters, submod, dataset = None)
print( "datanum: ", datanum)
print( "additive: ", additive)
print( "submod: ", submod)
print( "K: ", K)
print( "dataset: ", dataset)
print( "v: ", v)

# Test wrapper for:
#    void py_FuzzyMeasureFitLP(int datanum, int additive, struct fm_env* env, double* out_v, double* dataset, int* options, double* indexlow, double* indexhihg, int* option1, double* orness)
datanum = 10
additive = 2
options = [0]
indexlow = [0, 0, 0]
indexhihg = [1, 1, 1]
option1 = [0]
orness = [0.5]
v, dataset = pyw.FuzzyMeasureFitLP(datanum, additive, env, options, indexlow, indexhihg, option1, orness, dataset = None)
print( "datanum: ", datanum)
print( "additive: ", additive)
print( "indexlow: ", indexlow)
print( "options: ", options)
print( "indexhihg: ", indexhihg)
print( "option1: ", option1)
print( "orness: ", orness)
print( "dataset: ", dataset)
print( "v: ", v)

# Test wrapper for:
#    void py_FuzzyMeasureFitLPMob(int datanum, int additive, struct fm_env* env, double* out_v, double* dataset, int* options, double* indexlow, double* indexhihg, int* option1, double* orness)
datanum = 10
additive = 2
options = [0]
indexlow = [0, 0, 0]
indexhihg = [1, 1, 1]
option1 = [0]
orness = [0.5]
Mob, dataset = pyw.FuzzyMeasureFitLPMob(datanum, additive, env, options, indexlow, indexhihg, option1, orness, dataset = None)
print( "datanum: ", datanum)
print( "additive: ", additive)
print( "indexlow: ", indexlow)
print( "options: ", options)
print( "indexhihg: ", indexhihg)
print( "option1: ", option1)
print( "orness: ", orness)
print( "dataset: ", dataset)
print( "Mob: ", Mob)

# Test wrapper for:
#    void py_fittingOWA(int datanum, struct fm_env* env, double* out_v, double* dataset)
# documented, no example
datanum = 10
v , dataset = pyw.fittingOWA(datanum, env, dataset = None)
print( "datanum: ", datanum)
print( "dataset: ", dataset)
print( "v: ", v)

# Test wrapper for:
#    void py_fittingWAM(int datanum, struct fm_env* env, double* out_v, double* dataset)
# documented, no example
datanum = 10
atanum = 10
v , dataset = pyw.fittingWAM(datanum, env, dataset = None)
print( "datanum: ", datanum)
print( "dataset: ", dataset)
print( "v: ", v)



pyw.fm_free( env)
n = 3
env = pyw.fm_init( n)

# Test wrapper for:
#    void py_Interaction(double* Mob, double* out_v, struct fm_env* env)
Mob = [0,0.3,0.5,0.6,0.4,0.8,0.7,1]
v = pyw.Interaction(Mob, env)
print( "Mob: ", Mob)
print( "v: ", v)

# Test wrapper for:
#    void py_InteractionB(double* Mob, double* out_v, struct fm_env* env)
Mob = [0,0.3,0.5,0.6,0.4,0.8,0.7,1]
v = pyw.InteractionB(Mob, env)
print( "Mob: ", Mob)
print( "v: ", v)

# Test wrapper for:
#    void py_InteractionMob(double* Mob, double* out_v, struct fm_env* env)
Mob = [0.0,0.3,0.5,-0.2,0.4,0.1,-0.2,0.1]
v = pyw.InteractionMob(Mob, env)
print( "Mob: ", Mob)
print( "v: ", v)

# Test wrapper for:
#    void py_InteractionBMob(double* Mob, double* out_v, struct fm_env* env)
Mob = [0.0,0.3,0.5,-0.2,0.4,0.1,-0.2,0.1]
v = pyw.InteractionBMob(Mob, env)
print( "Mob: ", Mob)
print( "v: ", v)


# Test wrapper for:
#    void py_BipartitionShapleyIndex(double* v, double* out_w, struct fm_env* env)
# not documented in R or Python user guide
v = [0.0, 0.3, 0.5, -0.2, 0.4, 0.1]
s = pyw.BipartitionShapleyIndex(v, env)
print( "v: ", v)
print( "s: ", s)

# Test wrapper for:
#    void py_BipartitionBanzhafIndex(double* v, double* out_w, struct fm_env* env)
# not documented in R or Python user guide
v = [0.0, 0.3, 0.5, -0.2, 0.4, 0.1]
s = pyw.BipartitionBanzhafIndex(v, env)
print( "v: ", v)
print( "s: ", s)

# Test wrapper for:
#    void py_BNonadditivityIndexMob(double* Mob, double* out_w, struct fm_env* env)
# not documented in R or Python user guide
Mob = [0.2, 0.3, 0.5, -0.2, 0.4, 0.1]
s = pyw.BNonadditivityIndexMob(Mob, env)
print( "v: ", v)
print( "s: ", s)

# Test wrapper for:
#    void py_NonadditivityIndex(double* v, double* out_w, struct fm_env* env)
v = [0,0.3,0.5,0.6,0.4,0.8,0.7,1]
w = pyw.NonadditivityIndex(v, env)
print( "v: ", v)
print( "w: ", w)

# Test wrapper for:
#    void py_NonmodularityIndex(double* v, double* out_w, struct fm_env* env)
v = [0,0.3,0.5,0.6,0.4,0.8,0.7,1]
w = pyw.NonmodularityIndex(v, env)
print( "v: ", v)
print( "w: ", w)

# Test wrapper for:
#    void py_NonmodularityIndexMob(double* Mob, double* out_w, struct fm_env* env)
v =[0.0, 0.3, 0.5, -0.2, 0.4, 0.1, -0.2, 0.1]
w = pyw.NonmodularityIndexMob(Mob, env)
print( "v: ", v)
print( "w: ", w)

# Test wrapper for:
#    void py_NonmodularityIndexMobkadditive(double* Mob, double* out_w, int k,  struct fm_env* env)
v =[0.0,0.3,0.5,-0.2,0.4,0.1,-0.2,0.1]
k = 2
w = pyw.NonmodularityIndexMobkadditive(Mob, k, env)
print( "v: ", v)
print( "k: ", k)
print( "w: ", w)

# Test wrapper for:
#    int py_IsMeasureBalanced(double* v, struct fm_env* env)
v = [0,0.3,0.5,0.6,0.4,0.8,0.7,1]
is_measure = pyw.IsMeasureBalanced(v, env)
print( "v: ", v)
print( "is_measure: ", is_measure)

# Test wrapper for:
#    int py_IsMeasureSelfdual(double* v, struct fm_env* env)
v = [0,0.3,0.5,0.6,0.4,0.8,0.7,1]
is_measure = pyw.IsMeasureSelfdual(v, env)
print( "v: ", v)
print( "is_measure: ", is_measure)

# Test wrapper for:
#    int py_IsMeasureSubadditive(double* v, struct fm_env* env)
v = [0.0, 0.3, 0.5, -0.2, 0.4, 0.1, -0.2, 0.1]
is_measure = pyw.IsMeasureSubadditive(v, env)
print( "v: ", v)
print( "is_measure: ", is_measure)

# Test wrapper for:
#    int py_IsMeasureSubmodular(double* v, struct fm_env* env)
v = [0.0, 0.3, 0.5, -0.2, 0.4, 0.1, -0.2, 0.1]
is_measure = pyw.IsMeasureSubmodular(v, env)
print( "v: ", v)
print( "is_measure: ", is_measure)

# Test wrapper for:
#    int py_IsMeasureSuperadditive(double* v, struct fm_env* env)
v = [0.0, 0.3, 0.5, -0.2, 0.4, 0.1, -0.2, 0.1]
is_measure = pyw.IsMeasureSuperadditive(v, env)
print( "v: ", v)
print( "is_measure: ", is_measure)

# Test wrapper for:
#    int py_IsMeasureSymmetric(double* v, struct fm_env* env)
v = [0.0, 0.3, 0.5, -0.2, 0.4, 0.1, -0.2, 0.1]
is_measure = pyw.IsMeasureSymmetric(v, env)

print( "v: ", v)
print( "is_measure: ", is_measure)

# Test wrapper for:
#    int py_IsMeasureKMaxitive(double* v, struct fm_env* env)
v = [0.0, 0.3, 0.5, -0.2, 0.4, 0.1, -0.2, 0.1]
is_measure = pyw.IsMeasureKMaxitive(v, env)
print( "v: ", v)
print( "is_measure: ", is_measure)

# Test wrapper for:
#    int py_IsMeasureAdditiveMob(double* Mob, struct fm_env* env)
Mob = [0.0,0.3,0.5,-0.2,0.4,0.1,-0.2,0.1]
is_measure = pyw.IsMeasureAdditiveMob(Mob, env)
print( "v: ", v)
print( "is_measure: ", is_measure)

# Test wrapper for:
#    int py_IsMeasureBalancedMob(double* Mob, struct fm_env* env)
Mob = [0.0,0.3,0.5,-0.2,0.4,0.1,-0.2,0.1]
is_measure = pyw.IsMeasureBalancedMob(Mob, env)
print( "v: ", v)
print( "is_measure: ", is_measure)


# Test wrapper for:
#    int py_IsMeasureSelfdualMob(double* Mob, struct fm_env* env)
Mob = [0.0,0.3,0.5,-0.2,0.4,0.1,-0.2,0.1]
is_measure = pyw.IsMeasureSelfdualMob(Mob, env)
print( "v: ", v)
print( "is_measure: ", is_measure)

# Test wrapper for:
#    int py_IsMeasureSubadditiveMob(double* Mob, struct fm_env* env)
Mob = [0.0,0.3,0.5,-0.2,0.4,0.1,-0.2,0.1]
is_measure = pyw.IsMeasureSubadditiveMob(Mob, env)
print( "v: ", v)
print( "is_measure: ", is_measure)

# Test wrapper for:
#    int py_IsMeasureSubmodularMob(double* Mob, struct fm_env* env)
Mob = [0.0,0.3,0.5,-0.2,0.4,0.1,-0.2,0.1]
is_measure = pyw.IsMeasureSubmodularMob(Mob, env)
print( "v: ", v)
print( "is_measure: ", is_measure)

# Test wrapper for:
#    int py_IsMeasureSuperadditiveMob(double* Mob, struct fm_env* env)
Mob = [0.0,0.3,0.5,-0.2,0.4,0.1,-0.2,0.1]
is_measure = pyw.IsMeasureSuperadditiveMob(Mob, env)
print( "v: ", v)
print( "is_measure: ", is_measure)

# Test wrapper for:
#    int py_IsMeasureSupermodularMob(double* Mob, struct fm_env* env)
Mob = [0.0,0.3,0.5,-0.2,0.4,0.1,-0.2,0.1]
is_measure = pyw.IsMeasureSupermodularMob(Mob, env)
print( "v: ", v)
print( "is_measure: ", is_measure)

# Test wrapper for:
#    int py_IsMeasureSymmetricMob(double* Mob, struct fm_env* env)
Mob = [0.0,0.3,0.5,-0.2,0.4,0.1,-0.2,0.1]
is_measure = pyw.IsMeasureSymmetricMob(Mob, env)
print( "v: ", v)
print( "is_measure: ", is_measure)

# Test wrapper for:
#    int py_IsMeasureKMaxitiveMob(double* Mob, struct fm_env* env)
Mob = [0.0,0.3,0.5,-0.2,0.4,0.1,-0.2,0.1]
is_measure = pyw.IsMeasureKMaxitiveMob(Mob, env)
print( "v: ", v)
print( "is_measure: ", is_measure)

# Test wrapper for:
#    void py_Mobius(double* v, double* out_MobVal, struct fm_env* env)
v = [0,0.3,0.5,0.6,0.4,0.8,0.7,1]
Mob = pyw.Mobius(v, env)
print( "v: ", v)
print( "Mob: ", Mob)

# Test wrapper for:
#    double py_OWA(double* x, double* v, struct fm_env* env)
# not documented in R or Python user guide
x = [0.3, 0.4, 0.8, 0.2]   # inputs
w = [0.4, 0.35 ,0.2 ,0.05] # OWA weights
res = pyw.OWA(x, v, env)
print( "v: ", v)
print( "w: ", w)
print( "res: ", res)

# Test wrapper for:
#    double py_WAM(double* x, double* v, struct fm_env* env)
# not documented in R or Python user guide
x = [0.3, 0.4, 0.8, 0.2]   # inputs
w = [0.4, 0.35 ,0.2 ,0.05] # OWA weights
res = pyw.WAM(x, v, env)
print( "v: ", v)
print( "w: ", w)
print( "res: ", res)

# Test wrapper for:
#    void py_Zeta(double* Mob, double* out_v, struct fm_env* env)
Mob = [0.0,0.3,0.5,-0.2,0.4,0.1,-0.2,0.1]
v = pyw.Zeta(Mob, env)
print( "Mob: ", Mob)
print( "v: ", v)

# Test wrapper for:
#    void py_dualMobKadd(int k, double* src, double* out_dest, struct fm_env* env)
Mob = [0.0,0.3,0.5,-0.2,0.4,0.1,-0.2,0.1]
kadd = 2
dual, length = pyw.dualMobKadd(kadd, Mob, env)
print( "Mob: ", Mob)
print( "kadd: ", kadd)
print( "length of output: ", length)
print( "dual: ", dual)

# Test wrapper for:
#    void py_Shapley2addMob(double* v, double* out_x, int n)
v = [0.0, 0.3, 0.5, -0.2, 0.4, 0.1]
n = len( v)
shapley = pyw.Shapley2addMob( v, n)
print( "v: ", v)
print( "n: ", n)
print( "shapley: ", shapley)

# Test wrapper for:
#    void py_Banzhaf2addMob(double* v, double* out_x, int n)
v = [0.0, 0.3, 0.5, -0.2, 0.4, 0.1]
n = len(v)
banzhaf = pyw.Banzhaf2addMob(v, n)
print( "v: ", v)
print( "n: ", n)
print( "banzhaf: ", banzhaf)

# Test wrapper for:
#    double py_Choquet2addMob(double* x, double* Mob, int n)
x =[0.2,0.5,0.4]
Mob = [0.2, 0.3, 0.5, -0.2, 0.4, 0.1]
n = len( Mob)
ci = pyw.Choquet2addMob(x, Mob, n)
print( "x: ", x)
print( "Mob: ", Mob)
print( "CI: ", ci)

# Test wrapper for:
#    int py_fm_arraysize(int n, int kint, struct fm_env* env)
kint = 2
n = env.n
l = pyw.fm_arraysize(n, kint, env)
print( "kint: ", kint)
print( "n: ", n)
print( "length: ", l)

# Test wrapper for:
#    int py_generate_fm_minplus(int num, int n, int kint, int markov, int option, double K, double* out_vv, struct fm_env* env)
# pyw.generate_fm_minplus(num, n, kint, markov, option, K, out_vv, env)
# not documented in R or Python user guide
num = 10
n = 6
kint = 3
markov = 1000
option = 0
K = 0.7
ret_code = 0
length = 0
vv = []
ret_code, vv, length = pyw.generate_fm_minplus(num, n, kint, markov, option, K, env)
print( "num: ", num)
print( "n: ", n)
print( "kint: ", kint)
print( "markov: ", markov)
print( "option: ", option)
print( "K: ", K)
print( "ret_code: ", ret_code)
print( "length of output: ", length)
print( "vv: ", vv)

# Test wrapper for:
#    int py_generate_fm_2additive_convex(int num, int n,  double* out_vv)
# not documented in R or Python user guide
num = 10
n = 6
ret_code = 0
length = 0
ret_code, vv, length = pyw.generate_fm_2additive_convex(num, n)
print( "num: ", num)
print( "n: ", n)
print( "ret_code: ", ret_code)
print( "length of output: ", length)
print( "vv: ", vv)

# Test wrapper for:
#    int py_generate_fm_2additive_convex_withsomeindependent(int num, int n, double* out_vv)
# 
# not documented in R or Python user guide
num = 10
n = 6
ret_code = 0
length = 0
ret_code, vv, length = pyw.generate_fm_2additive_convex_withsomeindependent(num, n)
print( "num: ", num)
print( "n: ", n)
print( "ret_code: ", ret_code)
print( "length of output: ", length)
print( "vv: ", vv)

pyw.fm_free( env);
n = 3
env = pyw.fm_init( n)

#
# Here the testing for env_sparse starts
# 

# Test wrapper for:
#    void py_prepare_fm_sparse(int n, int tupsize, int* tuples, struct fm_env_sparse* out_env)
n = 3
tupsize = 0
env_sparse = pyw.prepare_fm_sparse( n, tupsize)

# Test wrapper for:
#    void py_add_tuple_sparse(int tupsize, int* tuple, double v, struct fm_env_sparse* env)
v = 0.2
tuple = [1, 3, 4]
pyw.add_tuple_sparse( tuple, v, env_sparse)
print( "tuple: ", tuple)

# Test wrapper for:
#    void py_ShapleyMob_sparse(double* out_v, int n, struct fm_env_sparse* env)
n = 3
v = pyw.ShapleyMob_sparse(n, env_sparse)
print( "n: ", n)
print( "Shapley values: ", v)

# Test wrapper for:
#    void py_BanzhafMob_sparse(double* out_v, int n, struct fm_env_sparse* env)
n = 3
v = pyw.BanzhafMob_sparse(n, env_sparse)
print( "n: ", n)
print( "Banzhaf values: ", v)

# Test wrapper for:
#    void py_add_pair_sparse(int i, int j, double v, struct fm_env_sparse* env)
v = 0.2
i = 2
j = 5
pyw.add_pair_sparse(i, j, v, env_sparse)
print( "v: ", v)
print( "i: ", i)
print( "j: ", j)


# Test wrapper for:
#    void py_populate_fm_2add_sparse_from2add(int n, double* v, struct fm_env_sparse* env)
# n = 3
# v = pyw.populate_fm_2add_sparse_from2add(n, v, env)


# Test wrapper for:
#    void py_populate_fm_2add_sparse(double* singletons, int numpairs, double* pairs, int* indicesp1, int* indicesp2, struct fm_env_sparse* env)
# pyw.populate_fm_2add_sparse(singletons, numpairs, pairs, indicesp1, indicesp2, env)



# Test wrapper for:
#    env)void py_expand_2add_full(double* v, struct fm_env_sparse* env)
# pyw.expand_2add_full(v, env)


# Test wrapper for:
#    int py_sparse_get_pairs(int* pairs, double* v, struct fm_env_sparse* env)
# pyw.sparse_get_pairs(pairs, v, env)

# Test wrapper for:
#    int py_sparse_get_tuples(int* tuples, double* v, struct fm_env_sparse* env)
# pyw.sparse_get_tuples(tuples, v, env)

# Test wrapper for:
#    int   py_generate_fm_2additive_convex_sparse(int n, struct fm_env_sparse* env)
# pyw.generate_fm_2additive_convex_sparse(n, env)

# Test wrapper for:
#    int   py_generate_fm_kadditive_convex_sparse(int n, int k, int nonzero, struct fm_env_sparse* env)
# pyw.generate_fm_kadditive_convex_sparse(n, k, nonzero, env)

# Test wrapper for:
#    void py_Nonmodularityindex_sparse(double* out_w, int n, struct fm_env_sparse* env)
n =3
w = pyw.Nonmodularityindex_sparse(n, env_sparse)
print( "n: ", n)
print( "w: ", w)

# Test wrapper for:
#    int py_tuple_cardinality_sparse(int i, struct fm_env_sparse* env)
i = 0;
tup_card = pyw.tuple_cardinality_sparse(i, env_sparse)
print( "i: ", i)
print( "tup_card: ", tup_card)

# Test wrapper for:
#    int py_get_num_tuples(struct fm_env_sparse* env)
num_tup = pyw.get_num_tuples(env_sparse)
print( "num_tup: ", num_tup)

# Test wrapper for:
#    int py_get_sizearray_tuples(struct fm_env_sparse* env)
length = pyw.get_sizearray_tuples(env_sparse)
print( "length of array of tuples: ", length)

# Test wrapper for:
#    int py_is_inset_sparse(int A, int card, int i, struct fm_env_sparse* env)
A = 0
card = 3
i = 1
is_contained = pyw.is_inset_sparse(A, card, i, env_sparse)
print( "A: ", A)
print( "card: ", card)
print( "i: ", i)
print( "is_contained: ", is_contained)

# Test wrapper for:
#    int py_is_subset_sparse(int A, int cardA, int B, int cardB, struct fm_env_sparse* env)
A = 0
cardA = 3
B = 1
cardB = 3
is_subset = pyw.is_subset_sparse(A, cardA, B, cardB, env_sparse)
print( "A: ", A)
print( "cardA: ", cardA)
print( "B: ", B)
print( "cardB: ", cardB)
print( "is_subset: ", is_subset)

# Test wrapper for:
#    double py_min_subset_sparse(double* x, int n, int S, int cardS, struct fm_env_sparse* env)
# pyw.min_subset_sparse(x, n, S, cardS, env_sparse)

# Test wrapper for:
#    double py_max_subset_sparse(double* x, int n, int S, int cardS, struct fm_env_sparse* env)
# pyw.max_subset_sparse(x, n, S, cardS, env_sparse)


# Test wrapper for:
#    double py_ChoquetMob_sparse(double* x, int n, struct fm_env_sparse* env)
x = [0.1,0.05,0.2]
c_i = pyw.ChoquetMob_sparse(x, env_sparse)
print( "x: ", x)
print( "Choquet integral: ", c_i)

# Test wrapper for:
#    void py_free_fm_sparse( struct fm_env_sparse* env)
pyw.free_fm_sparse( env_sparse)

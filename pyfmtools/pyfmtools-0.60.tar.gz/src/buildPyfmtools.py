from cffi import FFI
import os

ffibuilder = FFI()
PATH = os.path.dirname(__file__)

ffibuilder.cdef(r"""
    typedef unsigned long long int_64;
    struct  fm_env {
	int n;
	int m;
	int* card;
	int* cardpos;
	double* bit2card;
	double* card2bit;
	double* factorials;};
    struct  fm_env_sparse { 
	int xx[40];};
    double py_min_subset(double* x, int n, int_64 S);
    double py_max_subset(double* x, int n, int_64 S);
    void py_ConvertCard2Bit(double* dest, double* src,  struct fm_env* env);
    double py_min_subsetC(double* x, int n, int_64 S, struct fm_env* env);
    double py_max_subsetNegC(double* x, int n, int_64 S, struct fm_env* env);
    int py_SizeArraykinteractive(int n, int k, struct fm_env* env);
    int py_IsSubsetC(int i, int j, struct fm_env* env); 
    int py_IsElementC(int i, int j, struct fm_env* env); 
    void py_ExpandKinteractive2Bit(double* dest, double* src, struct fm_env* env, int kint, int arraysize);
	void py_ExpandKinteractive2Bit_m(double* dest, double* src, struct fm_env* env, int kint, int arraysize, double* VVC);
    void py_fm_init(int n, struct  fm_env* env);
    void py_fm_free(struct  fm_env* env);
    void py_Shapley(double* v, double* x, struct fm_env* env);
    void py_Banzhaf(double* v, double* B, struct fm_env* env);
    void py_ShapleyMob(double* Mob, double* x, struct fm_env* env);
    void py_BanzhafMob(double* Mob, double* B, struct fm_env* env);
    double py_Choquet(double* x, double* v, struct fm_env* env);
    double py_ChoquetKinter(double* x, double* v, int kint, struct fm_env* env);
    double py_ChoquetMob(double* x, double* Mob, struct fm_env* env);
    void py_ConstructLambdaMeasure(double* singletons, double* lambda, double* v, struct fm_env* env);
    void py_ConstructLambdaMeasureMob(double* singletons, double* lambda, double* Mob, struct fm_env* env);
    void py_dualm(double* v, double* w, struct fm_env* env);
    void py_dualmMob(double* v, double* w, struct fm_env* env);
    double py_Entropy(double* v, struct fm_env* env);
    void py_FuzzyMeasureFit(int datanum, int additive, struct fm_env* env, double* v, double* dataset);
    void py_FuzzyMeasureFitMob(int datanum, int additive, struct fm_env* env, double* v, double* dataset);
    void py_FuzzyMeasureFitKtolerant(int datanum, int additive, struct fm_env* env, double* v, double* dataset);
    void py_FuzzyMeasureFitLPKmaxitive(int datanum, int additive, struct fm_env* env, double* v, double* dataset);
    void py_FuzzyMeasureFitLPKinteractive(int datanum, int additive, struct fm_env* env, double* v, double* dataset, double* K);
    void py_FuzzyMeasureFitLPKinteractiveMaxChains(int datanum, int additive, struct fm_env* env, double* v, double* dataset, double* K);
    void py_FuzzyMeasureFitLPKinteractiveAutoK(int datanum, int additive, struct fm_env* env, double* v, double* dataset, double* K, int* maxiters);
    void py_FuzzyMeasureFitLPKinteractiveMarginal(int datanum, int additive, struct fm_env* env, double* v, double* dataset, double* K, int submod);
    void py_FuzzyMeasureFitLPKinteractiveMarginalMaxChain(int datanum, int additive, struct fm_env* env, double* v, double* dataset, double* K, int* maxiters, int submod);
    void py_FuzzyMeasureFitLP(int datanum, int additive, struct fm_env* env, double* v, double* dataset, int * options, double* indexlow, double* indexhihg, int* option1, double* orness);
    void py_FuzzyMeasureFitLPMob(int datanum, int additive, struct fm_env* env, double* v, double* dataset, int * options, double* indexlow, double* indexhihg, int* option1, double* orness);
    void py_fittingOWA(int datanum, struct fm_env* env, double* v, double* dataset);
    void py_fittingWAM(int datanum, struct fm_env* env, double* v, double* dataset);
    void py_Interaction(double* Mob, double* v, struct fm_env* env);
    void py_InteractionB(double* Mob, double* v, struct fm_env* env);
    void py_InteractionMob(double* Mob, double* v, struct fm_env* env);
    void py_InteractionBMob(double* Mob, double* v, struct fm_env* env);
    void py_BipartitionShapleyIndex(double* v, double* w, struct fm_env* env);
    void py_BipartitionBanzhafIndex(double* v, double* w, struct fm_env* env);
    void py_BNonadditivityIndexMob(double* Mob, double* w, struct fm_env* env);
    void py_NonadditivityIndex(double* v, double* w, struct fm_env* env);
	void py_NonmodularityIndex(double* v, double* w, struct fm_env* env);
	void py_NonmodularityIndexMob(double* Mob, double* w, struct fm_env* env);	
	void py_NonmodularityIndexKinteractive(double* v, double* w, int kint,  struct fm_env* env);
    void py_NonmodularityIndexMobkadditive(double* Mob, double* w, int k,  struct fm_env* env);
   	void py_ShowCoalitions(int* coalition, struct fm_env* env);
	void py_ShowCoalitionsCard(int* coalition, struct fm_env* env);
    int py_IsMeasureAdditive(double* v, struct fm_env* env);
    int py_IsMeasureBalanced(double* v, struct fm_env* env);
    int py_IsMeasureSelfdual(double* v, struct fm_env* env);
    int py_IsMeasureSubadditive(double* v, struct fm_env* env);
    int py_IsMeasureSubmodular(double* v, struct fm_env* env);
    int py_IsMeasureSuperadditive(double* v, struct fm_env* env);
    int py_IsMeasureSupermodular(double* v, struct fm_env* env);
    int py_IsMeasureSymmetric(double* v, struct fm_env* env);
    int py_IsMeasureKMaxitive(double* v, struct fm_env* env);
	int py_IsMeasureAdditiveMob(double* Mob, struct fm_env* env); 
	int py_IsMeasureBalancedMob(double* Mob, struct fm_env* env); 
	int py_IsMeasureSelfdualMob(double* Mob, struct fm_env* env); 
	int py_IsMeasureSubadditiveMob(double* Mob, struct fm_env* env);
	int py_IsMeasureSubmodularMob(double* Mob, struct fm_env* env); 
	int py_IsMeasureSuperadditiveMob(double* Mob, struct fm_env* env);
	int py_IsMeasureSupermodularMob(double* Mob, struct fm_env* env); 
	int py_IsMeasureSymmetricMob(double* Mob, struct fm_env* env);
	int py_IsMeasureKMaxitiveMob(double* Mob, struct fm_env* env);
    void py_Mobius(double* v, double* MobVal, struct fm_env* env);
    double py_Orness(double* Mob, struct fm_env* env);
    double py_OWA(double* x, double* v, struct fm_env* env);
    double py_Sugeno(double* x, double* v, struct fm_env* env);
    double py_WAM(double* x, double* v, struct fm_env* env);
    void py_Zeta(double* Mob, double* v, struct fm_env* env);
	void py_dualMobKadd(int m, int length, int k, double* src, double* dest, struct fm_env* env);
	void py_Shapley2addMob(double* v, double* x, int n);
	void py_Banzhaf2addMob(double* v, double* x, int n);
    double py_Choquet2addMob(double*x, double* Mob, int n);
	int py_fm_arraysize(int n, int kint, struct fm_env* env);
	int py_generate_fm_tsort(int num, int n, int kint, int markov, int option, double K, double * vv, struct fm_env* env);
	int py_generate_fmconvex_tsort(int num, int n, int kint, int markov, int option, double K, double * vv, struct fm_env* env);
	int py_generate_fm_minplus(int num, int n, int kint, int markov, int option, double K, double * vv, struct fm_env* env);
	int py_generate_fm_2additive_convex(int num, int n,  double * vv);
	int py_generate_fm_2additive_concave(int num, int n, double * vv);
    int py_generate_fm_2additive_convex_withsomeindependent(int num, int n, double * vv);
    void py_export_maximal_chains(int n, double* v, double* mc, struct fm_env* env);
    void py_prepare_fm_sparse(int n, int tupsize, int* tuples, struct fm_env_sparse* env);
    void py_free_fm_sparse( struct fm_env_sparse* env);
    int py_tuple_cardinality_sparse(int i, struct fm_env_sparse* env);
    int py_get_num_tuples(struct fm_env_sparse* env);
	int py_get_sizearray_tuples(struct fm_env_sparse* env);
    int py_is_inset_sparse(int A, int card, int i, struct fm_env_sparse* env);
    int py_is_subset_sparse(int A, int cardA, int B, int cardB, struct fm_env_sparse* env);
    double py_min_subset_sparse(double* x, int n, int S, int cardS, struct fm_env_sparse* env);
	double py_max_subset_sparse(double* x, int n, int S, int cardS, struct fm_env_sparse* env);
    double py_ChoquetMob_sparse(double* x, int n, struct fm_env_sparse* env);
    void py_ShapleyMob_sparse(double* v, int n, struct fm_env_sparse* env);
	void py_BanzhafMob_sparse(double* v, int n, struct fm_env_sparse* env);
    void py_populate_fm_2add_sparse(double* singletons, int numpairs, double* pairs, int* indicesp1, int* indicesp2, struct fm_env_sparse* env);
    void py_add_pair_sparse(int i, int j, double v, struct fm_env_sparse* env);
    void py_add_tuple_sparse(int tupsize, int* tuple, double v, struct fm_env_sparse* env);
    void py_populate_fm_2add_sparse_from2add(int n, double * v, struct fm_env_sparse* env);
    void py_expand_2add_full(double* v, struct fm_env_sparse* env);
    void py_expand_sparse_full(double* v, struct fm_env_sparse* env);
	void py_sparse_get_singletons(int n, double* v, struct fm_env_sparse* env);
	int py_sparse_get_pairs(int* pairs, double* v, struct fm_env_sparse* env);
	int py_sparse_get_tuples(int* tuples, double* v, struct fm_env_sparse* env);
    int   py_generate_fm_2additive_convex_sparse(int n, struct fm_env_sparse* env);
    int   py_generate_fm_kadditive_convex_sparse(int n, int k, int nonzero, struct fm_env_sparse* env);
    void py_Nonmodularityindex_sparse(double* w, int n, struct fm_env_sparse* env);
    """, override=True)

pyfmtools_src=['src/colamd.c','src/lp_lib.c','src/lp_params.c','src/lp_simplex.c','src/lusolio.c','src/commonlib.c','src/lp_LUSOL.c','src/lp_presolve.c','src/lpslink56.c','src/mmio.c',
	'src/ini.c','src/lp_matrix.c','src/lp_price.c','src/lp_SOS.c','src/myblas.c','src/isfixedvar.c','src/lp_MDO.c','src/lp_pricePSE.c','src/lp_utils.c','src/sparselib.c',
	'src/lp_crash.c','src/lp_mipbb.c','src/lp_report.c','src/lp_wlp.c','src/yacc_read.c','src/lp_Hash.c','src/lp_MPS.c','src/lp_scale.c','src/lusol.c',
	'src/fmrandom.cpp','src/fuzzymeasurefit.cpp','src/wrapperpy.cpp','src/fuzzymeasurefit3.cpp','src/fuzzymeasuretools.cpp']

ffibuilder.set_source("_pyfmtools",r""" #include "wrapperpy.h" """,  
    sources=pyfmtools_src,
    include_dirs=[PATH],
    )
    

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)

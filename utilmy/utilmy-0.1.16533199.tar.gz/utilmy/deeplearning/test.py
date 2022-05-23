import utilmy.deeplearning.util_embedding

try:
    from utilmy.deeplearning.util_embedding import embedding_load_word2vec
except NameError:
    def dummy_embedding_load_word2vec(dirin="df.parquet", nmax = 500):
        n_points = 100
        mdim = 200
        embs = np.random.random((n_points,mdim))
        embs = embs/np.linalg.norm(embs,p=2,axis=-1)       
        id_map = { f'point_{i}':i for i in range(n_pts)}
        df = None
        return embs, id_map, df 

    utilmy.deeplearning.util_embedding.embedding_load_word2vec = dummy_embedding_load_word2vec

from utilmy.deeplearning.util_embedding import vizEmbedding

myviz = vizEmbedding(path = "./model.vec")
myviz.run_all(nmax=5000)

myviz.dim_reduction(mode='mds')
myviz.create_visualization(dir_out="ztmp/vis/")        


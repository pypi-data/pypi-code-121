#from .feature.pdb2graph import pdb2graph
class feature_combine:
    def __init__(self,a_features, b_features,seqs):
        self.features = {
                "AC":ac.ac().AC,
                "DPC":dpc.dpc().DPC,
                "CT":ct.ct().CT,
                "CKSAAP":cksaap.cksaap().CKSAAP,
                "esm_mean":esm.esm().ESM_MEAN,
                "node2vec":node2vec.node2vec().NODE2VEC
                }
        self.feature_shape = {
                "AC":210,
                "DPC":400,
                "CT":343,
                "CKSAAP":1600,
                "esm_mean":1280,
                "node2vec":128
                }
        self.seqs = seqs
        self.a_features = a_features
        self.b_features = b_features

    def encode(self,ppis):
        x = []
        for a,b in ppis:
            temp_a = []
            temp_b = []
            for feature in self.a_features:
                if feature == "esm_mean" or feature == "node2vec":
                    temp_a.append(self.features[feature](a))
                else:
                    temp_a.append(self.features[feature](self.seqs[a]))
            
            for feature in self.b_features:
                if feature == "esm_mean" or feature == "node2vec":
                    temp_b.append(self.features[feature](b))
                else:
                    temp_b.append(self.features[feature](self.seqs[b]))
            temp_a = np.hstack(temp_a)
            temp_b = np.hstack(temp_b)
            x.append(np.hstack((temp_a,temp_b)))
        return np.array(x)




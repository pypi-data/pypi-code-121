from .metalogic import logic_variable


number_of_features = logic_variable("number_of_features")
number_of_samples = logic_variable("number_of_samples")#test+train
categorical = logic_variable("categorical")
numeric = logic_variable("numeric")
nominal = logic_variable("nominal")
name = logic_variable("name")
textual = logic_variable("textual")
twodim = logic_variable("twodim")
threedim = logic_variable("threedim")
image_data = logic_variable("image_data")
image_based = logic_variable("image_based")#no longer an image, but derived from an image
linearly_separable = logic_variable("linearly_separable")
easy_to_separate = logic_variable("easy_to_separate")#in tests most algorithms achieve auc>0.9
hard_to_separate = logic_variable("hard_to_separate")#in tests no algorithm achieves auc>0.9
number_anomalies = logic_variable("number_anomalies")
number_normals = logic_variable("number_normals")
index = logic_variable("index")
fraction_anomalies = logic_variable("fraction_anomalies")#number_anomalies/number_of_samples
quantconst = logic_variable("quantconst")#min options of feature over the numerical features. Only defined if twodim==True
quantmedian = logic_variable("quantmedian")#median options of feature over the numerical features. Only defined if twodim==True
quantisation = logic_variable("quantisation")#quantconst/numberof_samples<0.2

logical_false = logic_variable("logical_false")
logical_true = ~logical_false


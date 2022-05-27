from monai.transforms import ( Activations
                             , AsDiscrete
                             , Compose
                             )

def postprocessing(list_postprocessing):
    post_trans = []
    for count, step in enumerate(list_postprocessing):
        if list(step.keys())[0] == "Activation":
            if list_postprocessing[count]["Activation"] == "Sigmoid":
                activation = Activations(sigmoid = True)
                post_trans.append(activation)
            if list_postprocessing[count]["Activation"] == "Softmax":
                activation = Activations(softmax = True)
                post_trans.append(activation)
        if list(step.keys())[0] == "Threshold":
            threshold_op = AsDiscrete( threshold_values = True
                                     , logit_thresh = list_postprocessing[count]["Threshold"]
                                     )
            post_trans.append(threshold_op)
    post_trans_new = Compose(post_trans)
    return post_trans_new, post_trans

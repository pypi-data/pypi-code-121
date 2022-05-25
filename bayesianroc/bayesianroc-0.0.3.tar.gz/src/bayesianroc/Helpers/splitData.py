
def getTwoSplitters(splitterType, folds, repeats):
    split_random_state = 19
    if   splitterType == 'KFold':
        from sklearn.model_selection import KFold
        kf  = KFold(n_splits=folds, random_state=split_random_state,   shuffle=True)
        kf2 = KFold(n_splits=folds, random_state=split_random_state+1, shuffle=True)
        total_folds = folds
    elif splitterType == 'RepeatedKFold':
        from sklearn.model_selection import RepeatedKFold
        # shuffle=True is automatic and is not an option to specify
        kf  = RepeatedKFold(n_splits=folds, n_repeats=repeats, random_state=split_random_state)
        kf2 = RepeatedKFold(n_splits=folds, n_repeats=repeats, random_state=split_random_state+1)
        total_folds = folds * repeats
    elif splitterType == 'StratifiedKFold':
        from sklearn.model_selection import StratifiedKFold
        kf  = StratifiedKFold(n_splits=folds, random_state=split_random_state,   shuffle=True)
        kf2 = StratifiedKFold(n_splits=folds, random_state=split_random_state+1, shuffle=True)
        total_folds = folds
    elif splitterType == 'RepeatedStratifiedKFold':
        from sklearn.model_selection import RepeatedStratifiedKFold
        # shuffle=True is automatic and is not an option to specify
        kf  = RepeatedStratifiedKFold(n_splits=folds, n_repeats=repeats, random_state=split_random_state)
        kf2 = RepeatedStratifiedKFold(n_splits=folds, n_repeats=repeats, random_state=split_random_state+1)
        total_folds = folds * repeats
    else:
        ValueError('splitterType not recognized')
    #endif
    return total_folds, kf, kf2
#enddef

def getTrainAndValidationFoldData(X_deriv_df, y_deriv_s, splitterType, folds, repeats):
    ''' Gets fold data for training and validation and ensures both classes are present 
        and does not allow any validation fold to have only one class. To enforce both
        classes, a main and backup splitter are used, where the latter splitter is used if
        the requirement is not met by a fold in the main splitter.
        
        splitterType = {'KFold', 'RepeatedKFold', 'StratifiedKFold', 'RepeatedStratifiedKFold'}
    ''' 
    import numpy as np

    print(f'Making training/validation sets with {splitterType} cross validation.')
    total_folds, kf, kf2 = getTwoSplitters(splitterType, folds, repeats)
    
    X_train_df  = [None] * total_folds
    y_train_s   = [None] * total_folds
    X_cv_df     = [None] * total_folds
    y_cv_s      = [None] * total_folds

    # fix undocumented bug in sklearn's StratifiedKFold: include dummy_y in call to split
    dummy_y = np.zeros(X_deriv_df.shape[0])

    i = 0  # index
    j = 0  # backup batch index
    for train_index, val_index in kf.split(X_deriv_df, dummy_y):
        # if the validation set has more than one class, then things are normal
        if len(np.unique(y_deriv_s.iloc[val_index])) > 1:
            X_train_df[i] = X_deriv_df.iloc[train_index]
            y_train_s[i]  = y_deriv_s.iloc[train_index]
            X_cv_df[i]    = X_deriv_df.iloc[val_index]
            y_cv_s[i]     = y_deriv_s.iloc[val_index]
            i = i + 1
        else:
            # the validation set only had one class, so let's get indices
            # from the backup batch we hope are better, starting at index j==0 (to avoid reuse/duplication)
            k = 0
            for train_index2, val_index2 in kf2.split(X_deriv_df, dummy_y):
                if k < j:  # if not at starting index j, then loop to get there
                    k = k + 1
                    continue
                else:
                    # if the validation set has more than one class
                    if len(np.unique(y_deriv_s.iloc[val_index2])) > 1:
                        X_train_df[i] = X_deriv_df.iloc[train_index2]
                        y_train_s[i]  = y_deriv_s.iloc[train_index2]
                        X_cv_df[i]    = X_deriv_df.iloc[val_index2]
                        y_cv_s[i]     = y_deriv_s.iloc[val_index2]
                        i = i + 1
                        j = j + 1
                        break
                    else:
                        continue
                    #endif
                #endif
            #endfor
        #endif
    #endfor
    return total_folds, X_train_df, y_train_s, X_cv_df, y_cv_s
#enddef

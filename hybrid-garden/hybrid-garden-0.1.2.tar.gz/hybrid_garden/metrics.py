def get_model_scoring_metrics(task='regression', binary=False, template='minimum'):
    if template == 'minimum':
        scoring = {'regression': ['neg_mean_absolute_error',
            'neg_mean_squared_error',            
            'neg_mean_absolute_percentage_error',
            ],
            'binary': [
            'roc_auc',
            'recall',
            'precision',
            ],
            'classification': [
                'roc_auc_ovo',
                'precision_weighted',
                'recall_weighted',
            ]}

    else:
        scoring = {'regression': [
            'explained_variance',
            'r2',
            'max_error',
            'neg_median_absolute_error',
            'neg_mean_absolute_error',
            'neg_mean_absolute_percentage_error',
            'neg_mean_squared_error',
            'neg_mean_squared_log_error',
            'neg_root_mean_squared_error',
            'neg_mean_poisson_deviance',
            'neg_mean_gamma_deviance',
            ],
            
        'binary': [
            #for classification
            'average_precision',
            'balanced_accuracy',
            'accuracy',
            'top_k_accuracy',
            #for binary
            'jaccard',
            'roc_auc',
            'f1',
            'recall',
            'precision',
            ],
        'classification': [
            #for mylticlass
            'precision_macro',
            'precision_micro',
            'precision_samples',
            'precision_weighted',
            'recall_macro',
            'recall_micro',
            'recall_samples',
            'recall_weighted',
            'f1_macro',
            'f1_micro',
            'f1_samples',
            'f1_weighted',
            'jaccard_macro',
            'jaccard_micro',
            'jaccard_samples',
            'jaccard_weighted',
            'roc_auc_ovr',
            'roc_auc_ovo',
            'roc_auc_ovr_weighted',
            'roc_auc_ovo_weighted',
            #for classification
            'average_precision',
            'balanced_accuracy',
            'accuracy',
            'top_k_accuracy'        
            ]
            }
    if task == 'classification' and binary:
        return scoring['binary']
    return scoring[task]
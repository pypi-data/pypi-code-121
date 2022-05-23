from imblearn.combine import (
    SMOTEENN, SMOTETomek,
)
from imblearn.over_sampling import (
    SMOTE, ADASYN, BorderlineSMOTE,
)
from imblearn.under_sampling import (
    ClusterCentroids,
    NearMiss,
    RandomUnderSampler,
    EditedNearestNeighbours,
    AllKNN,
    TomekLinks,
    OneSidedSelection,
    CondensedNearestNeighbour,
    NeighbourhoodCleaningRule,
)

from kolibri.samplers.auto_smpler import AutoSampler


def get_sampler(sampler, random_state=None):
    '''
    sampler: String
        The method used to perform re-sampling
        currently support: ['RUS', 'CNN', 'ENN', 'NCR', 'Tomek', 'ALLKNN', 'OSS',
            'NM', 'CC', 'SMOTE', 'ADASYN', 'BorderSMOTE', 'SMOTEENN', 'SMOTETomek',
            'ORG', AUTO']
    '''

    sampler=sampler.lower()
    if sampler == 'rus':
        return RandomUnderSampler(random_state=random_state)
    elif sampler == 'cnn':
        return CondensedNearestNeighbour(random_state=random_state)
    elif sampler == 'enn':
        return EditedNearestNeighbours()
    elif sampler == 'ncr':
        return NeighbourhoodCleaningRule()
    elif sampler == 'tomek':
        return TomekLinks()
    elif sampler == 'allknn':
        return AllKNN()
    elif sampler == 'oss':
        return OneSidedSelection(random_state=random_state)
    elif sampler == 'nm':
        return NearMiss()
    elif sampler == 'cc':
        return ClusterCentroids(random_state=random_state)
    elif sampler == 'smote':
        return SMOTE(random_state=random_state)
    elif sampler == 'adasyn':
        return ADASYN(random_state=random_state)
    elif sampler == 'bordersmote':
        return BorderlineSMOTE(random_state=random_state)
    elif sampler == 'smoteen':
        return SMOTEENN(random_state=random_state)
    elif sampler == 'smotetomek':
        return SMOTETomek(random_state=random_state)
    elif sampler == 'auto':
        return AutoSampler(random_state=random_state)
    else:
        raise Exception('Unexpected \'by\' type {}'.format(sampler))

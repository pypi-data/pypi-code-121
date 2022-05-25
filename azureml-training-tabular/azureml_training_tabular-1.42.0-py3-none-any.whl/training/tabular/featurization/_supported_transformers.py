# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class SupportedTransformers:
    """Defines customer-facing names for transformers supported by AutoML.

    Transformers are classified for use with
    :class:`azureml.automl.core.constants.SupportedTransformersFactoryNames.Categorical`
    data (e.g., ``CatImputer``),
    :class:`azureml.automl.core.constants.SupportedTransformersFactoryNames.DateTime`
    data (e.g., ``DataTimeTransformer``),
    :class:`azureml.automl.core.constants.SupportedTransformersFactoryNames.Text`
    data (e.g., ``TfIdf``), or for
    :class:`azureml.automl.core.constants.SupportedTransformersFactoryNames.Generic`
    data types (e.g., ``Imputer``).

    .. remarks::

        The attributes defined in SupportedTransformers are used in featurization summaries when using
        `automatic preprocessing in automated ML
        <https://docs.microsoft.com/azure/machine-learning/concept-automated-ml#preprocess>`_
        or when customizing featurization with the
        :class:`azureml.automl.core.featurization.featurizationconfig.FeaturizationConfig` class
        as shown in the example.

        .. code-block:: python

            featurization_config = FeaturizationConfig()
            featurization_config.add_transformer_params('Imputer', ['column1'], {"strategy": "median"})
            featurization_config.add_transformer_params('HashOneHotEncoder', [], {"number_of_bits": 3})

        For more information, see `Configure automated ML experiments
        <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train>`_.

    Attributes:
        ImputationMarker: Add boolean imputation marker for imputed values.

        Imputer: Complete missing values.

        MaxAbsScaler: Scale data by its maximum absolute value.

        CatImputer: Impute missing values for categorical features by the most frequent category.

        HashOneHotEncoder: Convert input to hash and encode to one-hot encoded vector.

        LabelEncoder: Encode categorical data into numbers.

        CatTargetEncoder: Map category data with averaged target value for regression and to the class probability
            for classification.

        WoETargetEncoder: Calculate the Weight of Evidence of correlation of a categorical data to a target column.

        OneHotEncoder: Convert input to one-hot encoded vector.

        DateTimeTransformer: Expand datatime features into sub features such as year, month, and day.

        CountVectorizer: Convert a collection of documents to a matrix of token counts.

        NaiveBayes: Transform textual data using sklearn Multinomial Naïve Bayes.

        StringCast: Cast input to string and lower case.

        TextTargetEncoder: Apply target encoding to text data where a stacked linear model with bag-of-words
            generates the probability of each class.

        TfIdf: Transform a count matrix to a normalized TF or TF-iDF representation.

        WordEmbedding: Convert vectors of text tokens into sentence vectors using a pre-trained model.

        CUSTOMIZABLE_TRANSFORMERS: Transformers that are customized in featurization with parameters of methods
            in the :class:`azureml.automl.core.featurization.featurizationconfig.FeaturizationConfig` class.

        BLOCK_TRANSFORMERS: Transformers that can be blocked from use in featurization in the
            :class:`azureml.automl.core.featurization.featurizationconfig.FeaturizationConfig` class.

        FULL_SET: The full set of transformers.
    """

    # Generic
    ImputationMarker = "ImputationMarker"
    Imputer = "Imputer"
    MaxAbsScaler = "MaxAbsScaler"

    # Categorical
    CatImputer = "CatImputer"
    HashOneHotEncoder = "HashOneHotEncoder"
    LabelEncoder = "LabelEncoder"
    CatTargetEncoder = "CatTargetEncoder"
    WoETargetEncoder = "WoETargetEncoder"
    OneHotEncoder = "OneHotEncoder"

    # DateTime
    DateTimeTransformer = "DateTimeTransformer"

    # Text
    CountVectorizer = "CountVectorizer"
    NaiveBayes = "NaiveBayes"
    StringCast = "StringCast"
    TextTargetEncoder = "TextTargetEncoder"
    TfIdf = "TfIdf"
    WordEmbedding = "WordEmbedding"

    CUSTOMIZABLE_TRANSFORMERS = {HashOneHotEncoder, Imputer, TfIdf}

    BLOCK_TRANSFORMERS = {
        HashOneHotEncoder,
        LabelEncoder,
        CatTargetEncoder,
        WoETargetEncoder,
        OneHotEncoder,
        CountVectorizer,
        NaiveBayes,
        TextTargetEncoder,
        TfIdf,
        WordEmbedding,
    }

    FULL_SET = {
        ImputationMarker,
        Imputer,
        MaxAbsScaler,
        CatImputer,
        HashOneHotEncoder,
        LabelEncoder,
        CatTargetEncoder,
        WoETargetEncoder,
        OneHotEncoder,
        DateTimeTransformer,
        CountVectorizer,
        NaiveBayes,
        StringCast,
        TextTargetEncoder,
        TfIdf,
        WordEmbedding,
    }


class SupportedTransformersInternal(SupportedTransformers):
    """Defines transformer names for all transformers supported by AutoML, including those not exposed."""

    # Generic
    LambdaTransformer = "LambdaTransformer"
    MiniBatchKMeans = "MiniBatchKMeans"

    # Numeric
    BinTransformer = "BinTransformer"

    # Text
    BagOfWordsTransformer = "BagOfWordsTransformer"
    StringConcat = "StringConcat"
    TextStats = "TextStats"
    AveragedPerceptronTextTargetEncoder = "AveragedPerceptronTextTargetEncoder"

    # TimeSeries
    GrainMarker = "GrainMarker"
    MaxHorizonFeaturizer = "MaxHorizonFeaturizer"
    Lag = "Lag"
    RollingWindow = "RollingWindow"
    STLFeaturizer = "STLFeaturizer"
    TimeIndexFeaturizer = "TimeIndexFeaturizer"

    # Ignore
    Drop = ""

    # For categorical indicator work column transformer
    DropColumnsTransformer = "DropColumnsTransformer"

    FULL_SET = {
        LambdaTransformer,
        MiniBatchKMeans,
        BinTransformer,
        BagOfWordsTransformer,
        StringConcat,
        TextStats,
        AveragedPerceptronTextTargetEncoder,
        GrainMarker,
        MaxHorizonFeaturizer,
        Lag,
        RollingWindow,
        STLFeaturizer,
        TimeIndexFeaturizer,
        Drop,
    }.union(set(SupportedTransformers.FULL_SET))


FEATURIZERS_NOT_TO_BE_SHOWN_IN_ENGG_FEAT_NAMES = {
    SupportedTransformersInternal.StringCast,
    SupportedTransformersInternal.DateTimeTransformer,
}

import pandas as pd
import pytest


class MultilabelTestDataset:
    def __init__(self, multiple_text_column):
        self.multiple_text_column = multiple_text_column

    def get_data(self):
        text_col_1 = [
            'This is a small sample dataset containing cleaned text data.',
            'It was created manually so that it can be used for tests in text-classification tasks.',
            'It can be leveraged in tests to verify that codeflows are working as expected.',
            'It can also be used to verify that a machine learning model training successfully.',
            'It should not be used to validate the model performance using metrics.'
        ] * 10

        text_col_2 = [
            'This is an additional column.',
            'It was created to test the multiple-text columns scenario for classification.',
            'It can be leveraged in tests to verify that multiple-column codeflows are functional.',
            'It can also be used to verify that a ML model trained successfully with multiple columns.',
            'It should not be used to validate the multiple text columns model performance'
        ] * 10

        labels_col = [
            "['A', 'a', '1', '2', 'label5', 'label6']",
            "['1', 'label6', 'label5', 'A']",
            "['a', '2']",
            "['label6']",
            "[]"
        ] * 10

        data = {'text': text_col_1,
                'labels_col': labels_col}

        if self.multiple_text_column:
            data['text_second'] = text_col_2

        df = pd.DataFrame(data)
        return df


class MultilabelNoisyLabels:
    def __init__(self, special_token):
        self.special_token = special_token

    def get_data(self):
        labels = [
            "['A<TOKEN>B', 'C<TOKEN>D', 'E<TOKEN>F']".replace("<TOKEN>", self.special_token),
            "['A<TOKEN>B', 'E<TOKEN>F']".replace("<TOKEN>", self.special_token),
            "[1, 2]"
        ]
        return pd.DataFrame({"labels": labels})


@pytest.fixture
def MultilabelDatasetTester(multiple_text_column):
    """Create MultilabelDatasetTester object"""
    return MultilabelTestDataset(multiple_text_column)


@pytest.fixture
def MultilabelNoisyLabelsTester(special_token):
    """Create MultilabelNoisyLabels object"""
    return MultilabelNoisyLabels(special_token)

import copy
import re
import logging

import numpy as np
import pandas as pd

from .core_objects import DatasetInfo

LOG = logging.getLogger(__name__)

class ExperimentalFeatures:
    def __init__(self, client):
        self.client = client
        self.embeddings = None

    def initialize_embeddings(self, path):
        """
        Initializes NLP embeddings.
        :param path: A file path containing an embeddings file.
        """
        embedding_index = {}

        with open(path, encoding='utf8') as f:
            LOG.info('Reading embedding file ...')
            for line in f:
                values = line.split()
                word = values[0]
                vectors = np.asarray(values[1:], dtype='float32')
                embedding_index[word] = vectors

        self.embeddings = embedding_index
        LOG.info('Embeddings initialized.')

    def embed_texts(self, texts):
        """Helper to embed texts"""
        if self.embeddings is None:
            raise Exception(
                'No embeddings initialized.  Please run ' 'initialize_embeddings first.'
            )

        emb_length = len(self.embeddings[next(iter(self.embeddings))])
        tokenized_texts = self.make_word_list(texts)
        output_embeddings = []

        for text in tokenized_texts:
            word_embeddings = [
                self.embeddings[word] for word in text if word in self.embeddings
            ]
            if len(word_embeddings) == 0:
                output_embeddings.append(np.zeros([emb_length]))
            else:
                v = np.sum(np.asarray(word_embeddings).reshape(-1, emb_length), axis=0)
                output_embeddings.append(v / np.sqrt(v @ v))

        return np.asarray(output_embeddings)

    def upload_dataset_with_nlp_embeddings(
        self, project_id, dataset_id, dataset, info, text_field_to_index
    ):
        """
        Uploads a dataset with NLP embeddings.
        :param project_id: The project to which the dataset will be uploaded.
        :param dataset_id: A unique ID for the dataset.
        :param dataset: A dictionary mapping names of data files to pandas DataFrames.
        :param info: The fdl.DatasetInfo object for the dataset.
        :param text_field_to_index: The text field to be indexed.
        """
        info = copy.copy(info)
        indexed_dfs = {}
        first = True
        for k, input_df in dataset.items():
            df = input_df.reset_index(drop=True)
            embeddings = self.embed_texts(df[text_field_to_index].tolist())
            emb_df = pd.DataFrame(
                embeddings,
                columns=[
                    f'_emb_{text_field_to_index}_{i}'
                    for i in range(embeddings.shape[1])
                ],
            )

            final_df = pd.concat([df, emb_df], axis=1)
            indexed_dfs[k] = final_df
            if first:
                emb_dataset_info = DatasetInfo.from_dataframe(emb_df)
                info.columns = info.columns + emb_dataset_info.columns
            first = False

        res = self.client.upload_dataset(
            project_id=project_id, dataset_id=dataset_id, dataset=indexed_dfs, info=info
        )

        return res

    def nlp_similarity_search(
        self,
        project_id,
        dataset_id,
        model_id,
        nlp_field='',
        string_to_match='',
        num_results=5,
        where_clause='',
        drop_emb_cols=True,
    ):
        """
        Performs text-wise similarity search for NLP data.
        :param project_id: The project containing the dataset and model.
        :param dataset_id: The dataset associated with the model.
        :param model_id: The model associated with the dataset.
        :param nlp_field: The field containing NLP data.
        :param string_to_match: The string being searched against.
        :param num_results: The number of results to return.
        :param where_clause: Optional WHERE clause for filtering.
        """

        def generate_dist_query(string):
            # computes the SQL dot-product of a particular point's embeddings
            # and embedding column names.
            emb_point = self.embed_texts([string])[0]
            fields = [f'_emb_{nlp_field}_{i}' for i in range(len(emb_point))]
            prods = [f'{val}*{field}' for val, field in zip(emb_point, fields)]
            return '+'.join(prods)

        dist = generate_dist_query(string_to_match)

        q = f'SELECT *, {dist} as cossim FROM "{dataset_id}.{model_id}" {where_clause} ORDER BY cossim DESC LIMIT {num_results}'

        path = ['executor', self.client.org_id, project_id, 'slice_query']
        out = self.client._call(path, json_payload={'sql': q, 'project': project_id})
        info = out[0]
        data = out[1:]

        if drop_emb_cols:
            emb_cols = [x for x in info['columns'] if '_emb' in x]
            return pd.DataFrame(data, columns=info['columns']).drop(emb_cols, axis=1)
        else:
            return pd.DataFrame(data, columns=info['columns'])

    DIST_NUMERIC = 0  # Distance can be computed numerically
    DIST_BINARY = 1  # Distance is binary

    DIST_METRIC_BY_DATA_TYPE = {
        'int': DIST_NUMERIC,
        'category': DIST_BINARY,
        'float': DIST_NUMERIC,
        'bool': DIST_BINARY,
        'str': DIST_BINARY,
    }

    def tabular_similarity_search(
        self,
        project_id,
        dataset_id,
        model_id,
        feature_point_to_match,
        features_in_dist=[],
        exclude_features_in_dist=[],
        most_similar=True,
        num_results=5,
        where_clause='',
    ):
        """
        Performs row-wise similarity search for tabular data.
        :param project_id: The project containing the dataset and model.
        :param dataset_id: The dataset associated with the model.
        :param model_id: The model associated with the dataset.
        :param feature_point_to_match: The event being searched against.
        :param num_results: The number of results to return.
        :param where_clause: Optional WHERE clause for filtering.
        """

        # If the input is a DataFrame, convert it to a series
        if isinstance(feature_point_to_match, pd.DataFrame):
            feature_point = feature_point_to_match.iloc[0]
        else:
            feature_point = feature_point_to_match

        query_target = f'{dataset_id}.{model_id}'

        ################
        # Let's get all the info about the fields in the slice so we can
        # build a distance query.  Metrics for each field will vary by data
        # type.

        q = f'SELECT * FROM "{query_target}" {where_clause}  LIMIT 0'

        path = ['executor', self.client.org_id, project_id, 'slice_query']
        out = self.client._call(path, json_payload={'sql': q, 'project': project_id})
        info = out[0]

        feature_dtype_hash = {
            x['column-name']: x['data-type'] for x in info['model_schema']['inputs']
        }

        if not features_in_dist:
            features_in_dist = feature_dtype_hash.keys()

        # Make sure the user provided enough fields for the specified
        # model's inputs.
        missing_features = set(feature_dtype_hash.keys()) - set(feature_point.index)

        if missing_features:
            raise Exception(
                f'feature_point_to_match is missing: '
                f'{missing_features} which is a '
                f'necesary input for the model specified ('
                f'{project_id}:{model_id}).'
            )

        # Make sure any exclude_features actually reside in the dataset
        unknown_excludes = set(exclude_features_in_dist) - set(
            feature_dtype_hash.keys()
        )

        if unknown_excludes:
            raise Exception(
                f'Exclude features include: '
                f'{unknown_excludes} which not '
                f'an input for the model ('
                f'{project_id}:{model_id}).'
            )

        ################
        # Get the standard deviation of the numeric fields for scaling. In the
        # future, add options for alternatives e.g. Median Absolute Distance

        scalable_fields = [
            fname
            for fname in features_in_dist
            if self.DIST_METRIC_BY_DATA_TYPE[feature_dtype_hash[fname]]
            == self.DIST_NUMERIC
            and fname not in exclude_features_in_dist
        ]

        if scalable_fields:
            q_items = [
                f'cast(stddev({self._fix_db_name(fname)}) as FLOAT)'
                for fname in scalable_fields
            ]

            q = f'SELECT {", ".join(q_items)} FROM "{query_target}" {where_clause}'

            out = self.client._call(
                path, json_payload={'sql': q, 'project': project_id}
            )

            scale_factors = {x: y for x, y in zip(scalable_fields, out[1])}

        def generate_dist_query():
            query_items = []
            for feature_name in features_in_dist:
                feature_type = feature_dtype_hash[feature_name]
                if feature_name in exclude_features_in_dist:
                    continue
                if self.DIST_METRIC_BY_DATA_TYPE[feature_type] == self.DIST_NUMERIC:
                    query_items.append(
                        f'POWER(({self._fix_db_name(feature_name)}-{feature_point[feature_name]})/{scale_factors[feature_name]},2)'
                    )
                else:
                    query_items.append(
                        f'CASE WHEN {self._fix_db_name(feature_name)}=\'{feature_point[feature_name]}\' THEN 0.0 ELSE 1.0 END'
                    )

            return 'CAST(POWER(' + ' + '.join(query_items) + ', 0.5) AS FLOAT)'

        q = f'SELECT {generate_dist_query()} AS __distance, * FROM "{query_target}" {where_clause} ORDER BY __distance {"" if most_similar else "DESC"} LIMIT {num_results}'

        out = self.client._call(path, json_payload={'sql': q, 'project': project_id})

        ######
        # Make a map to unmangle all the column names before output
        orig_fields = {}

        for x in info['model_schema']['inputs']:
            orig_fields[self._fix_db_name(x['column-name'])] = x['column-name']

        for x in info['model_schema']['targets']:
            orig_fields[self._fix_db_name(x['column-name'])] = x['column-name']

        for x in info['model_schema']['outputs']:
            orig_fields[self._fix_db_name(x['column-name'])] = x['column-name']
        ######

        out_cols = [
            orig_fields[x] if x in orig_fields else x for x in out[0]['columns']
        ]

        out_df = pd.DataFrame(out[1:], columns=out_cols)

        # return out_df, q
        return out_df

    def run_nlp_feature_impact(
        self,
        project_id,
        dataset_id,
        model_id,
        prediction_field_name=None,
        source=None,
        num_texts=None,
    ):
        """
        Performs ablation feature impact on a collection of text samples
        determining which words have the most impact on the
        prediction. Will default to first prediction of a multi-output model
        if no prediction_field_name is specified.

        Returns the name of the prediction field being explained, a list
        of the prediction fields available, and a list of tuples containing
        average-impact, word-token, and occurrence count.
        :param project_id: The project containing the dataset and model.
        :param dataset_id: The dataset associated with the model.
        :param model_id: The model associated with the dataset.
        :param source: The dataset split to compute feature impact over.
        """
        afi = self.FeatureImpactWBatchedRetrieval(
            api=self.client,
            project_id=project_id,
            dataset_id=dataset_id,
            model_id=model_id,
            source=source,
            num_texts=num_texts,
            output_key=prediction_field_name,
        )

        texts = self.make_word_list(afi.texts)

        for text in texts:
            afi.get_prediction(
                None, ' '.join(text)
            )  # Full texts is base-prediction; no words ablated.

            for word in text:
                afi.get_prediction(word, ' '.join([w for w in text if w is not word]))

        # Get predictions from any remaining words in the queue.
        afi.flush_cache()

        afi.mean_word_impact = {
            word: afi.total_word_impact[word] / afi.word_counts[word]
            for word in afi.word_counts.keys()
        }

        afi.sorted_impact = sorted(
            zip(afi.mean_word_impact.values(), afi.mean_word_impact.keys()),
            reverse=True,
        )

        return (
            afi.requested_key,
            afi.prediction_keys,
            [(impact, key, afi.word_counts[key]) for impact, key in afi.sorted_impact],
        )

    # Non-member experimental functions/classes

    def _fix_db_name(self, name):
        """
        Helper to convert non-alphanumeric characters to underscores.
        :param name: str A feature name to make SQL-compatible
        :return: str A SQL-compatible field name.
        """
        # Copied from database.py
        # Allow only a-z, 0-9, and _
        return re.sub(r'[^a-zA-Z0-9_]', '_', name).lower()

    # ["A!dog.", "Let's Dance!"] -> [["a", "dog"], ["let's", "dance"]]

    def make_word_list(self, texts):
        """Helper for other NLP features"""
        out = []
        # This is essentially how the Keras tokenizer preprocesses.
        for text in texts:
            # replace punctuation with space unless single-quote
            x = re.sub('[!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n]', ' ', text)
            # condense multiple space characters, strip leading + trailing
            # finally split into a word list.  Append to a list with an
            # entry per text.
            x = re.sub(' +', ' ', x).strip().lower().split(' ')
            out.append(x)

        return out

    class FeatureImpactWBatchedRetrieval:
        """Helper class to support NLP feature impact"""

        DEFAULT_BATCH_SIZE = 1000
        DEFAULT_NUM_TEXTS = 250

        def __init__(
            self,
            api,
            project_id,
            dataset_id,
            model_id,
            source=None,
            num_texts=DEFAULT_NUM_TEXTS,
            batch_size=DEFAULT_BATCH_SIZE,
            output_key=None,
        ):
            self.api = api
            self.dataset = api.get_dataset(
                project_id=project_id,
                dataset_id=dataset_id,
                max_rows=1000000 if num_texts is None else num_texts,
            )

            self.batch_size = batch_size
            self.text_field_name = (
                api.get_model_info(project_id, model_id).inputs[0].name
            )

            self.texts = []
            if source is None:
                source = next(iter(self.dataset))

            self.texts = self.dataset[source][self.text_field_name].values

            self.project_id = project_id
            self.model_id = model_id

            self.requested_key = output_key
            self.prediction_keys = None

            self.word_counts = {}
            self.total_word_impact = {}
            self.last_base_prediction = None
            self.clear_cache()

        def clear_cache(self):
            self.predict_cache_size = 0
            self.cache_word = []
            self.cache_text = []

        def run_predictions(self, texts):
            if len(texts) > 0:

                prediction = self.api.run_model(
                    project_id=self.project_id,
                    model_id=self.model_id,
                    df=pd.DataFrame({self.text_field_name: texts}),
                )

                self.prediction_keys = prediction.columns

                if self.requested_key is None:
                    self.requested_key = self.prediction_keys[0]

                return prediction[self.requested_key]
            else:
                return []

        def flush_cache(self):
            preds = self.run_predictions(self.cache_text)
            for word, pred in zip(self.cache_word, preds):
                if word is None:
                    self.last_base_prediction = pred
                else:
                    if word not in self.word_counts:
                        self.word_counts[word] = 0
                        self.total_word_impact[word] = 0

                    self.word_counts[word] += 1
                    self.total_word_impact[word] += self.last_base_prediction - pred

            self.clear_cache()

        def get_prediction(self, word, text):
            self.predict_cache_size += 1

            if self.predict_cache_size > self.batch_size:
                self.flush_cache()
            else:
                self.cache_word.append(word)
                self.cache_text.append(text)

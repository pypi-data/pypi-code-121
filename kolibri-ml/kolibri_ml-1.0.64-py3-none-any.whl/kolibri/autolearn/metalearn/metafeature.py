from kolibri.core import Component
from io import StringIO
import os
import joblib

import arff

KOLIBRI_FEATURE_FILE_NAME = 'Features_file.arff'


class DatasetMetafeatures(Component):
    def __init__(self, dataset_name, metafeature_values):
        super().__init__()
        self.dataset_name = dataset_name
        self.metafeature_values = metafeature_values

    def persist(self, model_dir):

        classifier_file = os.path.join(model_dir, KOLIBRI_FEATURE_FILE_NAME)
        joblib.dump(self, classifier_file)

        output = dict()
        output['relation'] = "metafeatures_%s" % (self.dataset_name)
        output['description'] = ""
        output['attributes'] = [('name', 'STRING'),
                                ('type', 'STRING'),
                                ('fold', 'NUMERIC'),
                                ('repeat', 'NUMERIC'),
                                ('value', 'NUMERIC'),
                                ('time', 'NUMERIC'),
                                ('comment', 'STRING')]
        output['data'] = []

        for key in sorted(self.metafeature_values):
            output['data'].append(self.metafeature_values[key].to_arff_row())
        with open(model_dir, "w") as fh:
            arff.dump(output, fh)


        return {
            "features_file": KOLIBRI_FEATURE_FILE_NAME,
        }


    @classmethod
    def load(cls, model_dir=None, model_metadata=None, cached_component=None, **kwargs):

        file_name = model_metadata.get("features_file", KOLIBRI_FEATURE_FILE_NAME)
        arff_file = os.path.join(model_dir, file_name)

        if isinstance(arff_file, str):
            with open(arff_file) as fh:
                input = arff.load(fh)
        else:
            input = arff.load(arff_file)

        dataset_name = input['relation'].replace('metafeatures_', '')
        feature_values = []
        for feature in input['data']:
            feature_values.append(feature)

        return cls(dataset_name, feature_values)

    def __repr__(self, verbosity=0):
        repr = StringIO()
        repr.write("Metafeatures for dataset %s\n" % self.dataset_name)
        for name in self.metafeature_values:
            if verbosity == 0 and self.metafeature_values[name].type_ != "METAFEATURE":
                continue
            if verbosity == 0:
                repr.write("  %s: %s\n" %
                           (str(name), str(self.metafeature_values[name].value)))
            elif verbosity >= 1:
                repr.write("  %s: %10s  (%10fs)\n" %
                           (str(name), str(self.metafeature_values[
                                               name].value)[:10],
                            self.metafeature_values[name].time))

            # Add the reason for a crash if one happened!
            if verbosity > 1 and self.metafeature_values[name].comment:
                repr.write("    %s\n" % self.metafeature_values[name].comment)

        return repr.getvalue()

    def keys(self):
        return self.metafeature_values.keys()

    def __getitem__(self, item):
        return self.metafeature_values[item]

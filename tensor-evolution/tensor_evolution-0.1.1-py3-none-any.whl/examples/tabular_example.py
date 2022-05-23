import pandas as pd
import tensorflow as tf
from tensorEvolution import evo_config, tensor_evolution

raw_train = pd.read_csv('C:\\Users\\arjud\\Downloads\\train.csv\\train.csv')
test = pd.read_csv('C:\\Users\\arjud\\Downloads\\train.csv\\test.csv')

# From https://www.kaggle.com/ambrosm/tpsmay22-eda-which-makes-sense
for df in [raw_train, test]:
    for i in range(10):
        df[f'ch{i}'] = df.f_27.str.get(i).apply(ord) - ord('A')
    df["unique_characters"] = df.f_27.apply(lambda s: len(set(s)))

raw_train = raw_train.sample(frac=1.0)
train_split = raw_train.sample(frac=0.7, random_state=200)  # random state is a seed value
validation = raw_train.drop(train_split.index)

test_ids = test['id']

train_labels = train_split['target']
train_split = train_split.drop(['id', 'target', 'f_27'], axis=1)
test = test.drop(['id', 'f_27'], axis=1)

validation_labels = validation['target']
validation = validation.drop(['id', 'target', 'f_27'], axis=1)

# build custom config
custom_config = {}
custom_config['input_shapes'] = [[41]]
custom_config['num_outputs'] = [1]
custom_config['pop_size'] = 50
custom_config['remote'] = True
custom_config['loss'] = 'BinaryCrossentropy'
custom_config['remote_actors'] = 5

# set the custom config
evo_config.master_config.setup_user_config(custom_config)

# build data tuple
data = train_split, train_labels, validation, validation_labels
# create evolution worker
worker = tensor_evolution.EvolutionWorker()
worker.evolve(data=data)

# inputs = tf.keras.Input(shape=(41,))
# x = tf.keras.layers.Dense(32, activation="relu")(inputs)
# x = tf.keras.layers.Dense(32, activation="relu")(x)
# outputs = tf.keras.layers.Dense(1, activation=None)(x)
# model = tf.keras.Model(inputs, outputs)
# model.compile(loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
#               optimizer='adam',
#               metrics=[tf.metrics.BinaryAccuracy(threshold=0.0), tf.keras.metrics.AUC(from_logits=True)])
# model.fit(train, train_labels, validation_split=0.3, shuffle=False, epochs=10)
# probability_model = tf.keras.Sequential([model,
#                                          tf.keras.layers.Activation('sigmoid')])
#
# predictions = probability_model.predict(test)
# predictions_df = pd.DataFrame(predictions)
# submission_df = pd.concat([test_ids, predictions_df], axis=1)
# submission_df = submission_df.rename({0: 'target'}, axis="columns")
# submission_df.to_csv("C:\\Users\\arjud\\Downloads\\train.csv\\submission.csv", index=False)

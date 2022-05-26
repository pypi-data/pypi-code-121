import numpy as np
import sklearn
import matplotlib.pyplot as plt

import json
import pandas as pd
from datetime import datetime, timedelta

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from tensorflow import keras
from tensorflow.keras import layers
import tensorflow
from tensorflow.keras import models
import joblib

############################

############################ Import Dataset
df_dataset = pd.read_csv("./nova/slippage_estimation_ml/database/full_dataset_3_0_10k.csv")

############################ Create train et test set

df_entry_train = df_dataset[['side', 'quote_asset_volume', 'taker_quote_volume', 'nb_of_trades', 'last_24h_volume']]
df_entry_train['side'] = np.where(df_entry_train['side'] == 'buy', 1, 0)
df_outputs_train = df_dataset[['beta0', 'beta1']]

X_train, X_test, y_train, y_test = train_test_split(df_entry_train, df_outputs_train, test_size=0.05, random_state=42)

############################ Scale data

scaler_x = StandardScaler(with_mean=False)

X_train = scaler_x.fit_transform(X_train)
X_test = scaler_x.transform(X_test)

scaler_y = StandardScaler(with_mean=False)

y_train = scaler_y.fit_transform(y_train)

############################ Create model

model = keras.Sequential(
    [
        layers.Dense(8, activation="relu"),
        layers.Dense(8, activation="relu"),
        layers.Dense(2, activation="relu"),
        layers.Dense(2),
    ]
)

model.compile(optimizer=tensorflow.keras.optimizers.Adam(learning_rate=0.0001),
              loss='mse')


############################ Train
callbacks = [
    tensorflow.keras.callbacks.EarlyStopping(patience=2)
]

with tensorflow.device('GPU'):
    model.fit(X_train, y_train,
              validation_split=0.3,
              epochs=50,
              batch_size=128,
              callbacks=callbacks)

model.save("model_slippage_3.h5")

############################ Display loss evolution

plt.figure(figsize=(7,7))
plt.plot([i + 1 for i in range(len(model.history.history['loss']))],
            model.history.history['loss'], c='blue', label='train_loss')
plt.plot([i + 1 for i in range(len(model.history.history['loss']))],
         model.history.history['val_loss'], c='red', label='val_loss')
plt.title(f"Loss evolution")
plt.legend()
plt.show()

############################ Evaluate model

model.evaluate(X_test, scaler_y.transform(y_test))

########################### Print results

scaler_x = joblib.load('./scaler_x.gz')
scaler_y = joblib.load('./scaler_y.gz')
model = models.load_model('./model_slippage_3.h5')


def get_all_price_qty(df,
                      ts,
                      side='ask'):
    all_ask_price = []
    all_ask_qty_usdt = []

    row = df[df['timestamp'] == ts]

    for i in range(99):
        price = row[f'{side}_price_{i}'].to_list()[0]
        qty = row[f'{side}_qty_{i}'].to_list()[0]
        all_ask_price.append(price)
        all_ask_qty_usdt.append(round(qty * price, 2))

    return all_ask_price, all_ask_qty_usdt

def compute_slippage(all_price,
                     all_qty_usdt,
                     amount):
    residual_amount = amount
    avg_price = 0
    first_price = all_price[0]

    for i in range(len(all_price)):

        if residual_amount <= all_qty_usdt[i]:
            avg_price += residual_amount * all_price[i]
            break

        else:
            avg_price += all_qty_usdt[i] * all_price[i]
            residual_amount -= all_qty_usdt[i]

    avg_price = avg_price / amount

    slippage = 100 * (max(avg_price, first_price) / min(avg_price, first_price) - 1)

    return slippage


def display_results(pair,
                    ts):

    df = pd.read_csv(f"./nova/slippage_estimation_ml/database/{pair}_binance_orderbook_full.csv")
    df['timestamp'] = df['timestamp'] - df['timestamp'] % 10000
    df['open_time'] = pd.to_datetime(df['timestamp'], unit='ms')

    all_ask_price, all_ask_qty_usdt = get_all_price_qty(df, ts, side='ask')

    list_amounts = [i for i in range(100, 1000,100)] + [i for i in range(1000, 10000,1000)]
    list_slippage = []

    for amount in list_amounts:
        list_slippage.append(compute_slippage(all_ask_price, all_ask_qty_usdt, amount))

    historical_data = pd.read_csv(f"../nova-algo/database/futures/hist_{pair}_1m.csv")
    historical_data['last_24h_volume'] = historical_data['quote_asset_volume'].rolling(min_periods=1, window=60*24).sum()
    historical_data = historical_data[historical_data['timestamp'] == ts]
    historical_data['side'] = 1

    features_data = historical_data[['side', 'quote_asset_volume', 'taker_quote_volume', 'nb_of_trades',
                                     'last_24h_volume']]

    features_data = scaler_x.transform(features_data)

    pred = model.predict(features_data)
    pred = scaler_y.inverse_transform(pred)[0]

    slippage_pred = [0, pred[0], pred[1]]
    list_amounts_pred = [0, 5000, 10000]

    plt.figure(figsize=(10,10))
    plt.scatter(list_amounts, list_slippage, s=1, facecolor='blue', label='real slippage')
    plt.plot(list_amounts_pred, slippage_pred, c='red', label='Prediction')
    plt.title(f"Slippage prediction for {pair}")
    plt.axis([0, 10000, 0, 0.08])
    plt.legend()
    plt.show()


for pair in ["AAVEUSDT", "1INCHUSDT", "ANTUSDT", "AUDIOUSDT", "SOLUSDT", "TRXUSDT", "YFIUSDT", "ZECUSDT", "ZENUSDT",
             "ETHUSDT", "BTCUSDT", "IOTAUSDT", "HOTUSDT", "GRTUSDT", "GALAUSDT", "LTCUSDT", "NEARUSDT", "MANAUSDT",
             "MASKUSDT", "ONTUSDT", "RVNUSDT", "SANDUSDT", "STORJUSDT"]:
    display_results(pair=pair,
                    ts=1649269320000)





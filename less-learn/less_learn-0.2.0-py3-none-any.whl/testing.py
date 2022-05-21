# # %%
# from random import Random, random
# from sklearn.datasets import make_regression, make_classification
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import mean_squared_error, accuracy_score
# from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
# from sklearn.tree import DecisionTreeRegressor
# from less import LESSRegressor, LESSClassifier
# from sklearn.cluster import KMeans
# # %%

# X, y = make_regression(n_samples=1000, n_features=50, random_state=42)

# # Train and test split
# X_train, X_test, y_train, y_test = \
#     train_test_split(X, y, test_size=0.3, random_state=42)

# # LESS fit() & predict()
# LESS_model = LESSRegressor(random_state=42)
# LESS_model.fit(X_train, y_train)
# y_pred = LESS_model.predict(X_test)
# print('Test error of LESS: {0:.2f}'.format(mean_squared_error(y_pred, y_test)))

# RF_model = RandomForestRegressor(random_state=42)
# RF_model.fit(X_train, y_train)
# y_pred = RF_model.predict(X_test)
# print('Test error of RF: {0:.2f}'.format(mean_squared_error(y_pred, y_test)))

# # %%
# # %%

# X, y = make_classification(n_samples=1000, n_features=20, n_classes=3, n_clusters_per_class=2, n_informative=10, random_state=42)

# # Train and test split
# X_train, X_test, y_train, y_test = \
#     train_test_split(X, y, test_size=0.3, random_state=42)

# # LESS fit() & predict()
# LESS_model = LESSClassifier(random_state=42, cluster_method=KMeans)
# LESS_model.fit(X_train, y_train)
# y_pred = LESS_model.predict(X_test)
# print('Test accuracy of LESS: {0:.2f}'.format(accuracy_score(y_pred, y_test)))

# RF_model = RandomForestClassifier(random_state=42)
# RF_model.fit(X_train, y_train)
# y_pred = RF_model.predict(X_test)
# print('Test accuracy of RF: {0:.2f}'.format(accuracy_score(y_pred, y_test)))
# %%

# from sklearn.datasets import make_regression, make_classification
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import mean_squared_error, accuracy_score
# from less import LESSRegressor, LESSClassifier

# # Classification
# X, y = make_classification(n_samples=1000, n_features=20, random_state=42)

# # Train and test split
# X_train, X_test, y_train, y_test = \
#     train_test_split(X, y, test_size=0.3, random_state=42)

# # LESS fit() & predict()
# LESS_model = LESSClassifier(random_state=42)
# LESS_model.fit(X_train, y_train)
# y_pred = LESS_model.predict(X_test)
# print('Test accuracy of LESS: {0:.2f}'.format(accuracy_score(y_pred, y_test)))

# # Regression
# X, y = make_regression(n_samples=1000, n_features=20, random_state=42)

# # Train and test split
# X_train, X_test, y_train, y_test = \
#     train_test_split(X, y, test_size=0.3, random_state=42)

# # LESS fit() & predict()
# LESS_model = LESSRegressor(random_state=42)
# LESS_model.fit(X_train, y_train)
# y_pred = LESS_model.predict(X_test)
# print('Test error of LESS: {0:.2f}'.format(mean_squared_error(y_pred, y_test)))
# %%


from sklearn.datasets import make_regression, make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
from less import LESSRegressor, LESSClassifier

X, y = make_classification(n_samples=1000, n_features=20, n_classes=3, \
                           n_clusters_per_class=2, n_informative=10, random_state=42)

# Train and test split
X_train, X_test, y_train, y_test = \
    train_test_split(X, y, test_size=0.3, random_state=42)

# LESS fit() & predict()
LESS_model = LESSClassifier(random_state=42)
LESS_model.fit(X_train, y_train)
y_pred = LESS_model.predict(X_test)
print('Test accuracy of LESS: {0:.2f}'.format(accuracy_score(y_pred, y_test)))

# Regression
X, y = make_regression(n_samples=1000, n_features=20, random_state=42)

# Train and test split
X_train, X_test, y_train, y_test = \
    train_test_split(X, y, test_size=0.3, random_state=42)

# LESS fit() & predict()
LESS_model = LESSRegressor(random_state=42)
LESS_model.fit(X_train, y_train)
y_pred = LESS_model.predict(X_test)
print('Test error of LESS: {0:.2f}'.format(mean_squared_error(y_pred, y_test)))
# %%

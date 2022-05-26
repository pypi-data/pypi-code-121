import matplotlib.pyplot as plt

import sklearn
import sklearn.datasets
import sklearn.linear_model
from booba.utils.planar_utils import plot_decision_boundary, load_planar_dataset
from booba.src import nn_1hl as nn_testhl
from booba.src.dnn import DNNModel
from booba.utils.process_datasets import *


def run_snn():
    #  load the dataset
    X, Y = load_planar_dataset()
    plt.scatter(X[0, :], X[1, :], c=Y, s=40, cmap=plt.cm.Spectral)
    plt.show()

    """
    # Performance on other datasets
    # Datasets
    noisy_circles, noisy_moons, blobs, gaussian_quantiles, no_structure = load_extra_datasets()
    datasets = {"noisy_circles": noisy_circles,
                "noisy_moons": noisy_moons,
                "blobs": blobs,
                "gaussian_quantiles": gaussian_quantiles}
    ### START CODE HERE ### (choose your dataset)
    dataset = "gaussian_quantiles"
    ### END CODE HERE ###
    X, Y = datasets[dataset]
    X, Y = X.T, Y.reshape(1, Y.shape[0])
    # make blobs binary
    if dataset == "blobs":
        Y = Y % 2
    # Visualize the data
    plt.scatter(X[0, :], X[1, :], c=Y, s=40, cmap=plt.cm.Spectral)
    plt.show()
    """

    shape_X = X.shape
    shape_Y = Y.shape
    m = Y.size

    print('The shape of X is: ' + str(shape_X))
    print('The shape of Y is: ' + str(shape_Y))
    print(f'I have m = {m} training examples1!')

    # Train the logistic regression classifier
    clf = sklearn.linear_model.LogisticRegressionCV()
    clf.fit(X.T, Y.T.ravel())

    # Plot the decision boundary for logistic regression
    plot_decision_boundary(lambda x: clf.predict(x), X, Y)
    plt.title("Logistic Regression")
    plt.show()

    # Print accuracy
    LR_predictions = clf.predict(X.T)
    print('Accuracy of logistic regression: %d ' % float(
        (np.dot(Y, LR_predictions) + np.dot(1 - Y, 1 - LR_predictions)) / float(Y.size) * 100) +
          '% ' + "(percentage of correctly labelled datapoints)")

    hidden_layer_size = 4
    nn_test = nn_1hl.NN1HiddenLayer(X, Y, hidden_layer_size)

    # Build a model with a n_h-dimensional hidden layer
    nn_model = nn_testhl.NN1HiddenLayer(X, Y, hidden_layer_size)
    nn_model.train(X, Y, n_h=4, num_iterations=10000, print_cost=True)
    # Plot the decision boundary
    plot_decision_boundary(lambda x: nn_model.predict(x.T), X, Y)
    plt.title("Decision Boundary for hidden layer size " + str(4))
    # Print accuracy
    predictions = nn_model.predict(X)
    print("Accuracy: {}" % float(
        (np.dot(Y, predictions.T) + np.dot(1 - Y, 1 - predictions.T)) / float(Y.size) * 100) + '%')
    plt.show()

    # Tuning hidden layer size
    plt.figure(figsize=(16, 32))
    hidden_layer_sizes = [1, 2, 3, 4, 5, 20, 50, 200]
    for i, n_h in enumerate(hidden_layer_sizes):
        plt.subplot(5, 2, i + 1)
        plt.title('Hidden Layer of size %d' % n_h)
        nn_model.train(X, Y, n_h, num_iterations=5000)
        plot_decision_boundary(lambda x: nn_model.predict(x.T), X, Y)
        predictions = nn_model.predict(X)
        accuracy = float((np.dot(Y, predictions.T) + np.dot(1 - Y, 1 - predictions.T)) / float(Y.size) * 100)
        print("Accuracy for {} hidden units: {} %".format(n_h, accuracy))
    plt.show()


def run_dnn():
    plt.rcParams['figure.figsize'] = (5.0, 4.0)  # set default size of plots
    plt.rcParams['image.interpolation'] = 'nearest'
    plt.rcParams['image.cmap'] = 'gray'
    np.random.seed(1)

    # Load datasets
    train_x_orig, train_y, test_x_orig, test_y, classes = load_data()
    index = 10
    plt.imshow(train_x_orig[index])
    print("y = " + str(train_y[0, index]) + ". It's a " + classes[train_y[0, index]].decode("utf-8") + " picture.")
    plt.show()

    # Explore your dataset
    m_train = train_x_orig.shape[0]
    num_px = train_x_orig.shape[1]
    m_test = test_x_orig.shape[0]
    """
    print("Number of training examples1: " + str(m_train))
    print("Number of testing examples1: " + str(m_test))
    print("Each image is of size: (" + str(num_px) + ", " + str(num_px) + ", 3)")
    print("train_x_orig shape: " + str(train_x_orig.shape))
    print("train_y shape: " + str(train_y.shape))
    print("test_x_orig shape: " + str(test_x_orig.shape))
    print("test_y shape: " + str(test_y.shape))
    """

    # Reshape the training and test examples1
    train_x_flatten = train_x_orig.reshape(train_x_orig.shape[0],
                                           -1).T  # The "-1" makes reshape flatten the remaining dimensions
    test_x_flatten = test_x_orig.reshape(test_x_orig.shape[0], -1).T
    # Standardize data to have feature values between 0 and 1.
    train_x = train_x_flatten / 255.
    test_x = test_x_flatten / 255.
    print("train_x's shape: " + str(train_x.shape))
    print("test_x's shape: " + str(test_x.shape))

    n_x = 12288  # num_px * num_px * 3
    n_h1 = 20
    n_h2 = 7
    n_h3 = 5
    n_y = 1
    layers_dims = [n_x, n_h1, n_h2, n_h3, n_y]  # 4-layer model
    dnn4layers = DNNModel(layers_dims)
    dnn4layers.train(train_x, train_y, learning_rate=0.0075, num_iterations=2500, print_cost=True)

    predictions_train = dnn4layers.predict(train_x, train_y)
    predictions_test = dnn4layers.predict(test_x, test_y)

    dnn4layers.print_mislabeled_images(classes, test_x, test_y, predictions_test)

    return


if __name__ == '__main__':
    # run_snn()
    run_dnn()
    print("\nProgram finished. Goodbye!")

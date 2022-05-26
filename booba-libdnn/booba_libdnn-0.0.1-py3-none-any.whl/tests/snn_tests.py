

def SNNTests():
    # t_X, t_Y = layer_sizes_test_case()
    # (n_x, n_h, n_y) = layer_sizes(t_X, t_Y)
    print("The size of the input layer is: n_x = " + str(nn_test.n_x))
    print("The size of the hidden layer is: n_h = " + str(nn_test.n_h))
    print("The size of the output layer is: n_y = " + str(nn_test.n_y))
    # TEST
    # layer_sizes_test(layer_sizes)

    #np.random.seed(2)
    #test_n_x, test_n_h, test_n_y = initialize_parameters_test_case()

    # nn_test.set_layer_sizes(test_n_x, test_n_h, test_n_y)
    # nn_test.initialize_parameters()

    print("W1 = " + str(nn_test.parameters["W1"]))
    print("b1 = " + str(nn_test.parameters["b1"]))
    print("W2 = " + str(nn_test.parameters["W2"]))
    print("b2 = " + str(nn_test.parameters["b2"]))
    # TEST
    #initialize_parameters_test(nn_test)


    t_X, parameters = forward_propagation_test_case()
    A2, cache = forward_propagation(t_X, parameters)
    print("A2 = " + str(A2))
    # TEST
    # forward_propagation_test(forward_propagation)


    A2, t_Y = compute_cost_test_case()
    cost = compute_cost(A2, t_Y)
    print("cost = " + str(compute_cost(A2, t_Y)))
    # TEST
    #compute_cost_test(compute_cost)


    parameters, cache, t_X, t_Y = backward_propagation_test_case()
    grads = backward_propagation(parameters, cache, t_X, t_Y)
    print("dW1 = " + str(grads["dW1"]))
    print("db1 = " + str(grads["db1"]))
    print("dW2 = " + str(grads["dW2"]))
    print("db2 = " + str(grads["db2"]))
    # TEST
    #backward_propagation_test(backward_propagation)

    parameters, grads = update_parameters_test_case()
    parameters = update_parameters(parameters, grads)
    print("W1 = " + str(parameters["W1"]))
    print("b1 = " + str(parameters["b1"]))
    print("W2 = " + str(parameters["W2"]))
    print("b2 = " + str(parameters["b2"]))
    # TEST
    # update_parameters_test(update_parameters)


    t_X, t_Y = nn_model_test_case()
    nn_test.train(t_X, t_Y, 4, num_iterations=10000, print_cost=True)
    print("W1 = " + str(nn_test.parameters["W1"]))
    print("b1 = " + str(nn_test.parameters["b1"]))
    print("W2 = " + str(nn_test.parameters["W2"]))
    print("b2 = " + str(nn_test.parameters["b2"]))
    # TEST
    nn_model_test(nn_test)


    parameters, t_X = predict_test_case()
    nn_test.set_parameters(parameters)
    predictions = nn_test.predict(t_X)
    print("Predictions: " + str(predictions))
    # TEST
    predict_test(nn_test)


def DNNTests():
    """
        dnn.initialize_parameters_test(3, 2, 1)
        print("W1 = " + str(dnn.parameters["W1"]))
        print("b1 = " + str(dnn.parameters["b1"]))
        print("W2 = " + str(dnn.parameters["W2"]))
        print("b2 = " + str(dnn.parameters["b2"]))
        dnn_tests.initialize_parameters_test(dnn.initialize_parameters)

        dnn.initialize_parameters_deep([5, 4, 3])

        print("W1 = " + str(dnn.parameters["W1"]))
        print("b1 = " + str(dnn.parameters["b1"]))
        print("W2 = " + str(dnn.parameters["W2"]))
        print("b2 = " + str(dnn.parameters["b2"]))
        # dnn_tests.initialize_parameters_deep_test(dnn.initialize_parameters_deep)

        t_A, t_W, t_b = linear_forward_test_case()
        t_Z, t_linear_cache = dnn.linear_forward(t_A, t_W, t_b)
        print("Z = " + str(t_Z))
        # dnn_tests.linear_forward_test(dnn.linear_forward)

        t_A_prev, t_W, t_b = linear_activation_forward_test_case()
        t_A, dnn.linear_activation_cache = dnn.linear_activation_forward(t_A_prev, t_W, t_b, activation="sigmoid")
        print("With sigmoid: A = " + str(t_A))
        t_A, dnn.linear_activation_cache = dnn.linear_activation_forward(t_A_prev, t_W, t_b, activation="relu")
        print("With ReLU: A = " + str(t_A))
        # dnn_tests.linear_activation_forward_test(dnn.linear_activation_forward)


        t_X, parameters = L_model_forward_test_case_2hidden(dnn)
        t_AL, caches = dnn.L_model_forward(t_X, parameters)
        print("AL = " + str(t_AL))
        dnn_tests.L_model_forward_test(dnn.L_model_forward)


        t_Y, t_AL = compute_cost_test_case()
        t_cost = dnn.compute_cost(t_AL, t_Y)
        print("Cost: " + str(t_cost))
        dnn_tests.compute_cost_test(dnn.compute_cost)


        t_dZ, t_linear_cache = linear_backward_test_case()
        t_dA_prev, t_dW, t_db = dnn.linear_backward(t_dZ, t_linear_cache)
        print("dA_prev: " + str(t_dA_prev))
        print("dW: " + str(t_dW))
        print("db: " + str(t_db))
        dnn_tests.linear_backward_test(dnn.linear_backward)


        t_dAL, t_linear_activation_cache = linear_activation_backward_test_case()
        t_dA_prev, t_dW, t_db = dnn.linear_activation_backward(t_dAL, t_linear_activation_cache, activation="sigmoid")
        print("With sigmoid: dA_prev = " + str(t_dA_prev))
        print("With sigmoid: dW = " + str(t_dW))
        print("With sigmoid: db = " + str(t_db))
        t_dA_prev, t_dW, t_db = dnn.linear_activation_backward(t_dAL, t_linear_activation_cache, activation="relu")
        print("With relu: dA_prev = " + str(t_dA_prev))
        print("With relu: dW = " + str(t_dW))
        print("With relu: db = " + str(t_db))
        dnn_tests.linear_activation_backward_test(dnn.linear_activation_backward)


        t_AL, t_Y_assess, t_caches = L_model_backward_test_case()
        grads = dnn.L_model_backward(t_AL, t_Y_assess, t_caches)
        print("dA0 = " + str(grads['dA0']))
        print("dA1 = " + str(grads['dA1']))
        print("dW1 = " + str(grads['dW1']))
        print("dW2 = " + str(grads['dW2']))
        print("db1 = " + str(grads['db1']))
        print("db2 = " + str(grads['db2']))
        dnn_tests.L_model_backward_test(dnn.L_model_backward)
        """

    t_parameters, grads = update_parameters_test_case()
    t_parameters = dnn.update_parameters(t_parameters, grads, 0.1)

    print("W1 = " + str(t_parameters["W1"]))
    print("b1 = " + str(t_parameters["b1"]))
    print("W2 = " + str(t_parameters["W2"]))
    print("b2 = " + str(t_parameters["b2"]))

    # dnn_tests.update_parameters_test(dnn.update_parameters)


    return
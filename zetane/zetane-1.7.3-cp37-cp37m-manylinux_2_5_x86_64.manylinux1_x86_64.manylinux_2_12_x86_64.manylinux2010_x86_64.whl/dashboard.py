

class Metric:
    """This class is used to initialize panels, dials and pie chart metrics"""
    def __init__(self):
        pass


    def metric_initialization(self):
        """This function is used to initialize the metrics variables
        
        Returns
        ztxt_overfitting(text): used to print whether model is overfitting, underfitting or working properly
        zchart_accuracy(chart dial): used to represent accuracy in dial
        Accuracy(z metric): used to show label and numeric value of accuracy
        zchart_val_accuracy(chart dial): used to represent validation accuracy in dial
        Val_Accuracy(z metric): used to show label and numeric value of validation accuracy
        z_train_accuracy(image): used to show the plot of the accuracy and validation accuracy on the matplotlib plot
        z_train_loss(image): used to show the plot of the loss and validation loss on the matplotlib plot
        zchart_Loss(char dial): used to represent loss in dial
        Loss(z metric):used to show label and numeric value of loss
        zchart_val_Loss(chart dial): used to represent validation loss in dial
        Val_Loss(z metric):used to show label and numeric value of validation loss
        z_precision(image):used to show the plot of the precision on the matplotlib plot
        zchart_precision(char dial):used to represent precision in dial
        Precision(z metric):used to show label and numeric value of precision
        z_recall(image): used to show the plot of the recall on the matplotlib plot
        zchart_recall(chart dial): used to represent recall in dial
        Recall(z metric): used to show label and numeric value of Recall
        zchart_Pie(pie chart): used to represent true positive, false positive, true negative and false negative in dial
        True_pos(z metric): used to show label and numeric value of true positive
        False_pos(z metric): used to show label and numeric value of false positive
        True_neg(z metric): used to show label and numeric value of true negative
        False_neg(z metric): used to show label and numeric value of false negative
        z_conf_matrix(image): used to represent the confusion matrix using matplotlib plot
        """
        return self


class Dashboard:
    """This class is used to create the Dashboard for both keras and pytorch classification models 
        
    Output -> [0,1,2,3,4,5,6,7,8,9,10] categorical variables 
    Args:
            model : defined or saved model used for training and inference
    
    """
    def __init__(self, model, zcontext, zmodel):
        pass


    def ztxt_initialization(self):
        """This function is used to initialize the metrics variables
        
        Returns
        ztxt_1(z_text): used to print the name and probability of the top prediction of the image
        ztxt_2(z_text): used to print the name and probability of the second best prediction of the image
        ztxt_3(z_text): used to print the name and probability of the third best prediction of the image
        ztxt_4(z_text): used to print the name and probability of the fourth best prediction of the image
        ztxt_5(z_text): used to print the name and probability of the fifth best prediction of the image
        ztxt_target(z_text): used to print the name of the target class
        ztxt_prediction(z_text): used to show prediction heading 
        ztxt_output(z_text): used to show target heading 
        time_ztxt(z_text): used to show the time taken for running one inference image
        zimg(z_image): used to show the images on the panel
        
        """
        return self


    def image_map(self, classes, image_table, N=1):
        """Take the most probable labels (output of postprocess).
        Args:
            classes (list): names of the classes used for training the model
            image_table (dictionary): dictionary to map the id to the names of the classes 
            N (int):  top N labels that fit the picture
            
        Returns:
            images (list):top N labels that fit the picture.
        """
        return self


    def plot_confusion_matrix(self, cm, classes, normalize=False, title='Confusion matrix', cmap=plt.cm.PuOr_r):
        """Plots and save the confusion matrix as jpg 
        Args:
            cm (numpy): numpy confusion matrix which will be plotted using this function
            classes (list): names of the classes used for training the model
            normalize (Boolean): Used to normalize the values of the confusion matrix
            title (string): used to provide the title to the image
            cmap (color map): used to provide the color map for the confusion matrix
            
        """
        return self


    def softmax(self, x):
        """Compute softmax values (probabilities from 0 to 1) for each possible label.
        Args:
            x (numpy): numpy (in this case score) for which softmax will be calculated
            
        Returns:
            e_x / e_x.sum(axis=0): softmax for the x values
        """
        return self


    def postprocess(self, scores):
        """This function takes the scores generated by the network.
        Args:
            scores(numpy): scores generated by the network 
            
        Returns:
            classes(numpy): the classes ids for the number of classes
            probability (float): probability of the classes predicted by the model
        """
        return self


    def metric_plots(self, title, metric_1 = [0], metric_2 = [0]):
        """This function plots the metrics and save them as png in the local directory
        
        Args:
            title(string): Title of the plot
            metric_1(list): numeric values of the metric in the list format to plot it on the graph
            metric_2(list): numeric values of the second metric in the list format to plot it on the graph
        
        """
        return self


    def keras_training(self, data, data_id, classes, model_type = 'classification', model_name='keras_model', validation_split =0.2, batch_size = 8, epochs = 1, verbose = 1):
        """
        This function is used to train the model, all types of models will be used for this template in future currently it handles only 
        classification models 
    
        Args:
            
            data (numpy): training data under which model will be trained
            data_id (numpy): class index or class id of the image under which model will be trained
            classes (list): names of the classes used for training the model
            model_type(string): Type of the model used 
            model_name (string): Name under which the keras model will be converted to onnx and will saved 
            validation_split (float): used to split the training data in validation and train set 
            batch_size (int): specifies the number of images that will send together for training 
            epochs (int): specifies the number of iterations that will be used for training the model
            verbose(int): specifies the verbage of the training model
    
        Returns:
          model: Returns the trained model which can used in inference
        """
        return self


    def keras_inference(self, test_data, test_data_id, image_table, model_name='keras_model', verbose = 1):
        """
        This function is used to test the model, all types of models will be used for this template in future currently it handles only 
        classification models 
    
        Args:
            
            test_data (numpy): test data under which model will be trained
            test_data_id (numpy): class index or class id of the image under which model will be tested
            image_table (dictionary): dictionary to map the id to the names of the classes 
            model_name (onnx model name): Name under which the keras model will be converted to onnx and will saved 
            verbose(int): specifies the verbage of the training model
    
        Returns:
           model: Returns the infered model
    
        """
        return self


    def pytorch_train(self, device, train_loader, optimizer, epochs, loss_criteria, test_loader, classes, model_name='pytorch_model', model_type='classification', opset_version=12):
        """
        This function is used to train the model, all types of models will be used for this template in future currently it handles only 
        classification models 
    
        Args:
            device: type of device used (cpu or cuda) for model
            train_loader: training data loader under which model will be trained
            epochs (int): specifies the number of iterations that will be used for training the model
            optimizer : specifies the type of optimizer used such as Adam, SGD or RMSProp
            loss_criteria : used to define the loss for the model
            test_loader: testing data loader under which model will be tested
            classes (list): names of the classes used for training the model
            dummy_input (tuple): dummy_input to convert the model to onnx
            model_name (string): Name under which the pytorch model will be converted to onnx and will saved 
            model_type(string): Type of the model used 
            opset_version (int): ONNX opset version (default: 12)
            
        Returns:
          model: Returns the trained model which can used in inference
        """
        return self


    def pytorch_test_loss(self, device, test_loader, loss_criteria):
        """
        This function is used to generate the test loss for the model
    
        Args:
            device: type of device used (cpu or cuda) for model
            test_loader: test data under which model will be tested
            loss_criteria : used to define the loss for the model
    
        Returns:
           avg_loss: Returns the average loss 
           test_acc: Returns the test accuracy
    
        """
        return self


    def pytorch_inference(self, device, test_loader, loss_criteria, image_table, model_name='pytorch_model', opset_version=12):
        """
        This function is used to test the model, all types of models will be used for this template in future currently it handles only 
        classification models 
    
        Args:
            device: type of device used (cpu or cuda) for model
            test_loader: testing data loader under which model will be tested
            loss_criteria : used to define the loss for the model
            image_table (dictionary): dictionary to map the id to the names of the classes
            model_name (string): Name under which the pytorch model will be converted to onnx and will saved
            opset_version (int): ONNX opset version (default: 12)

        Returns:
           model: Returns the infered model
    
        """
        return self

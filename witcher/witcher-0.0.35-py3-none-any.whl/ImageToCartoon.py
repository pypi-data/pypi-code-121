############################################
#### Date   : 2021-01-17              ######
#### Author : Babak Emami             ######
#### Model  : Image_To_Cartoon        ######
############################################

###### import requirments ##################

import cv2
import numpy as np



############################################
def ImageShow(image):
    """
        input : image vectore : from filechooser
        output : image plot 


        example :
        ImageShow(image)
    """
    
    cv2.imshow("window_name", image) 
    #waits for user to press any key  
    #(this is necessary to avoid Python kernel form crashing) 
    cv2.waitKey(0)  
    #closing all open windows  
    cv2.destroyAllWindows()
    
###################################################################################

def Img_Reader(filename):
    """
        input : image path 
        output : image vector 

        example:

        Img_Reader("c:/image/a.png")
    """
    img = cv2.imread(filename)
    ImageShow(img)
    #cv2.imshow("window_name", img) 

    #waits for user to press any key  
    #(this is necessary to avoid Python kernel form crashing) 
    cv2.waitKey(0)  

    #closing all open windows  
    cv2.destroyAllWindows() 
    return img
###################################################################################

def Decolorization(img, total_color=9, report= True):
    """
        input: image vector, number of the required colour

        output decolorized image + decolorized image vector


        example:
        
        img =Img_Reader(filename) 
        Decolorization(img, total_color=9, report= False/True )
        report= True  :> return the vector
        report= False :> will not return the vector image
    """  
    # Transform the image
    data = np.float32(img).reshape((-1, 3))
    # Determine criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.001)
    # Implementing K-Means
    ret, label, center = cv2.kmeans(data, total_color, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    center = np.uint8(center)
    result = center[label.flatten()]
    result = result.reshape(img.shape)
    ImageShow(result)
    if report != False :
        return result
###################################################################################
def Edgedetection(img, line_size=7, blur_value=7, report=True):
    """
        input :image vector , size of lines(int) , size of blur valu (int), report True/False 
        output : detected image edge , and plot the edges
        report =: True :> return the vector edges

        Example:
        img =Img_Reader(filename)
        edges=Edgedetection(img)


        
    """    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.medianBlur(gray, blur_value)
    edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, line_size, blur_value)
    ImageShow(edges)
    
    if report != False :
        return edges


################################################################################
def Blurred(img,d=10,sigmaColor=200,sigmaSpace=200):
    """ 
        input : image vector, d=int ( degree of blur value) output blurred 
        image + blurred image vector

        Example

        img =Img_Reader(filename)
        Blurred=Blurred(img)
    """
    
    
    blurred=cv2.bilateralFilter(img, d=d, sigmaColor=sigmaColor,sigmaSpace=sigmaSpace)
    ImageShow(blurred)
    return blurred
    

###################################################################################
def Cartoon(bluured="0",decolor="0",mask="0"):
    """ 
        input : image bluured vector, mask=inage edgs vector
        image + blurred image vector

        Example

        img =Img_Reader(filename) 
        Blurred=Blurred(img)
        edges=Edgedetection(img)
        Cartoon=Cartoon(bluured=Blurred,mask=edges)
        Cartoon=Cartoon(bluured=Blurred,decolor=IMG_D,mask=edges)
        
    """
    if len(mask) < 2:
        mask=Edgedetection(bluured, line_size=7, blur_value=7, report=True)
    if len(decolor) > 2 :
        Cartoon=cv2.bitwise_and(bluured,decolor , mask)
    else:
        Cartoon=cv2.bitwise_and(bluured,bluured , mask)
        
    ImageShow(Cartoon)
    return Cartoon
      
###################################################################################


###################################################################################


###################################################################################

    
    
    
    

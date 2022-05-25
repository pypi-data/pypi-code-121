######################################
####### Update : 2022-05-24     ######
######################################


#from ._version import version_info, __version__
from witcher import Recommender
from witcher import StockMarket
from witcher import FileChooser
from witcher import ImageToCartoon
from witcher import Portfolio_Advisor

def How_read_Witchwr():
    """
    from witcher import FileChooser
        FileChooser.Filechooser ==>
        will read the file and will returen the filename, filepath, and dataframe for
        CSV, XLS,XLSX, SAS, and Images

        Reprort=witcher.FileChooser.filechoose()
        Report

        report.files == > file path
        report.df ==> dataframe

    from witcher import FileChooser, ImageToCartoon
        img=FileChooser.Filechooser()
        img

        image=img.df or
        image=ImageToCartoon.Img_Reader(img.files[0]) # read image and return numpy vector

        ImageToCartoon.ImageShow(image) ### Show the image
        Image_D=IMG_D=ImageToCartoon.Decolorization(image)
        Blurred=Blurred(image)
        edges=ImageToCartoon.Edgedetection(image)
        Bluured=ImageToCartoon.Blurred(image)
        Cartoon=Cartoon(bluured=Blurred,mask=edges)
        or
        Cartoon=Cartoon(bluured=Blurred,decolor=Image_D,mask=edges)


    from witcher import StockMarket
        select your stock and starting date to end date 
        df=StockMarket.Stock_Reader(stock=["AC.TO"],Period="1D",Start_date="2010-01-01",End_date="Today")
        df=StockMarket.Dataset_Spliter(df,col="Close",split=.1,Forecasting=True)
        select the column you want to analysis and pass it to the finction 
        
        
    from witcher import Portfolio_Advisor
        optimize the selected portfolio
        portfolio=Portfolio_Advisor()
        
    """
    return help(How_read_Witchwr)



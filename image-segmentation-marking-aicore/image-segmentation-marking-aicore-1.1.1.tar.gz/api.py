###############################################################################
###                    Don't change this part                               ###
###############################################################################
from image_segmentation_aicore.utils import (ImageSegmentation,               #
                                             perform_segmentation,            #
                                             decode_image,                    #
                                             save_image_to_s3)                #   
import fastapi                                                                #   
from fastapi import File, UploadFile                                          #                                        
import uvicorn                                                                #
                                                                              #
                                                                              #
model = ImageSegmentation('model.tar.gz')                                     #                                
api = fastapi.FastAPI()                                                       # 
@api.get("/image")                                                            #           
def check_alive():                                                            #
    return "Alive"                                                            #
                                                                              #      
                                                                              #
@api.post("/image")                                                           #                          
async def process_input(image_encoded: UploadFile = File(...)):               #
    image_name = image_encoded.filename # Name of the image                   #                
    image = await image_encoded.read() # Read the encoded image               # 
                                                                              #
                                                                              #
    # Start here
    # TODO Milestone 1
    # TODO 1 [Task 2]: Print the name of the image
    # TODO 2 [Task 3]: Decode the image and print its size
    # TODO 3 [Task 4]: Rename the image to `xxxx/input.png` and assing the 
    #                  output to a variable as defined in the task
    # TODO 4 [Task 4]: Get the name of the bucket and save the 
    #                  decoded image to S3


    # TODO Milestone 2
    # TODO 5 [Task 1]: Perform segmentation on the image using the function
    #                  included in this script, passing the variable called
    #                  'model' and the variable you defined earlier with the 
    #                  image decoded
    # TODO 6 [Task 2]: print the size of the segmented image


    # TODO Milestone 3
    # TODO 7 [Task 1]: Rename the image to `xxxx/output.png` and assing the 
    #                  output to a variable as defined in the task
    # TODO 8 [Task 1]: Save the segmented image to the same S3 bucket
    
###############################################################################
###                    Don't change this part                               ###
###############################################################################
    return "Images uploaded successfully"                                     #                      
                                                                              #
if __name__ == '__main__':                                                    #                                  
    uvicorn.run(api, host='0.0.0.0', port=8000, debug=True,                   #
                log_level='critical')                                         #
                                                                              #  
###############################################################################
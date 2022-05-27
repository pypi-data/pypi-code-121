import cv2
from skimage import io

def crop_face(x_axis , y_axis , width , height , path):

    image_path = io.imread(path)
    real_h,real_w,c = image_path.shape

    w = int(float(width))
    h = int(float(height))
    x = int(float(x_axis))
    y = int(float(y_axis))

    w = int(w*(real_w / 224))
    h = int(h*(real_h / 224))
    x = int(x*(real_w / 224))
    y = int(y*(real_h / 224))

    cv2.rectangle(image_path, (x, y), (x + w, y + h), (255,0,255), 2)

    y1 = 0 if y < 0 else y
    x1 = 0 if x < 0 else x 
    y2 = real_h if y1 + h > real_h else y + h
    x2 = real_w if x1 + w > real_w else x + w

    image_path = image_path[y1:y2,x1:x2,:]
    cv2.imshow("Cropped",image_path)
    cv2.waitKey(0)


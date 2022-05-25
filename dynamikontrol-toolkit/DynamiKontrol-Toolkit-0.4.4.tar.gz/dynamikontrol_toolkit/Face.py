import cv2
import numpy as np

from Tool import Get_angle_class, Get_distance_class

class Face():
    def __init__(self, face_landmarks, frame):

        self.face_landmarks = face_landmarks
        self.frame = frame
        self.frame_height, self.frame_width, c = frame.shape

        self.landmark_list = []

        for id, lm in enumerate(self.face_landmarks.landmark):
            x, y = int(lm.x * self.frame_width), int(lm.y * self.frame_height)
            self.landmark_list.append([x, y])

        # face
        left = face_landmarks.landmark[127].x * self.frame_width
        right = face_landmarks.landmark[356].x * self.frame_width
        upper = face_landmarks.landmark[10].y * self.frame_height
        lower = face_landmarks.landmark[377].y * self.frame_height
        width = right - left
        height = abs( upper - lower )  

        self.x1 = left
        self.y1 = upper
        self.width = width
        self.height = height
        self.x2 = self.x1 + width
        self.y2 = self.y1 + height
        self.center_x = (self.x1 + self.x2) / 2
        self.center_y = (self.y1 + self.y2) / 2

        # lips
        self.lips_left = face_landmarks.landmark[62].x * self.frame_width
        self.lips_right = face_landmarks.landmark[292].x * self.frame_width
        self.lips_upper = face_landmarks.landmark[13].y * self.frame_height
        self.lips_lower = face_landmarks.landmark[14].y * self.frame_height
        self.lips_width = self.lips_right - self.lips_left
        self.lips_height = abs( self.lips_upper - self.lips_lower )

        self.lips_angle = self.get_angle(13,62,14)

        self.lips = Lips( x1 = self.lips_left, y1 = self.lips_upper,
                        width = self.lips_width, height = self.lips_height,
                        angle = self.lips_angle )

        lipsUpper_list = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 308, 415, 310, 311, 312, 13, 82, 81, 80, 191, 78]
        lipsLower_list = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 78]

        self.lipsUpper_list = [ [face_landmarks.landmark[i].x, face_landmarks.landmark[i].y ] for i in lipsUpper_list ]
        self.lipsLower_list = [ [face_landmarks.landmark[i].x, face_landmarks.landmark[i].y ] for i in lipsLower_list ]

        ##### left eye
        self.left_eye_left = face_landmarks.landmark[33].x * self.frame_width
        self.left_eye_right = face_landmarks.landmark[133].x * self.frame_width
        self.left_eye_upper = face_landmarks.landmark[159].y * self.frame_height
        self.left_eye_lower = face_landmarks.landmark[145].y * self.frame_height
        self.left_eye_width = self.left_eye_right-self.left_eye_left
        self.left_eye_height = abs(self.left_eye_upper - self.left_eye_lower)

        self.left_eye = Eye( x1 = self.left_eye_left, y1 = self.left_eye_upper
                        , width = self.left_eye_width, height = self.left_eye_height
                        , face_width = self.width, face_height = self.height )

        ##### right eye
        self.right_eye_left = face_landmarks.landmark[362].x * self.frame_width
        self.right_eye_right = face_landmarks.landmark[263].x * self.frame_width
        self.right_eye_upper = face_landmarks.landmark[386].y * self.frame_height
        self.right_eye_lower = face_landmarks.landmark[374].y * self.frame_height
        self.right_eye_width = self.right_eye_right-self.right_eye_left
        self.right_eye_height = abs(self.right_eye_upper - self.right_eye_lower)

        self.right_eye = Eye( x1 = self.right_eye_left, y1 = self.right_eye_upper
                        , width = self.right_eye_width, height = self.right_eye_height
                        , face_width = self.width, face_height = self.height )

        #### left iris
        self.left_iris_right = face_landmarks.landmark[469].x * self.frame_width
        self.left_iris_left = face_landmarks.landmark[471].x * self.frame_width
        self.left_iris_upper = face_landmarks.landmark[470].y * self.frame_height
        self.left_iris_lower = face_landmarks.landmark[472].y * self.frame_height
        self.left_iris_width = self.left_iris_right-self.left_iris_left
        self.left_iris_height = abs(self.left_iris_upper - self.left_iris_lower)

        self.left_iris = Iris( x1 = self.left_iris_left, y1 = self.left_iris_upper
                        , width = self.left_iris_width, height = self.left_iris_height )

        #### right iris
        self.right_iris_right = face_landmarks.landmark[474].x * self.frame_width
        self.right_iris_left = face_landmarks.landmark[476].x * self.frame_width
        self.right_iris_upper = face_landmarks.landmark[475].y * self.frame_height
        self.right_iris_lower = face_landmarks.landmark[477].y * self.frame_height
        self.right_iris_width = self.right_iris_right-self.right_iris_left
        self.right_iris_height = abs(self.right_iris_upper - self.right_iris_lower)

        self.right_iris = Iris( x1 = self.right_iris_left, y1 = self.right_iris_upper
                        , width = self.right_iris_width, height = self.right_iris_height )

        ### eyes
        self.eyes = Eyes( self.left_eye, self.right_eye, self.left_iris, self.right_iris )

        ### face turn estimation
        self.head_pose = head_pose_estimation(self.frame_width, self.frame_height, self.face_landmarks)
        self.direction = self.head_pose.text

    def get_angle(self,p1,p2,p3):
        get_angle = Get_angle_class(self.landmark_list)
        return get_angle.angle(p1,p2,p3) 
    def get_distance(self,p1,p2):
        get_distance = Get_distance_class(self.landmark_list)
        return get_distance.distance(p1,p2) 

    def is_located_left(self):
        return self.center_x <= 0.4 * self.frame_width
    def is_located_right(self):
        return self.center_x >= 0.6 * self.frame_width
    def is_located_top(self):
        return self.center_y <= 0.4 * self.frame_height
    def is_located_bottom(self):
        return self.center_y >= 0.6 * self.frame_height

    def __repr__(self):
        return 'center_x: %.3f, center_y: %.3f, width: %.3f, height: %.3f' % (self.center_x, self.center_y, self.width, self.height)

class Lips():
    def __init__(self,x1,y1,width,height,angle):
        self.x1 = x1
        self.y1 = y1
        self.width = width
        self.height = height
        self.x2 = self.x1 + width
        self.y2 = self.y1 + height
        self.center_x = (self.x1 + self.x2) / 2
        self.center_y = (self.y1 + self.y2) / 2
        self.angle = angle
    def is_opened(self, angle = 80):
        return self.angle >= angle
    def __repr__(self):
        return 'center_x: %.3f, center_y: %.3f, width: %.3f, height: %.3f' % (self.center_x, self.center_y, self.width, self.height)

##### Eye
class Eye():
    def __init__(self,x1,y1,width,height,face_width,face_height):
        self.x1 = x1
        self.y1 = y1
        self.width = width
        self.height = height
        self.x2 = self.x1 + width
        self.y2 = self.y1 + height
        self.center_x = (self.x1 + self.x2) / 2
        self.center_y = (self.y1 + self.y2) / 2
        self.face_width = face_width
        self.face_height = face_height
    def is_closed(self, ratio = 0.06):
        return (self.height) <= (self.face_width*ratio)
    def __repr__(self):
        return 'center_x: %.3f, center_y: %.3f, width: %.3f, height: %.3f' % (self.center_x, self.center_y, self.width, self.height)

#### Iris
class Iris():
    def __init__(self,x1,y1,width,height):
        self.x1 = x1
        self.y1 = y1
        self.width = width
        self.height = height
        self.x2 = self.x1 + width
        self.y2 = self.y1 + height
        self.center_x = (self.x1 + self.x2) / 2
        self.center_y = (self.y1 + self.y2) / 2
    def __repr__(self):
        return 'center_x: %.3f, center_y: %.3f, width: %.3f, height: %.3f' % (self.center_x, self.center_y, self.width, self.height)

class Eyes():
    def __init__(self,left_eye,right_eye,left_iris,right_iris):
        self.left_eye = left_eye
        self.right_eye = right_eye
        self.left_iris = left_iris
        self.right_iris = right_iris
    def is_look_left(self, ratio = 0.4):
        look_left = (self.left_iris.center_x <= (self.left_eye.x1 + self.left_eye.width*ratio)) and (self.right_iris.center_x <= (self.right_eye.x1 + self.right_eye.width*ratio))
        return look_left
    def is_look_right(self, ratio = 0.6):
        look_right = (self.left_iris.center_x >= (self.left_eye.x1 + self.left_eye.width*ratio)) and (self.right_iris.center_x >= (self.right_eye.x1 + self.right_eye.width*ratio))
        return look_right

class head_pose_estimation():
    def __init__(self,frame_width, frame_height,face_landmarks ):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.face_landmarks = face_landmarks

        face_2d = []
        face_3d = []
        for idx, lm in enumerate(self.face_landmarks.landmark):
            if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                if idx == 1:
                    nose_2d = (lm.x * self.frame_width, lm.y * self.frame_height)
                    nose_3d = (lm.x * self.frame_width, lm.y * self.frame_height, lm.z * 3000)
                x, y = int(lm.x * self.frame_width), int(lm.y * self.frame_height)

                face_2d.append([x, y])
                face_3d.append([x, y, lm.z])       

        face_2d = np.array(face_2d, dtype=np.float64)
        face_3d = np.array(face_3d, dtype=np.float64)

        focal_length = 1 * self.frame_width
        cam_matrix = np.array([ [focal_length, 0, self.frame_height / 2],
                                [0, focal_length, self.frame_width / 2],
                                [0, 0, 1]])

        dist_matrix = np.zeros((4, 1), dtype=np.float64)

        success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

        rmat, jac = cv2.Rodrigues(rot_vec)

        angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

        self.x = angles[0] * 360
        self.y = angles[1] * 360
        self.z = angles[2] * 360

        if self.y < -15:
            self.text = "left"
        elif self.y > 15:
            self.text = "right"
        elif self.x < -10:
            self.text = "down"
        elif self.x > 20:
            self.text = "up"
        else:
            self.text = "forward"



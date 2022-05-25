import numpy as np
import math

from .Tool import Get_angle_class, Get_distance_class

class Hand():
    def __init__(self, hand_landmarks, frame, hand_angle_data, hand_knn):
            self.hand_landmarks = hand_landmarks
            self.tipIds = [4,8,12,16,20]

            self.hand_knn = hand_knn
            self.hand_angle_data = hand_angle_data

            self.frame = frame
            self.frame_height, self.frame_width, c = frame.shape

            self.xList = []
            self.yList = []
            self.landmark_list = []
            self.joint = np.zeros((21,3))

            for id, lm in enumerate(self.hand_landmarks.landmark):
                x, y = int(lm.x * self.frame_width), int(lm.y * self.frame_height)
                self.xList.append(x)
                self.yList.append(y)
                self.landmark_list.append([x, y])

                self.joint[id] = [lm.x, lm.y, lm.z]

            xmin, xmax = min(self.xList), max(self.xList)
            ymin, ymax = min(self.yList), max(self.yList)
            self.bbox = xmin, ymin, xmax-xmin, ymax-ymin

            self.gesture_dict = {0:'rock', 1:'one', 2:'two', 3:'three', 4:'four', 5:'paper',
            6:'six', 7:'rocknroll',8:'spiderman', 9:'scissors',10:'ok'}

            self.gesture = self.detect_gesture()

            self.fingers = Fingers(landmark_list= self.landmark_list, tipIds = self.tipIds)

    def get_angle(self,p1,p2,p3):
        get_angle = Get_angle_class(self.landmark_list)
        return get_angle.angle(p1,p2,p3) 
        
    def get_distance(self,p1,p2):
        get_distance = Get_distance_class(self.landmark_list)
        return get_distance.distance(p1,p2) 

    def get_webcam_distance(self):
        x = [300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 80, 75, 70, 67, 62, 59, 57]
        y = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
        coff = np.polyfit(x, y, 2)

        x1, y1 = self.landmark_list[5]
        x2, y2 = self.landmark_list[17]
 
        distance = int(math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2))
        A, B, C = coff
        distanceCM = A * distance ** 2 + B * distance + C
 
        return distanceCM

    def detect_gesture(self):
        v1 = self.joint[[0,1,2,3,0,5,6,7,0,9,10,11,0,13,14,15,0,17,18,19],:]
        v2 = self.joint[[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],:] 
        v = v2 - v1

        v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]

        self.hand_angle_data = np.arccos(np.einsum('nt,nt->n',
            v[[0,1,2,4,5,6,8,9,10,12,13,14,16,17,18],:], 
            v[[1,2,3,5,6,7,9,10,11,13,14,15,17,18,19],:])) 

        self.hand_angle_data = np.degrees(self.hand_angle_data) 

        data = np.array([self.hand_angle_data], dtype=np.float32)
        ret, results, neighbours, dist = self.hand_knn.findNearest(data, 3)
        idx = int(results[0][0])

        text = self.gesture_dict[idx].lower()

        return text


class Fingers():
    def __init__(self, landmark_list, tipIds):
        self.landmark_list = landmark_list
        self.tipIds = tipIds

    def is_thumb_up(self):
        return self.landmark_list[self.tipIds[0]][1] < self.landmark_list[self.tipIds[0] - 2][1]

    def is_index_up(self):
        return self.landmark_list[self.tipIds[1]][1] < self.landmark_list[self.tipIds[1] - 2][1]

    def is_middle_up(self):
        return self.landmark_list[self.tipIds[2]][1] < self.landmark_list[self.tipIds[2] - 2][1]

    def is_ring_up(self):
        return self.landmark_list[self.tipIds[3]][1] < self.landmark_list[self.tipIds[3] - 2][1]

    def is_pinky_up(self):
        return self.landmark_list[self.tipIds[4]][1] < self.landmark_list[self.tipIds[4] - 2][1]

    def is_up(self):
        is_up_list = [ self.is_thumb_up(), self.is_index_up(), self.is_middle_up(), self.is_ring_up(), self.is_pinky_up() ]
        return_list = []
        for i in is_up_list:
            if i is True:
                return_list.append(True)
            else:
                return_list.append(False)

        return return_list

    def get_distance(self, tipId1, tipId2):

        tipId1 = (tipId1 + 1) * 4
        tipId2 = (tipId2 + 1) * 4

        x1, y1 = self.landmark_list[tipId1]
        x2, y2 = self.landmark_list[tipId2]

        distance = math.hypot(x2 - x1, y2 - y1)

        return distance








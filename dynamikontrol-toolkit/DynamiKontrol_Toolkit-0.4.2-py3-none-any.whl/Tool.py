import math

class Get_angle_class():
    def __init__(self, landmark_list):
        self.landmark_list = landmark_list

    def angle(self,p1,p2,p3):
        x1, y1 = self.landmark_list[p1]
        x2, y2 = self.landmark_list[p2]
        x3, y3 = self.landmark_list[p3]

        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) -math.atan2(y1 - y2, x1 - x2))

        if angle < 0:
            angle += 360
        if angle > 180:
            angle = 360 - angle

        return angle

class Get_distance_class():
    def __init__(self,landmark_list):
        self.landmark_list = landmark_list

    def distance(self, p1, p2):

        x1, y1 = self.landmark_list[p1]
        x2, y2 = self.landmark_list[p2]

        distance = math.hypot(x2 - x1, y2 - y1)

        return distance
from .Tool import Get_angle_class, Get_distance_class

class Body():
    def __init__(self, pose_landmarks, frame_width, frame_height):

        self.pose_landmarks = pose_landmarks
        self.frame_width, self.frame_height = frame_width, frame_height

        self.landmark_list = []

        for id, lm in enumerate(self.pose_landmarks.landmark):
            x, y = int(lm.x * self.frame_width), int(lm.y * self.frame_height)
            self.landmark_list.append([x, y])

        self.left_arm = Arm(self.landmark_list, self.get_angle(12,14,16))
        self.right_arm = Arm(self.landmark_list, self.get_angle(11,13,15))
        self.left_leg = Leg(self.landmark_list, self.get_angle(24,26,28))    
        self.right_leg = Leg(self.landmark_list, self.get_angle(23,25,27))

    def get_angle(self,p1,p2,p3):
        get_angle = Get_angle_class(self.landmark_list)
        return get_angle.angle(p1,p2,p3) 
        
    def get_distance(self,p1,p2):
        get_distance = Get_distance_class(self.landmark_list)
        return get_distance.distance(p1,p2) 

    def is_squat(self):
        left_leg_angle = self.get_angle(24,26,28)
        right_leg_angle = self.get_angle(23,25,27)
        if left_leg_angle <= 130 and right_leg_angle <= 130:
            return "down"
        if left_leg_angle >= 160 and right_leg_angle >= 160:
            return "up"

    def is_pushup(self):
        left_arm_angle = self.get_angle(12,14,16)
        right_arm_angle = self.get_angle(11,13,15)
        if left_arm_angle <= 70 and right_arm_angle <= 70:
            return "down"
        if left_arm_angle >= 150 and right_arm_angle >= 150:
            return "up"

    def is_situp(self):
        left_hip_angle = self.get_angle(12,24,26)
        right_hip_angle = self.get_angle(11,23,25)
        if left_hip_angle >= 125 and right_hip_angle >= 125:
            return "down"
        if left_hip_angle <= 55 and right_hip_angle <= 55:
            return "up"
    
    def is_pullup(self):
        left_arm_angle = self.get_angle(12,14,16)
        right_arm_angle = self.get_angle(11,13,15)
        if left_arm_angle >= 150 and right_arm_angle >= 150:
            return "down"
        if left_arm_angle <= 60 and right_arm_angle <= 60:
            return "up"


class Arm():
    def __init__(self, landmark_list, angle):
        self.landmark_list = landmark_list
        self.angle = angle

    def is_fold(self,angle = 35):
        return self.angle < angle

class Leg():
    def __init__(self, landmark_list, angle):
        self.landmark_list = landmark_list
        self.angle = angle

    def is_fold(self,angle = 40):
        return self.angle < angle
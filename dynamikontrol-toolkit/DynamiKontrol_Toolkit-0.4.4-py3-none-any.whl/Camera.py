import cv2
import mediapipe as mp
import numpy as np
import math

from .Face import Face
from .Hand import Hand
from .Body import Body
from .Tool import Hand_knn_data


class Camera():
    def __init__(self, path:any=0, width:int = None, height:int = None ) -> None:

        self.camera = cv2.VideoCapture(path)

        if width is None or height is None:     
            self.width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        else:
            self.width = int(width)
            self.height = int(height)
        
        print("Webcam/Video가 시작되었습니다. 현재 Window의 가로는 {} pixel, 세로는 {} pixel입니다.".format( self.width, self.height))

        self.hand_angle_data, self.hand_knn = self.hand_knn_learn()

        self.mp_pose_single = self.mediapipe_pose()
        self.mp_hand_single = self.meidapipe_hand()
        self.mp_face_single = self.meidapipe_face()

    def mediapipe_pose(self):
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.5)
        return pose

    def meidapipe_hand(self):
        mp_hands = mp.solutions.hands
        mp_hand_single = mp_hands.Hands(
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5)
        return mp_hand_single

    def meidapipe_face(self):
        mp_face_mesh = mp.solutions.face_mesh
        mp_face_single = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5, 
            min_tracking_confidence=0.5)
        return mp_face_single

    def hand_knn_learn(self):
        hand_knn_data = Hand_knn_data()
        hand_gesture_learn_list = hand_knn_data.hand_gesture_learn_list

        file = np.reshape(hand_gesture_learn_list, (110,16))
        
        hand_angle_data = file[:,:-1].astype(np.float32)
        label = file[:, -1].astype(np.float32)
        knn = cv2.ml.KNearest_create()
        knn.train(hand_angle_data, cv2.ml.ROW_SAMPLE, label)

        return hand_angle_data, knn

    def is_opened(self, close_key: int or str = 27) -> bool:
        if not self.camera.isOpened():
            return False

        ret, img = self.camera.read()

        if not ret:
            return False

        if len(str(close_key)) == 1:
            close_key = ord(close_key)
            if cv2.waitKey(20) & 0xFF == close_key:
                return False
        else:
            if cv2.waitKey(20) & 0xFF == close_key:
                return False

        self.frame = img
        self.frame = cv2.resize(self.frame, (self.width, self.height), interpolation=cv2.INTER_CUBIC)

        return True

    def get_frame(self, mirror_mode = True):

        if mirror_mode is True:
            self.frame = cv2.flip(self.frame, 1)

        return self.frame

    def show(self, frame, window_name = "Window"):
        return cv2.imshow(window_name, frame)

    def get_angle(self,p1,p2,p3):
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) -math.atan2(y1 - y2, x1 - x2))

        if angle < 0:
            angle += 360
        if angle > 180:
            angle = 360 - angle

        return angle

    def get_distance(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        distance = math.hypot(x2 - x1, y2 - y1)

        return distance

    def show_text(self, x = 30, y = 50, font_size = 1, color = "black", text = "text"):
        text = str(text)

        if color == "green":
            color = (0,255,0)
        elif color == "blue":
            color = (255,0,0)
        elif color == "red":
            color = (0,0,255)
        elif color == "black":
            color = (0,0,0)
        elif color == "white":
            color = (255,255,255)

        self.frame = cv2.putText(self.frame, text, org=(int(x), int(y)),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=font_size, color=color, thickness=3)

    #### draw face

    def draw_faces(self, faces):
        for face in faces:
            cv2.rectangle(self.frame, (int(round(face.x1)), int(round(face.y1))),
                    (int(round(face.x2)),int(round(face.y2))),
                    (0,255,0), 3)
    
    def draw_lips(self, faces):
        for face in faces:
            for i in range( len( face.lipsUpper_list )):
                face.lipsUpper_list[i][0] =  round(face.lipsUpper_list[i][0] * self.width)
                face.lipsUpper_list[i][1] =  round(face.lipsUpper_list[i][1] * self.height)
                face.lipsLower_list[i][0] =  round(face.lipsLower_list[i][0] * self.width)
                face.lipsLower_list[i][1] =  round(face.lipsLower_list[i][1] * self.height)

            lips_upper_points = np.array( face.lipsUpper_list, np.int32 )
            lips_lower_points = np.array( face.lipsLower_list, np.int32 )

            self.frame = cv2.polylines( self.frame, [lips_upper_points], False, (0,255,0), 2 )
            self.frame = cv2.polylines( self.frame, [lips_lower_points], False, (0,255,0), 2 )

    def draw_eyes(self, faces):
       for face in faces:
            left_eye_c_x = round(face.left_eye.center_x)
            left_eye_c_y = round(face.left_eye.center_y)
            left_eye_width = round(face.left_eye.width*0.5)
            left_eye_height = round(face.left_eye.height*0.5)

            right_eye_c_x = round(face.right_eye.center_x)
            right_eye_c_y = round(face.right_eye.center_y)
            right_eye_width = round(face.right_eye.width*0.5)
            right_eye_height = round(face.right_eye.height*0.5)

            left_eye_points = cv2.ellipse2Poly( (left_eye_c_x, left_eye_c_y),(left_eye_width,left_eye_height), 0, 0, 360, 30 )
            self.frame = cv2.polylines( self.frame, [left_eye_points], False, (0,255,0), 2 )

            right_eye_points = cv2.ellipse2Poly( (right_eye_c_x, right_eye_c_y),(right_eye_width,right_eye_height), 0, 0, 360, 30 )
            self.frame = cv2.polylines( self.frame, [right_eye_points], False, (0,255,0), 2 )

    def draw_irides(self, faces):
       for face in faces:
            self.frame = cv2.circle( self.frame, ( round(face.left_iris.center_x) , round(face.left_iris.center_y) ),
                                round( min( [face.left_iris.width, face.left_iris.height] ) * 0.5 ), (0,255,0), 2 )
            self.frame = cv2.circle( self.frame, ( round(face.right_iris.center_x) , round(face.right_iris.center_y) ),
                                round( min( [face.left_iris.width, face.left_iris.height] ) * 0.5 ), (0,255,0), 2 )

    def show_direction(self, faces):
        for face in faces:
            self.frame = cv2.putText(self.frame, face.head_pose.text, org=(int(face.x1), int(face.y1 - 15)),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 255, 0), thickness=2)

    #### draw hands

    def draw_hands(self, hands):
        thumb_list = [0,1,2,3,4]
        index_list = [0,5,6,7,8]
        middle_list = [9,10,11,12]
        ring_list = [13,14,15,16]
        pinky_list = [0,17,18,19,20]
        bridge_list = [5,9,13,17]

        temp_list = [ thumb_list, index_list, middle_list, ring_list, pinky_list, bridge_list ]

        for hand in hands:
            for j in range(len(temp_list)):
                for i in range(len(temp_list[j])-1):
                    self.frame = cv2.line( self.frame, ( hand.landmark_list[temp_list[j][i]][0] , hand.landmark_list[temp_list[j][i]][1] ),
                                        ( hand.landmark_list[temp_list[j][i+1]][0] , hand.landmark_list[temp_list[j][i+1]][1] ), (0,255,0), 3 )

            for i in range(21):
                self.frame = cv2.circle(self.frame, (hand.landmark_list[i][0] , hand.landmark_list[i][1]), 4, (255, 0, 255), cv2.FILLED)

    def show_gesture(self, hands):
        for hand in hands:
            
            text = hand.detect_gesture()
            gesture = hand.gesture_dict

            if text in gesture.values():
                self.frame = cv2.putText(self.frame, text.upper(), org=(int(hand.landmark_list[0][0]), int(hand.landmark_list[0][1] + 25)),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 255, 255), thickness=2)
    

    def show_distance(self, hands):
        for hand in hands:
            x,y,w,h = hand.bbox
            distanceCM = hand.get_distance()
            self.frame = cv2.rectangle(self.frame,(x,y), (x+w, y+h), (255,0,255),3 )
            self.frame = cv2.putText(self.frame, text= f'{int(distanceCM)} cm', org=(int(x+5), int(y-10)),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 255, 255), thickness=2)

    ### draw body

    def draw_body(self, body):
        face_upper_list = [8,6,5,4,0,1,2,3,7]
        face_lower_list = [10,9]
        hand_list = [18,16,14,12,11,13,15,17]
        left_finger_list = [18,20,16,22]
        right_finger_list = [17,19,15,21]
        body_list = [12,24,23,11]
        left_leg = [24,26,28,30,32,28]
        right_leg = [23,25,27,29,31,27]

        temp_list = [ face_upper_list, face_lower_list, hand_list, left_finger_list, right_finger_list, body_list, left_leg, right_leg ]

        for body in body:
            for j in range(len(temp_list)):
                for i in range(len(temp_list[j])-1):
                    self.frame = cv2.line( self.frame, ( body.landmark_list[temp_list[j][i]][0] , body.landmark_list[temp_list[j][i]][1] ),
                                        ( body.landmark_list[temp_list[j][i+1]][0] , body.landmark_list[temp_list[j][i+1]][1] ), (0,255,0), 3 )

            for i in range(33):
                self.frame = cv2.circle(self.frame, (body.landmark_list[i][0] , body.landmark_list[i][1]), 4, (255, 0, 255), cv2.FILLED)


    ### detect_face

    def detect_face(self, frame, draw_face = True, draw_lips = True, draw_eyes = True, draw_irides = True,
                    show_direction = False) -> object or None:

        face = []
        max_num_face = 1 

        frame.flags.writeable = False
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.mp_face_single.process(frame)

        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:  
                face.append( Face(face_landmarks, frame) )

        if draw_face:
            self.draw_faces(face)
        if draw_lips:
            self.draw_lips(face)
        if draw_eyes:
            self.draw_eyes(face)
        if draw_irides:
            self.draw_irides(face)
        if show_direction:
            self.show_direction(face)

        if len(face) == 1 and max_num_face == 1:
            return face[0]

        return None

    def detect_faces(self, frame, max_num_faces = 99, draw_faces =True, draw_lips = True, draw_eyes = True, draw_irides = True,
                    show_direction = False) -> list:
 
        mp_face_mesh = mp.solutions.face_mesh

        faces = []

        with mp_face_mesh.FaceMesh(
            max_num_faces=max_num_faces,
            refine_landmarks=True,
            min_detection_confidence=0.4, 
            min_tracking_confidence=0.5) as face_mesh:

                frame.flags.writeable = False
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(frame)

                frame.flags.writeable = True
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                if results.multi_face_landmarks:
                    for face_landmarks in results.multi_face_landmarks:  
                        faces.append( Face(face_landmarks,frame) )

        if draw_faces:
            self.draw_faces(faces)
        if draw_lips:
            self.draw_lips(faces)
        if draw_eyes:
            self.draw_eyes(faces)
        if draw_irides:
            self.draw_irides(faces)
        if show_direction:
            self.show_direction(faces)

        return faces

    ### detect_hand
    def detect_hand(self, frame, draw_hand = True, show_gesture = False, show_distance = False):
        mp_hands = mp.solutions.hands

        hand = []
        max_num_hand = 1

        frame.flags.writeable = False
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.mp_hand_single.process(frame)

        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                hand.append( Hand(hand_landmarks, frame, self.hand_angle_data, self.hand_knn) )

        if draw_hand:
            self.draw_hands(hand)
        if show_gesture:
            self.show_gesture(hand)
        if show_distance:
            self.show_distance(hand)

        if len(hand) == 1 and max_num_hand == 1:
            return hand[0]

        return None

    def detect_hands(self, frame, max_num_hands = 99, draw_hands = True, show_gesture = False, show_distance = False):
        mp_hands = mp.solutions.hands

        hands = []

        with mp_hands.Hands(
            max_num_hands=max_num_hands,
            model_complexity=0,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5) as detect_hands:

                frame.flags.writeable = False
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = detect_hands.process(frame)

                frame.flags.writeable = True
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        hands.append( Hand(hand_landmarks, frame, self.hand_angle_data, self.hand_knn) )

        if draw_hands:
            self.draw_hands(hands)
        if show_gesture:
            self.show_gesture(hands)
        if show_distance:
            self.show_distance(hands)

        return hands

    def detect_body(self, frame, draw_body = True):
        body = []

        frame.flags.writeable = False
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.mp_pose_single.process(frame) 

        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            body.append( Body(results.pose_landmarks, self.width, self.height) )

        if draw_body:
            self.draw_body(body)

        if len(body) == 1:
            return body[0]

        return None





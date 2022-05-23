import os
import contextlib

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    #importations utiles sans les messages des librairies
    import cv2
    import matplotlib
    import numpy as np
    import matplotlib.pyplot as plt
    import mediapipe as mp
    import mediapipe.python.solutions.face_mesh_connections as fm
    from IPython.display import clear_output

class Nexd_utils:
    def __init__(self, *args, **kwargs):
        super(Nexd_utils, self).__init__()
        self.__author = "importFourmi"
        self.__args = args
        self.__kwargs = kwargs


    def ext_list(self, path=None, list_ext=[".png", ".jpg", ".jpeg"]):
        """
        Fonction qui liste les extensions d'un dossier.

        :param path: path du dossier (None si dossier courant)
        :param (list_ext): liste des extensions possibles (par défaut: liste des images)

        :return: la liste des chemins
        """

        return np.array([file for file in os.listdir(path) for ext in list_ext if file.endswith(ext)])


    def extension_rect(self, coords, coef):
        """
        Fonction qui multiplie les coordonnées par un coefficient (0: pas d'extension, 0.5: size*2, 1:size*3, etc.).
        Le format est le suivant: [[xmin, ymin, xmax, ymax]].

        :param coords: liste de coordonnées de rectangles
        :param coef: coefficient multiplicateur

        :return: les nouvelles coordonnées
        """

        # où mettre les nouvelles coordonnées
        result = []

        # si il y a qu'un seul rectangle
        if len(np.array(coords).shape) == 1:
            coords = np.array([coords])

        for coord in coords:

            width = coord[2] - coord[0]
            height = coord[3] - coord[1]

            result.append([ coord[0] - int((width*coef)/2),
                            coord[1] - int((height*coef)/2),
                            coord[2] + int((width*coef)/2),
                            coord[3] + int((height*coef)/2)
                          ] )

        return np.array(result)


class Data_utils:
    def __init__(self, *args, **kwargs):
        super(Data_utils, self).__init__()
        self.__author = "importFourmi"
        self.__args = args
        self.__kwargs = kwargs


    def data_draw_pixels(self, x, y, value=None, classes=None, title=None, xlabel=None, ylabel=None):
        """
        Fonction qui dessine les points.

        :param x: liste des x à dessiner
        :param y: liste des y à dessiner
        :param (value): liste des valeurs pour chaque point
        :param (classes): nom des classes de chaque point si value n'est pas explicite
        :param (title): titre de l'image
        :param (xlabel): xlabel de l'image
        :param (ylabel): ylabel de l'image

        :return: None
        """

        # si il y a un titre on l'affiche
        if title:
            plt.title(title)

        # si il y a un xlabel on l'affiche
        if xlabel:
            plt.xlabel(xlabel)

        # si il y a un ylabel on l'affiche
        if ylabel:
            plt.ylabel(ylabel)

        # on affiche les points
        scatter = plt.scatter(x, y, c=value, cmap=plt.cm.Set1)

        # si on a des valeurs
        if not(value is None):

            # si les valeurs ne sont pas labellisées
            if classes is None:
                classes = [str(val) for val in set(value)]

            # on ajoute la légende
            plt.legend(handles=scatter.legend_elements()[0], labels=classes)

        plt.show()


class Img_utils:
    def __init__(self, *args, **kwargs):
        super(Img_utils, self).__init__()
        self.__author = "importFourmi"
        self.__args = args
        self.__kwargs = kwargs


    def im_load(self, img_path):
        """
        Fonction qui télécharge l'image en RGB.

        :param img_path: path de l'image

        :return: l'image
        """

        if not(os.path.isfile(img_path)):
            print("Image not found")
            return np.array([])

        else :
            # l'image est créée avec OpenCV
            img = cv2.imread(img_path)

            # on met de la bonne couleur
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


    def im_show(self, img, title="", dynamic=False, shape=True):
        """
        Fonction qui affiche l'image.

        :param img: image
        :param (title): titre de l'image
        :param (dynamic): permet de mettre l'image à jour
        :param (shape): permet de dire si on affiche la taille

        :return: None
        """

        img = img.copy()

        if shape:
            # on affiche les dimensions de l'image
            print(np.array(img).shape)

        # si il y a un titre on l'affiche
        if title:
            plt.title(title)

        # on n'affiche pas les axes
        plt.axis('off')

        # efface l'ancien output
        if dynamic:
            clear_output(wait=True)

        plt.imshow(img)
        plt.show()


    def im_draw_pixels(self, img, x, y, value=None, color=[0, 255, 0], radius=None):
        """
        Fonction qui dessine les pixels sur l'image.

        :param img: image
        :param x: liste des x à dessiner
        :param y: liste des y à dessiner
        :param (value): liste des valeurs pour chaque pixel
        :param (color): couleur des pixels si il n'y a pas de valeurs pour chaque pixel
        :param (radius): radius des pixels

        :return: l'image avec les pixels
        """

        img = img.copy()

        if radius is None:
            radius = int(0.01*max(img.shape[0], img.shape[1]))

        if not(value is None):
            # normalise linéairement les données entre 0.0 et 1.0
            norm = matplotlib.colors.Normalize(vmin=min(value), vmax=max(value))

            # transforme les valeurs en couleurs
            rgba = plt.get_cmap('inferno')(norm(value.astype(np.float64)))

            # on dessine un cercle de 1% de la taille de l'image (de la couleur de la valeur)
            for i in range(len(x)):
                img = cv2.circle(img, (int(x[i]), int(y[i])), radius, rgba[i][:-1]*255, -1)

        else:
            # on dessine un cercle (en vert) de 1% de la taille de l'image
            for i in range(len(x)):
                img = cv2.circle(img, (int(x[i]), int(y[i])), radius, color, -1)

        return img


    def im_draw_rect(self, img, coords, color=(255, 0, 0), thickness=1):
        """
        Fonction qui dessine des rectangles sur une image.

        :param img: image sur laquelle on veut dessiner des rectangles
        :param coords: liste des coordonnées des rectangles (x_start, y_start, x_end, y_end)
        :param (color): couleur des rectangles à dessiner
        :param (thickness): épaisseur des rectangles (-1 pour un rectangle plein)

        :return: l'image avec les rectangles
        """
        img = img.copy()

        # si il y a qu'un seul rectangle
        if len(np.array(coords).shape) == 1:
            coords = np.array([coords])

        for coord in coords:
            # on dessine tous les rectangles
            img = cv2.rectangle(img, (coord[0], coord[1]), (coord[2], coord[3]), color, thickness)
        return img


    def im_redim(self, img, size=(500,500), interpolator=cv2.INTER_LANCZOS4):
        """
        Fonction qui redimensionne une image.

        :param img: liste des x à dessiner
        :param (size): taille de la nouvelle image
        :param (interpolator): interpolateur qui gère les pixels

        :return: la nouvelle image
        """

        return cv2.resize(img.copy(), (int(size[0]),int(size[1])), interpolation=interpolator)


    def im_stack(self, list_img):
        """
        Fonction qui retourne la superposition des images.

        :param list_img: liste des x à dessiner

        :return: le résultat de la superposition
        """

        return np.stack(list_img, axis=3).mean(axis=3)/255


    def im_affine_transform(self, img, pts1, pts2):
        """
        Fonction qui applique une transormation affine sur l'image.

        :param img: image
        :param pts1: liste des coordonnées d'origine des trois points
        :param pts2: liste des coordonnées de destinations des trois points

        :return: l'image transformée
        """
        rows, cols = img.shape[:2]

        M = cv2.getAffineTransform(np.float32(pts1), np.float32(pts2))
        return cv2.warpAffine(img.copy(), M, (cols, rows))


    def im_save(self, filename, img):
        """
        Fonction qui permet d'enregistrer une image.
        :param filename: string représentant le nom de l'image
        :param img: image à enregistrer

        :return: None
        """

        # ordre normal des paramètres
        if isinstance(filename, str) and not isinstance(img, str):
            plt.imsave(filename, img)

        # si on se trompe sur l'ordre des paramètres
        elif isinstance(img, str) and not isinstance(filename, str):
            plt.imsave(img, filename)



class Landmarks:
    def __init__(self, *args, **kwargs):
        super(Landmarks, self).__init__()
        self.__author = "importFourmi"
        self.__args = args
        self.__kwargs = kwargs

        self.parts_face = self.__set_parts_face__()
        self.set_landmarks_detector()
        self.__set_parts_face_global__()


    def __frozenset_list__(self, pFrozenset):
        """
        Fonction qui transforme un frozenset en liste de points.

        :param frozenset: frozenset avec les points

        :return: la liste des points
        """

        return sorted(set(np.array(list(pFrozenset)).reshape(-1)))


    def __set_parts_face__(self):
        """
        Fonction qui renvoie pour chaque partie du visage les landmarks correspondants.

        :return: le dictionnaire des parties du visage
        """

        return {
            "LEFT_EYE": self.__frozenset_list__(fm.FACEMESH_LEFT_EYE),
            "LEFT_EYEBROW": self.__frozenset_list__(fm.FACEMESH_LEFT_EYEBROW),
            "LEFT_IRIS": self.__frozenset_list__(fm.FACEMESH_LEFT_IRIS),
            "LIPS": self.__frozenset_list__(fm.FACEMESH_LIPS),
            "RIGHT_EYE": self.__frozenset_list__(fm.FACEMESH_RIGHT_EYE),
            "RIGHT_EYEBROW": self.__frozenset_list__(fm.FACEMESH_RIGHT_EYEBROW),
            "RIGHT_IRIS": self.__frozenset_list__(fm.FACEMESH_RIGHT_IRIS),
        }


    def set_landmarks_detector(self, max_num_faces=1, min_detection_confidence=0.9):
        """
        Fonction qui permet d'initialiser notre détecteur.

        :param (max_num_faces): nombre maximum de visages à détecter
        :param (min_detection_confidence): coeficient de certitude de détection

        :return: None
        """

        self.__landmarks_detector__ = mp.solutions.face_mesh.FaceMesh(max_num_faces=max_num_faces,
                                                                  refine_landmarks=True,
                                                                  min_detection_confidence=min_detection_confidence,
                                                                  static_image_mode=True,
                                                                 )


    def extract_landmarks(self, img, normalized=True):
        """
        Fonction qui retourne les landmarks d'un visage détécté sous le format [x, y, z(profondeur de chaque repère)].

        :param img: image
        :param (normalized): x et y normalisés si True / x et y en pixels si False

        :return: une liste de dimensions (478, 3) si un visage est détécté
        """

        results = self.__landmarks_detector__.process(img)
        if results.multi_face_landmarks:
            rows, cols = img.shape[:2]

            list_landmarks = list(results.multi_face_landmarks[0].landmark)
            if normalized:
                return np.array([[i.x, i.y, i.z] for i in list_landmarks])

            else:
                return np.array([[i.x*cols, i.y*rows, i.z] for i in list_landmarks])
        else:
            return np.array([])


    def parts_face_mean(self, img):
        """
        Fonction qui retourne un dictionnaire avec les coordonnées du centre de chaque partie du visage.

        :param img: image

        :return: le dictionnaire si un visage est détécté
        """

        landmarks = self.extract_landmarks(img)
        if np.any(landmarks):
            center_dic = {}
            for key, value in self.parts_face.items():
                center_dic[key] = np.array([landmarks[ld] for ld in value]).mean(axis=0)
            return center_dic

        else:
            return np.array([])


    def __parts_face_selected__(self, img):
        """
        Fonction qui retourne un dictionnaire avec le centre des lèvres et des iris.

        :param img: image

        :return: le dictionnaire si un visage est détécté
        """

        dictionnaire = self.parts_face_mean(img)
        if np.any(dictionnaire):
            select = ["LEFT_IRIS", "LIPS", "RIGHT_IRIS"]
            return {key: value for key, value in dictionnaire.items() if key in select}

        else:
            return np.array([])


    def __set_parts_face_global__(self, coef=0.3):
        """
        Fonction qui intialise les positions d'un visage moyen.

        :param (coef): coeficient de zoom ou dézoom

        :return: None
        """

        D = {}
        D["LEFT_IRIS"] = [0.65, 0.42]
        D["LIPS"] = [0.50,  0.75]
        D["RIGHT_IRIS"] = [0.35, 0.42]

        pts = np.array([D["LEFT_IRIS"], D["LIPS"], D["RIGHT_IRIS"]])
        self.__parts_face_global__ = (pts+coef/2)/(1+coef)


    def align_face(self, img):
        """
        Fonction qui aligne un visage toujours dans la même position.

        :param img: image

        :return: l'image alignée
        """

        rows, cols = img.shape[:2]

        pts1 = self.__parts_face_selected__(img)

        if np.any(pts1):

            pts1 = np.array([pts1["LEFT_IRIS"][:2], pts1["LIPS"][:2], pts1["RIGHT_IRIS"][:2]])
            pts2 = self.__parts_face_global__.copy()

            for i in range(3):
                pts1[i][0] *= cols
                pts1[i][1] *= rows

                pts2[i][0] *= cols
                pts2[i][1] *= rows


            M = cv2.getAffineTransform(np.float32(pts1), np.float32(pts2))
            return cv2.warpAffine(img.copy(), M, (cols, rows))

        else:
            return np.array([])



class Nexd(Nexd_utils, Data_utils, Img_utils, Landmarks):

    def __init__(self, *args, **kwargs):
        super(Nexd, self).__init__()
        self.__author = "importFourmi"
        self.__args = args
        self.__kwargs = kwargs
        self.methods = [f for f in dir(self) if not f.startswith('_')]


        if self.__kwargs.get("verbose") == 1:
            print("Bienvenue dans Nexd, les fonctions disponibles sont les suivantes et vous pouvez utiliser help(fonction) pour plus d'informations :")
            for fonction in self.methods:
                print("  -", fonction)

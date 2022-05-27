import cv2
from uuid import uuid1
import numpy as np
import torch
from torchvision import transforms
from PIL import Image
import json
from json import JSONEncoder
import pathlib
import os
from fro_AI.face_evoLve.align.align_trans import get_reference_facial_points, warp_and_crop_face
from fro_AI.face_evoLve.align.detector import detect_faces
from fro_AI.face_evoLve.backbone.model_irse import IR_50
from fro_AI.utils.generic_utils import Logger
from base64 import b64encode
from base64 import b64decode
import datetime
try:
    from torch.hub import load_state_dict_from_url
except ImportError:
    from torch.utils.model_zoo import load_url as load_state_dict_from_url
from tqdm.auto import tqdm

model_urls = {
    'ir50':
    'http://gz.chuangfeigu.com:8087/fro_AI/models/backbone_ir50_asia-c3d1a901.pth',
}


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


def img2tensor(rgb):
    mean = np.array([0.5, 0.5, 0.5])
    std = np.array([0.5, 0.5, 0.5])
    # rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    tensor = transforms.functional.to_tensor(rgb)
    tensor = transforms.functional.normalize(tensor, mean, std)
    tensor = torch.unsqueeze(tensor, 0)
    return tensor


def unit_vector(input, axis=1):
    norm = torch.norm(input, 2, axis, True)
    output = torch.div(input, norm)
    return output


def run_inference(model, device, img):
    """
    img: bgr format
    """
    model.eval()
    tensor = img2tensor(img)
    with torch.no_grad():
        tensor = tensor.to(device)
        output = model(tensor)
    return unit_vector(output)


reference = get_reference_facial_points(default_square=True)
crop_size = 112


def align(img, crop_size):
    """
    从img中检测人脸，将其提取出来并对齐。注意下面的代码只提取img中的一张人脸。
    """
    _, landmarks = detect_faces(img)
    if len(landmarks) == 0:
        return

    facial5points = [[landmarks[0][j], landmarks[0][j + 5]] for j in range(5)]
    warped_face = warp_and_crop_face(np.array(img),
                                     facial5points,
                                     reference,
                                     crop_size=(crop_size, crop_size))
    return warped_face


def timestr():
    return str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    else:
        print(f'"{path}" 目录已存在')
        return False


class FaceRecognizer(Logger):
    """
    一个简单的人脸识别模块

    Parameters
    ----------
    path: str, optional
        模型参数路径，若为None，则自动从服务器下载模型参数，否则从指定路径载入。
    """
    def __init__(self, path=None):
        super().__init__()
        self._db = {}
        self._device = torch.device(
            "cuda:0" if torch.cuda.is_available() else "cpu")
        self._model = IR_50([112, 112])
        if path is None:
            state_dict = load_state_dict_from_url(
                model_urls['ir50'],
                map_location=torch.device(
                    "cuda:0" if torch.cuda.is_available() else "cpu"),
                check_hash=True)
            self._model.load_state_dict(state_dict)
        else:
            self._model.load_state_dict(
                torch.load(
                    path,
                    map_location=torch.device(
                        "cuda:0" if torch.cuda.is_available() else "cpu")))

        self._model = self._model.to(self._device)

    def _preprocess(self, bgr):
        if type(bgr) == str:
            bgr = cv2.imread(bgr)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(rgb)
        try:
            aligned_face = align(im_pil, crop_size)
        except:
            aligned_face = None
        return aligned_face

    def get_user_name(self, user_id):
        """
        返回用户名

        Parameters
        ----------
        user_id: str
            用户ID
        
        Returns
        -------
        name
            如果user_id存在，则返回用户名；若不存在，则返回None
        """
        if user_id not in self._db:
            return
        else:
            return self._db[user_id]['name']

    def get_user_image(self, user_id):
        """
        返回用户头像

        Parameters
        ----------
        user_id: str
            用户ID
        
        Returns
        -------
        image
            如果user_id存在，则返回BGR格式图像；若不存在，则返回None
        """
        if user_id not in self._db:
            return None
        else:
            b64string = self._db[user_id]['imgs'][0]
            raw_img = b64decode(b64string)
            data_encode = np.asarray(bytearray(raw_img), dtype='uint8')
            img_decoded = cv2.imdecode(data_encode, cv2.IMREAD_COLOR)
            return img_decoded

    def get_user_ids(self):
        """
        返回数据库中的所有用户ID

        Returns
        -------
        list
            由用户ID组成的列表
        """
        return list(self._db)

    def _register(self, img, id, name):
        aligned_face = self._preprocess(img)
        if aligned_face is not None:
            ft = run_inference(self._model, self._device, aligned_face)
        else:
            self.logger.warning('未在输入图像中找到人脸')
            return False

        bgr = cv2.cvtColor(aligned_face, cv2.COLOR_RGB2BGR)
        bimg = bytes(cv2.imencode('.bmp', bgr)[1])
        b64bytes = b64encode(bimg)
        b64string = b64bytes.decode('utf-8')

        self._db[id] = {'name': name, 'features': [ft], 'imgs': [b64string]}
        return True

    def register(self, img, user_id=None, user_name=None):
        """
        人脸注册

        Parameters
        ----------
        img
            BGR格式的图像 或 图像路径
        user_id: str, optional
            用户ID
        user_name: str, optional
            用户名

        Returns
        -------
        ret: bool
            True: 注册成功, False: 注册失败
        id: str
            刚注册了的用户ID

        Raises
        ------
        TypeError
            如果 `user_id` 或 `user_name` 的类型不是 `str`或 `NoneType`
        """
        id = -1
        if user_id is not None:
            if type(user_id) == str:
                id = user_id
            else:
                raise TypeError('user_id must be str')
        else:
            id = str(uuid1())

        if user_name is not None:
            if type(user_name) == str:
                name = user_name
            else:
                raise TypeError('user_name must be str')
        else:
            name = 'anonymity'

        ret = self._register(img, id, name)

        return ret, id

    def deregister(self, user_id):
        """
        删除用户

        Parameters
        ----------
        user_id: str
            需要从数据库中删除的用户ID
        """
        self._db.pop(user_id, -1)

    def recognize(self, img, threshold=1.4):
        """
        人脸识别

        Parameters
        ----------
        img
            BGR格式的图像 或 图像路径
        threshold: float
            检测阈值，普通用户无需理会。

        Returns
        -------
        errno: int
            0： 识别成功
            -1: 人脸数据库为空
            -2: 输入图像中检测不到人脸
            -3: 未找到匹配对象
        id: str
            当 errno 为0时：识别到的用户ID，当 errno 为-3时：最接近的用户ID
        name: str
            当 errno 为0时：识别到的用户名，当 errno 为-3时：最接近的用户名
        """

        errno = -1
        id = -1
        name = "unknown"

        if len(self._db) == 0:
            self.logger.warning(
                '人脸数据库中并没有任何人脸数据！请使用`register()`方法添加人脸数据再进行识别。')
            return -1, id, name

        aligned_face = self._preprocess(img)
        if aligned_face is not None:
            encoding = run_inference(self._model, self._device, aligned_face)
        else:
            self.logger.warning('未在输入图像中找到人脸')
            return -2, id, name

        min_dist = 100

        for i, v in self._db.items():
            enc = v['features'][0]
            dist = torch.norm(enc - encoding)**2
            if dist < min_dist:
                min_dist = dist
                id = i

        if min_dist > threshold:
            errno = -3
        else:
            errno = 0

        name = self._db[id]['name']
        self.logger.debug(f'min_dist: {min_dist} id: {id} name: {name}')

        return errno, id, name

    def verify(self, img, user_id, threshold=1.4):
        """
        人脸认证

        Parameters
        ----------
        img
            BGR格式的图像 或 图像路径
        user_id: str
            用户ID
        threshold: float
            检测阈值，普通用户无需理会。

        Returns
        -------
        errno: int
            0: `img` 中的用户和 `user_id` 对应的用户是同一人
            -1: `user_id` 不在人脸数据库中
            -2: 输入图像中检测不到人脸
            -3: 认证失败
        """

        if user_id not in self._db:
            self.logger.warning(f'user_id: "{user_id}" 不在人脸数据库中')
            return -1

        aligned_face = self._preprocess(img)
        if aligned_face is not None:
            encoding = run_inference(self._model, self._device, aligned_face)
        else:
            self.logger.warning('未在输入图像中找到人脸')
            return -2

        dist = torch.norm(self._db[user_id]['features'][0] - encoding)**2

        if dist < threshold:
            errno = 0
        else:
            errno = -3

        return errno

    def _save_database(self, path):
        dump_db = {}
        for k, v in self._db.items():
            ft_np = v['features'][0].cpu().numpy()
            tmp = {'name': v['name'], 'features': [ft_np], 'imgs': v['imgs']}
            dump_db[k] = tmp
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(dump_db,
                      f,
                      indent=4,
                      separators=(',', ':'),
                      cls=NumpyArrayEncoder)

    def save_database(self, path=None, progress=True):
        """
        保存人脸数据库

        Parameters
        ----------
        path: str, optional
            当path为None时，会自动创建一个'face_db-<timestamp>'的文件夹，数据会保存在该文件夹下，包括图片。
            当path后缀为'.json'，数据会保存在json文件内，不含图片。
            当path不为None且后缀不为'.json'，则数据会保存在path文件夹内，包括图片。
        progress: bool, optional
            True: 显示图片保存进度，False: 不显示进度。

        Returns
        -------
        bool
            True: 保存成功
            False: 保存失败
        """
        if path is None:
            path = 'face_db-' + timestr()
        elif path[-5:] == '.json':
            self._save_database(path)
            print(f'数据已保存到{path}')
            return True

        ret = create_dir(path)
        if ret:
            pbar = tqdm(self._db.items(), unit='张', disable=not progress)
            for k, v in pbar:
                raw_img = b64decode(v['imgs'][0])
                fp = os.path.join(path, k + '-' + v['name'] + '.bmp')
                pbar.set_description(f'保存 {fp}')
                with open(fp, 'wb') as f:
                    f.write(raw_img)
            db_json = os.path.join(path, path + '.json')
            self._save_database(db_json)
            print(f'数据已保存到 "{path}" 目录下')
        return ret

    def _load_database(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        for k, v in raw.items():
            ft_list = []
            for ft in v['features']:
                ft_list.append(
                    torch.from_numpy(np.asarray(ft)).to(self._device))
            v['features'] = ft_list
        return raw

    def load_database(self, path):
        """
        载入人脸数据库

        Parameters
        ----------
        path: str
            人脸数据库(*.json)的路径
        """
        self._db = self._load_database(path)

    def add_database(self, path):
        add = self._load_database(path)
        for k, v in add.items():
            self._db[k] = v

    def _parse_id(self, name_id):
        i = name_id.find('-')
        if i != -1:
            id = name_id[:i]
        else:
            id = str(uuid1())
        if i < len(name_id) - 1:
            name = name_id[i + 1:]
        else:
            name = 'unknow'
        return name, id

    def batch_register(self, dir, parse_id=True, progress=True):
        """
        人脸批注册

        Parameters
        ----------
        dir: str
            人脸图片文件夹路径
        parse_id: bool, optional
            True: 从图片名称中解释用户名和用户id，图片名称格式要求为'id-name'。
            False: 从图片名称中获取用户名，用户id将自动生成。
        progress: bool, optional
            True: 显示进度，False: 不显示进度。
        
        Returns
        -------
        dict
            由{用户ID-用户名}组成的字典，字典里的用户ID都是刚注册成功的用户ID
        """
        data_dir = pathlib.Path(dir)
        face_imgs = list(data_dir.glob('*.jpg'))
        last = {}

        pbar = tqdm(face_imgs, unit='张', disable=not progress)
        for f in pbar:
            name_id = f.stem
            pbar.set_description(f'当前处理 {name_id}.jpg')
            if parse_id:
                name, id = self._parse_id(name_id)
            else:
                id = str(uuid1())
                name = name_id
            ret = self._register(str(f), id, name)
            if ret:
                last[id] = name
        return last

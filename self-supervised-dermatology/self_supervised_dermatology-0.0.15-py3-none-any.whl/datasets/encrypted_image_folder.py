import io
from PIL import Image, ImageFile, UnidentifiedImageError
from pathlib import Path
from cryptography.fernet import Fernet, MultiFernet, InvalidToken
from typing import Union, List
from torchvision.datasets import ImageFolder
ImageFile.LOAD_TRUNCATED_IMAGES = True


class EncryptedImageFolder(ImageFolder):
    def __init__(self,
                 *args,
                 enc_keys: Union[List[str], None],
                 val_transform=None,
                 **kwargs):
        super(EncryptedImageFolder, self).__init__(*args, **kwargs)
        # config for selecting the correct transform
        self.training = True
        self.val_transform = val_transform
        # load all encryption keys
        self.f_keys = []
        self.enc_keys = enc_keys
        if enc_keys is not None:
            # loop over all the keys
            for enc_key_path in enc_keys:
                enc_key_path = Path(enc_key_path)
                if not enc_key_path.exists():
                    raise ValueError("Encryption key does not exist.")
                with open(enc_key_path, "rb") as kf:
                    self.f_keys.append(Fernet(kf.read()))
            # create our multi decryption model
            self.multi_fernet = MultiFernet(self.f_keys)

    def load_encrypted_image(self, path: str):
        with open(path, 'rb') as f:
            try:
                # first try to load the image without encryption,
                # we'll do this first, since it is more often the case
                # and thus more efficient
                return self.loader(path)
            except UnidentifiedImageError:
                # if this exception is thrown, the file is encrypted
                # decrypt encrypted image
                dec_img = self.multi_fernet.decrypt(f.read())
                # check if the decoded byte string is not empty
                if dec_img.rstrip(b'\x00') != b'':
                    # get PIL image from bytes
                    return Image.open(io.BytesIO(dec_img)).convert("RGB")
                else:
                    raise ValueError(
                        f'Image {path} is an encrypted but EMPTY image'
                        ', please remove it.')
            except InvalidToken:
                # if this error is thrown we don't have the correct key
                # to decrypt the image
                raise Warning(
                    f'No valid key available to decrypt the image: {path}')

    def __getitem__(self, index):
        """
        Args:
            index (int): Index

        Returns:
            tuple: (sample, target) where target is class_index of the target class.
        """
        path, target = self.samples[index]

        # check if encryption should be used or not
        if self.enc_keys is not None:
            # use our custom encrypted loader
            sample = self.load_encrypted_image(path)
        else:
            # without a key use the regular loader from pytorch
            sample = self.loader(path)

        if self.transform and self.training:
            sample = self.transform(sample)
        elif self.val_transform and not self.training:
            sample = self.val_transform(sample)

        if self.target_transform is not None:
            target = self.target_transform(target)

        return sample, target

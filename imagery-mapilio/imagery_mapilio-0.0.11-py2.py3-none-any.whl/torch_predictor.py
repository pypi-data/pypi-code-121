import torch
from torchvision import transforms
from PIL import Image


class TorchPredictor:

    @staticmethod
    def predictor_triggers(model_inference, tile_image):
        img_tensor = mask_or_faster_rcnn_predictor(tile_image)
        return model_inference(img_tensor)


def mask_or_faster_rcnn_predictor(tile_image):
    im_pil = Image.fromarray(tile_image)
    input_transforms = [transforms.ToTensor(),
                        ]
    my_transforms = transforms.Compose(input_transforms)
    img_tensor = my_transforms(im_pil).unsqueeze_(0).cuda()
    torch.nonzero(img_tensor, as_tuple=False)
    # torch.cuda.empty_cache()
    return img_tensor

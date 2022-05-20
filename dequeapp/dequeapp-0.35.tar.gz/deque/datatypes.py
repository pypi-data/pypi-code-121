from PIL import Image as PILImage
import PIL
import pickle
import json
import time
import deque.util as util
import numpy as np


class BoundingBox2D():
    def __init__(self, coordinates, domain=None, scores=None, caption=None):
        self.coordinates = coordinates
        if domain is None:
            self.domain = "relative"
        else:
            self.domain = domain
        self.scores = scores
        self.caption = caption


    def _validate(self):
        pass


class Image:

    def __init__(self, data, box_data=None, mode=None):
        self.images = []
        self.box_data = None

        if isinstance(data, list):
            if len(data) == 0:
                raise Exception("Empty list. The list must have one or more images of type numpy, tensor or pil")

            if box_data is not None:
                raise Exception(
                    "Bounding boxes cannot be set with data of array type. In order to use bounding box, "
                    "please pass data of type pil image, tensor or numpy array")

            for d in data:
                if isinstance(data, PILImage.Image):
                    self.images.append(d)
                    # print("I am PIL image")
                elif util.is_type_torch_tensor(util.get_full_typename(data)):
                    torch_module = util.get_module(
                        "torch", "torch is required to render images"
                    )
                    _image = self._tensor_to_pil_image(torch_module=torch_module, pic=d, mode=mode)
                    self.images.append(_image)
                    # print("I used to be tensor image")
                else:
                    if hasattr(d, "numpy"):  # TF data eager tensors
                        d = d.numpy()
                    if d.ndim > 2:
                        d = d.squeeze()  # get rid of trivial dimensions as a convenience
                    _image = PILImage.fromarray(
                        self.to_uint8(d), mode=mode or self.guess_mode(d)
                    )
                    self.images.append(_image)
                    # print("I used to be numpy image")

        else:
            if isinstance(data, PILImage.Image):
                self.images.append(data)
                # print("I am PIL image")
            elif util.is_type_torch_tensor(util.get_full_typename(data)):
                torch_module = util.get_module(
                    "torch", "torch is required to render images"
                )
                self.images.append(self._tensor_to_pil_image(torch_module=torch_module, pic=data, mode=mode))
                # print("I used to be tensor image")
            else:
                if hasattr(data, "numpy"):  # TF data eager tensors
                    data = data.numpy()
                if data.ndim > 2:
                    data = data.squeeze()  # get rid of trivial dimensions as a convenience
                self.images.append(PILImage.fromarray(
                    self.to_uint8(data), mode=mode or self.guess_mode(data)
                ))
                # print("I used to be numpy image")
                if not isinstance(box_data, dict):
                    raise Exception("box_data must be of type dict. The key can be string and value can be a list of boxes with dimensions described as min_x, min_y, max_x, max_y ")
                for key, value in box_data.items():
                    if not isinstance(key, str):
                        raise Exception(
                            "box_data must be of type dict. The key can be string and value can be a list of boxes with dimensions described as min_x, min_y, max_x, max_y ")
                    break

        if not isinstance(box_data, list):
            raise Exception("box_data must be a list of BoundingBox2d objects")
        for b in box_data:
            if not isinstance(b, BoundingBox2D):
                raise Exception("box_data array must have BoundingBox2d objects")

        self.box_data = box_data
        self.type = "Deque.Image"

    def _tensor_to_pil_image(self, torch_module, pic, mode):

        if not (isinstance(pic, torch_module.Tensor) or isinstance(pic, np.ndarray)):
            raise TypeError(f"pic should be Tensor or ndarray. Got {type(pic)}.")

        elif isinstance(pic, torch_module.Tensor):
            if pic.ndimension() not in {2, 3}:
                raise ValueError(f"pic should be 2/3 dimensional. Got {pic.ndimension()} dimensions.")

            elif pic.ndimension() == 2:
                # if 2D image, add channel dimension (CHW)
                pic = pic.unsqueeze(0)

            # check number of channels
            if pic.shape[-3] > 4:
                raise ValueError(f"pic should not have > 4 channels. Got {pic.shape[-3]} channels.")

        elif isinstance(pic, np.ndarray):
            if pic.ndim not in {2, 3}:
                raise ValueError(f"pic should be 2/3 dimensional. Got {pic.ndim} dimensions.")

            elif pic.ndim == 2:
                # if 2D image, add channel dimension (HWC)
                pic = np.expand_dims(pic, 2)

            # check number of channels
            if pic.shape[-1] > 4:
                raise ValueError(f"pic should not have > 4 channels. Got {pic.shape[-1]} channels.")

        npimg = pic
        if isinstance(pic, torch_module.Tensor):
            if pic.is_floating_point() and mode != "F":
                pic = pic.mul(255).byte()
            npimg = np.transpose(pic.cpu().numpy(), (1, 2, 0))

        if not isinstance(npimg, np.ndarray):
            raise TypeError("Input pic must be a torch.Tensor or NumPy ndarray, not {type(npimg)}")

        if npimg.shape[2] == 1:
            expected_mode = None
            npimg = npimg[:, :, 0]
            if npimg.dtype == np.uint8:
                expected_mode = "L"
            elif npimg.dtype == np.int16:
                expected_mode = "I;16"
            elif npimg.dtype == np.int32:
                expected_mode = "I"
            elif npimg.dtype == np.float32:
                expected_mode = "F"
            if mode is not None and mode != expected_mode:
                raise ValueError(
                    f"Incorrect mode ({mode}) supplied for input type {np.dtype}. Should be {expected_mode}")
            mode = expected_mode

        elif npimg.shape[2] == 2:
            permitted_2_channel_modes = ["LA"]
            if mode is not None and mode not in permitted_2_channel_modes:
                raise ValueError(f"Only modes {permitted_2_channel_modes} are supported for 2D inputs")

            if mode is None and npimg.dtype == np.uint8:
                mode = "LA"

        elif npimg.shape[2] == 4:
            permitted_4_channel_modes = ["RGBA", "CMYK", "RGBX"]
            if mode is not None and mode not in permitted_4_channel_modes:
                raise ValueError(f"Only modes {permitted_4_channel_modes} are supported for 4D inputs")

            if mode is None and npimg.dtype == np.uint8:
                mode = "RGBA"
        else:
            permitted_3_channel_modes = ["RGB", "YCbCr", "HSV"]
            if mode is not None and mode not in permitted_3_channel_modes:
                raise ValueError(f"Only modes {permitted_3_channel_modes} are supported for 3D inputs")
            if mode is None and npimg.dtype == np.uint8:
                mode = "RGB"

        if mode is None:
            raise TypeError(f"Input type {npimg.dtype} is not supported")

        return PILImage.fromarray(npimg, mode=mode)

    def guess_mode(self, data: "np.ndarray") -> str:
        """
        Guess what type of image the np.array is representing
        """
        # TODO: do we want to support dimensions being at the beginning of the array?
        if data.ndim == 2:
            return "L"
        elif data.shape[-1] == 3:
            return "RGB"
        elif data.shape[-1] == 4:
            return "RGBA"
        else:
            raise ValueError(
                "Un-supported shape for image conversion %s" % list(data.shape)
            )

    @classmethod
    def to_uint8(cls, data: "np.ndarray") -> "np.ndarray":
        """
        Converts floating point image on the range [0,1] and integer images
        on the range [0,255] to uint8, clipping if necessary.
        """
        np = util.get_module(
            "numpy",
            required="Deque.Image requires numpy if not supplying PIL Images: pip install numpy",
        )

        dmin = np.min(data)
        if dmin < 0:
            data = (data - np.min(data)) / np.ptp(data)
        if np.max(data) <= 1.0:
            data = (data * 255).astype(np.int32)

        # assert issubclass(data.dtype.type, np.integer), 'Illegal image format.'
        return data.clip(0, 255).astype(np.uint8)


class Histogram:
    """
    This object works just like numpy's histogram function
    https://docs.scipy.org/doc/numpy/reference/generated/numpy.histogram.html
    Examples:
        Generate histogram from a sequence
        ```python
        dequeapp.Histogram([1,2,3])
        ```
        Efficiently initialize from np.histogram.
        ```python
        hist = np.histogram(data)
        dequeapp.Histogram(np_histogram=hist)
        ```
    Arguments:
        sequence: (array_like) input data for histogram
        np_histogram: (numpy histogram) alternative input of a precomputed histogram
        num_bins: (int) Number of bins for the histogram.  The default number of bins
            is 64.  The maximum number of bins is 512
    Attributes:
        bins: ([float]) edges of bins
        histogram: ([int]) number of elements falling in each bin
    """

    MAX_LENGTH: int = 512
    _log_type = "histogram"

    def __init__(
        self,
        sequence=None,
        np_histogram=None,
        num_bins=None,
    ):

        if sequence is None and np_histogram is None:
            raise Exception("Either sequence or numpy histogram must be provided but not both")

        if np_histogram:
            if len(np_histogram) == 2:
                self.histogram = (
                    np_histogram[0].tolist()
                    if hasattr(np_histogram[0], "tolist")
                    else np_histogram[0]
                )
                self.bins = (
                    np_histogram[1].tolist()
                    if hasattr(np_histogram[1], "tolist")
                    else np_histogram[1]
                )
            else:
                raise ValueError(
                    "Expected np_histogram to be a tuple of (values, bin_edges) or sequence to be specified"
                )
        else:
            np = util.get_module(
                "numpy", required="Auto creation of histograms requires numpy"
            )

            self.histogram, self.bins = np.histogram(sequence, bins=num_bins)
            self.histogram = self.histogram.tolist()
            self.bins = self.bins.tolist()
        if len(self.histogram) > self.MAX_LENGTH:
            raise ValueError(
                "The maximum length of a histogram is %i" % self.MAX_LENGTH
            )
        if len(self.histogram) + 1 != len(self.bins):
            raise ValueError("len(bins) must be len(histogram) + 1")



if __name__ == "__main__":
    bins = [0,1, 2, 3]
    h = np.histogram([1,2,1], bins=bins)
    import matplotlib.pyplot as plt

    #plt.hist(h)
    #plt.hist(h, bins=bins)
    #plt.show()
    dh = Histogram(np_histogram=h)
    print(dh.histogram, dh.bins)

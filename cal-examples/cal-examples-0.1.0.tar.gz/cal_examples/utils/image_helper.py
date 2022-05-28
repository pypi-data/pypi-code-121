import numpy as np
from PIL import Image
from matplotlib.cm import get_cmap


def generate_heatmap_image(
    pil_img: Image.Image,
    np_heatmap_0to1: np.ndarray,
    grayscale: bool = True,
    alpha: float = 0.4
) -> np.ndarray:
    # Use jet colormap to colorize heatmap
    jet = get_cmap("jet")
    jet_colors = jet(np.arange(256))[:, :3]

    # Create an image with RGB colorized heatmap
    np_heatmap_img = np.uint8(255 * np_heatmap_0to1)
    np_colormap_0to1 = jet_colors[np_heatmap_img]
    np_colormap_img = np.uint8(255 * np_colormap_0to1)
    pil_colormap_img = Image.fromarray(np_colormap_img)

    # Resize the colorized heatmap to the input image size
    w, h = pil_img.size
    pil_colormap_img = pil_colormap_img.resize((w, h))
    np_colormap_img = np.array(pil_colormap_img)

    # Convert the input image to grayscale
    if grayscale:
        pil_img = pil_img.convert('L')
        np_img = np.array(pil_img).reshape((h, w, 1))
    else:
        np_img = np.array(pil_img)

    # Superimpose the heatmap on the input image
    np_cam_img = np.uint8((1.0 - alpha) * np_img + alpha * np_colormap_img)
    pil_cam_img = Image.fromarray(np_cam_img)
    return pil_cam_img

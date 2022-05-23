"""Image Validation module."""


def allowed_base64_image(image: str) -> bool:
    """Check if base64 image has an allowed format.
    :param image:
    :return:
    """
    if not image.startswith('data:image/'):
        return False
    return image[11:14] in {'png', 'jpg', 'jpeg', 'gif'}

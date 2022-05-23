import base64


def convert_image(filename: str) -> str:
    """Converts image to string.

    Args:
        filename: The name of the image to convert.

    Returns:
        The image converted to serializable string representation.
    """
    with open(filename, "rb") as file:
        converted = base64.b64encode(file.read()).decode()
    return converted


def extract_csv_row(filename: str, row: int) -> str:
    """Extracts a selected line from the csv file.

    Args:
        filename:
            A path to the file.
        row:
            The row number to extract.

    Returns:
        The row from the csv file as a string.
    """
    with open(filename, "r") as file:
        extracted = file.readlines()[row - 1 : row][0].strip("\n")
    return extracted


def join_url(*components: str) -> str:
    """Concatenates multiple url components into one url.

    Args:
        *components:
            Multiple url components.

    Returns:
        A complete url.
    """
    clean = [str(comp).strip("/") for comp in components]
    return "/".join(clean)

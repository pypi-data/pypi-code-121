from pathlib import Path

from black import color_diff, diff


def text_diff(input_path: Path, output_code: str) -> str:
    """
    Report the differences that globality black will make to input_path file
    in a git-like format leveraging code already in black.
    """

    diff_contents = diff(input_path.read_text(), output_code, "", input_path.name)
    diff_contents = color_diff(diff_contents)
    return diff_contents

from os import path

from nwon_baseline.file_helper.file import file_extension_from_path


def path_to_write_pydantic_model(file_path: str) -> str:
    suffix = file_extension_from_path(file_path)

    if suffix != ".json":
        splitted_file_name = path.basename(file_path).split(".")
        directory = path.dirname(file_path)

        if len(splitted_file_name) > 2:
            raise Exception(
                f"The file type of {path.basename(file_path)} needs to be json or it can't contain a dot."
            )
        elif len(splitted_file_name) == 2:
            file_path = path.join(directory, f"{splitted_file_name[0]}.json")

    return file_path

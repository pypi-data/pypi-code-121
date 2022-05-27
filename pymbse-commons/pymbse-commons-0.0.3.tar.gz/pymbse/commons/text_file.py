def read(file_path: str) -> str:
    with open(file_path, "r") as file:
        return file.read()


def readlines(file_path: str) -> list:
    with open(file_path, "r") as file:
        return file.readlines()


def write(file_path: str, content: str) -> None:
    with open(file_path, "w") as file:
        file.write(content)


def writelines(file_path: str, contents: list, endline="\n") -> None:
    with open(file_path, "w") as file:
        for content in contents:
            file.write(content + endline)

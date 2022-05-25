import os


def main() -> None:
    file_path = os.getcwd()
    if os.path.exists(file_path + "/requirements.txt"):
        file_path = file_path + "/requirements.txt"
    else:
        raise FileNotFoundError("File requirements.txt not found.")

    requirements = []

    with open(file_path, "r", encoding="utf8") as f:
        requirements = [req.rstrip("\n") for req in f.readlines()]

    with open(file_path, "w", encoding="utf8") as f:
        f.write("\n".join(sorted(requirements)))

    print("Your requirements.txt file is formatted.")


if __name__ == "__main__":
    main()

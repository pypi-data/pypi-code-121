import base64
import ntpath
import zipfile


def encode_to_base64(file):
    with open(file, "rb") as f:
        encoded = base64.b64encode(f.read())
    return encoded


def base64_to_string(base):
    return base.decode('utf-8')


def get_path_tail(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def get_path_dir(path):
    head, tail = ntpath.split(path)
    return head or ntpath.dirname(path)


def zip_file(source_report_file, output_zip):
    file_name = get_path_tail(source_report_file)
    print(f"Start zipping {source_report_file} into {output_zip}")
    try:
        with zipfile.ZipFile(output_zip, mode="w") as archive:
            archive.write(source_report_file, arcname=file_name)
            archive.close()
        print("Zipped successfully!")
    except zipfile.BadZipFile as error:
        print(error)

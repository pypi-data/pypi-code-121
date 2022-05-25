import os
import sys


def read_file(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
        return data


def modify_files(files_list, change_source, change_dest, url_name):
    """! Replaces a string in a list of files.

        Args:
            files_list: List of files to run search on.
            change_source: Source text to search.
            change_dest: Text to be inserted.
            url_name: Url to be used in inserted text.

    """
    for file in files_list:
        data = read_file(file[0])
        new_url = url_name if file[1] == '.' else url_name + file[1] + '/'
        change_dest1 = change_dest.replace('url_tag', new_url)
        data = data.replace(change_source, change_dest1)

        if os.path.exists(file[0]):
            os.remove(file[0])

        save_file(file[0], data)


def find_files(path, ext):
    """! Find files in path with specified extension.

    Args:
        path: File path
        ext: Required file extension

    Returns:
        List with files abs paths and sub folder name.
    """

    files_path = []

    for root, dirs, files in os.walk(path):
        file_list = [[os.path.join(root, file), os.path.relpath(root, path)] for file in files if file.endswith(ext)]
        files_path.extend(file_list)

    return files_path


def save_file(file_name_path, data):
    f = open(file_name_path, "w")
    f.write(data)
    f.close()


if __name__ == '__main__':
    current_doc_folder = sys.argv[1]
    base_tag_path = sys.argv[2]

    print("Finding files...")
    html_list = find_files(current_doc_folder, 'html')
    css_list = find_files(current_doc_folder, 'css')

    print(f'Found {len(html_list)} html files.')
    print(f'Found {len(css_list)} css files.')

    print("Modifying files...")
    modify_files(html_list, '<head>', '<head><base href=\"url_tag\">', base_tag_path)
    modify_files(css_list, "url(\'", "url(\'url_tag", base_tag_path)
    modify_files(css_list, "url(\"", "url(\"url_tag", base_tag_path)

    print("Adding <base> tag done!")

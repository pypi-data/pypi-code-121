def read_conll(file_path: str, file_type='conll'):
    """
    Read conll format data_file
    Args:
        file_path: path of label file
        text_index: index of text texts, default 0
        label_index: index of label texts, default 1

    Returns:

    """

    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            rows = line.strip().split(' ')
            if len(rows) == 1:

                yield data
                data = []

            else:
                data.append(rows)

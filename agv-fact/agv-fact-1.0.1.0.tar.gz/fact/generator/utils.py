


def replace_char(text, de, a):
    a = a
    for i in de.encode().decode('utf-8'):
        for j in a.encode().decode('utf-8'):
            text = text.replace(i, j)
            if a.find(j) != -1:
                a = a[a.find(j) + 1:]
            break
    return text


def replace(text):
    return replace_char(text, 'áéíóúÁÉÍÓÚàèìòùÀÈÌÒÙñÑ', 'aeiouAEIOUaeiouAEIOUnN')
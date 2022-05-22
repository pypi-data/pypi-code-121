# функция для извлечения из строки электрой почты

def email_finder (string):
    list_of_words = string.split (" ")
    for word in list_of_words:
        if word.find ("@") > 0:
            return word

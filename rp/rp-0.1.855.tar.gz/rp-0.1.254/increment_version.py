def string_to_text_file(file_path,string,) :
    file=open(file_path,"w")
    try:
        file.write(string)
    except:
        file=open(file_path,"w",encoding='utf-8')
        file.write(string,)

    file.close()
def text_file_to_string(file_path) :
    return open(file_path).read()
print("Incrementing version number...")
string_to_text_file('version.py',str(int(text_file_to_string('version.py'))+1))
print('...done.')

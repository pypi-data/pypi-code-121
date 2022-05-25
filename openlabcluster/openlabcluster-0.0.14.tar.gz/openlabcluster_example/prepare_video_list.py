import os

with open('./PreprocessedNameList_12set_selected.text', 'r') as f_in:
    curre_path = os.getcwd()
    root_path = curre_path.split('/')[:-1]
    root_path2 = '/'.join(root_path)
    with open('./video_name.text', 'w') as f_out:
        lines =f_in.readlines()
        for line in lines:
            f_out.writelines(os.path.join(root_path2,line[1:]))



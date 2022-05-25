import os
import json

def processing_input_from_front_end():
    try:
        script_dir=os.path.dirname('.')
        file_path_read=os.path.join(script_dir+'data/input.json')
        with open(file_path_read,'r') as openfile:
            input_request=json.load(openfile)
            openfile.close()
        print(input_request)
    except:
        return{
            'status':'Error',
            'code': 500,
            'message': 'Bad Error Request'
        }
    return input_request

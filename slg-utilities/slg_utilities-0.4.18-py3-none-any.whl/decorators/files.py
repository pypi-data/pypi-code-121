import os

def get_filename(filetype):
  '''
  forces user to input filename if one not detected with filetype == <filetype>

  <filetype> example: '.json'
  '''

  def outer(func):

    def inner(*args, **kwargs):
      print(kwargs)
      print(args)

      filename = kwargs.get('filename')
      if not filename:
        while True:
          filename = input(f'Please enter a valid filename (filetype== {filetype}: ')
          if get_file_parts(filename)[1] == filetype:
            kwargs['filename'] = filename
      
      return func(*args, **kwargs)
    
    return inner
  
  return outer


      



















#region HELPERS FOR DECORATORS

def get_file_parts(file_):
  '''
  file needs appropriate path headed

  returns filename, file_extension
  '''
  print(os.path.splitext(file_))
  return os.path.splitext(file_)



#endregion HELPERS FOR DECORATORS
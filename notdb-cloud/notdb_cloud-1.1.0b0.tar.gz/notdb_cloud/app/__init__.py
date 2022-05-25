from flask import Flask, render_template, abort, Response, request, jsonify, url_for
import notdb
import pyonr
from termcolor import colored
import os

def refresh_data(file:pyonr.Read) -> dict:
   return file.readfile

def get_class(obj):
   return type(obj)

def get_obj_class_name(obj):
   return type(obj)().__class__.__name__

def is_secured(file:pyonr.Read):
   '''
   check if a NotDB database is secured with a password or not
   '''
   if file.readfile.get('__password'):
      return True
   return False

def find_ndb_files(path):
   p = path
   if path == '.':
      p = os.getcwd()
   files = [f for f in os.listdir(p) if f.endswith('.ndb')]

   return files

def create_app():
   
   app = Flask(__name__)

   @app.route('/favicon.ico')
   def favicon():
      return ''

   @app.route('/', methods=['GET'])
   def index():
      dbs = find_ndb_files('.')
      host = f'{request.base_url}'
      return render_template('index.html', host=host, dbs=dbs)

   @app.route('/<db_name>', methods=['GET', 'POST', 'CONNECT', 'BRING', 'UPDATE'])
   def documents_route(db_name):
      try:
         file = pyonr.Read(db_name)
         db = None

         if request.method == 'CONNECT':
            return 'Success'
         if request.method == 'POST':
            try:
               password = request.form.get('password', '')
               db = notdb.NotDBClient(db_name, password=password) 
               if app.take_password_once:
                  app.config[f'{db_name}_p'] = password
            except notdb.WrongPasswordError:
               return render_template('get_password.html', error='Password is wrong.', db=db_name)
               
         elif request.method == 'BRING':
            data = refresh_data(file)
            return f'{data}'
         
         elif request.method == 'UPDATE':
            update = request.form.get('update', None)
            if not update:
               err = 'Error: Invalid update'
               print(colored(f'\n{err}\n', 'red'))
            
               return f'{err}'
               
            file.write(update)
            return 'Success'

         else:
            if app.config.get(f'{db_name}_p', None):
               db = notdb.NotDBClient(db_name, app.config[f'{db_name}_p'])
            else:
               db = notdb.NotDBClient(db_name)

         data = refresh_data(file)

         db_info = {}

         db_info['Secured with password'] = True if data.get('__password') else False
         db_info['documents'] = db.documents

         dr_redirect = url_for('documents_route', db_name=db_name)
         fr_redirect = url_for('files_route', db_name=db_name)
         dbname = f'{db_name}'
         return render_template('viewer.html',
                        documents=db.get({}),
                        db_info=db_info,
                        host=f'{request.base_url}',
                        db_name=dbname,
                        dr_redirect=dr_redirect,
                        fr_redirect=fr_redirect,
                        get_obj_class_name=get_obj_class_name,
                        get_class=get_class,
                        f=file)

      except pyonr.FileExistsError:
         err = {}
         err['success'] = False
         err['err'] = 'INVALID_NAME'
         print('pyonr')
         return jsonify(err)
      except notdb.WrongPasswordError:
         print('notdb')
         return render_template('get_password.html', db=db_name)
      except Exception as err:
         print(err)
         err = {}
         err['success'] = False
         err['err'] = str(err)
         return jsonify(err)

   @app.route('/<db_name>/files', methods=['GET', 'POST'])
   def files_route(db_name):
      db = pyonr.Read(db_name)
      webAppURL = str(request.url_root)
      host = request.base_url.replace('/files', '')
      dr_redirect = url_for('documents_route', db_name=db_name)
      fr_redirect = url_for('files_route', db_name=db_name)

      if request.method == 'POST':
         try:
            password = request.form.get('password', '')
            db = notdb.NotDBClient(db_name, password=password) 
            if app.take_password_once:
               app.config[f'{db_name}_p'] = password
         except notdb.WrongPasswordError:
            return render_template('get_password.html', error='Password is wrong.', db=db_name)
      else:
         if app.config.get(f'{db_name}_p', None):
            db = notdb.NotDBClient(db_name, app.config[f'{db_name}_p'])
         else:
            db = notdb.NotDBClient(db_name)

      return render_template('files.html',
                        files=db.files.getFiles({}),
                        host=f'{request.base_url}',
                        webAppURL=webAppURL,
                        dr_redirect=dr_redirect,
                        fr_redirect=fr_redirect,
                        db_name=db_name,
                        get_obj_class_name=get_obj_class_name,
                        get_class=get_class)

   @app.route('/<db_name>/cdn/<name>')
   def cdn_loader(db_name, name):
      try:
         file = pyonr.Read(db_name)
         db = notdb.NotDBClient(file.filepath)
         webAppURL = str(request.url_root)

         file = db.files.getFile({'name': name})
         err = {}

         if not file:
            err['success'] = False
            err['err'] = 'INVALID_NAME'
            err['msg'] = f'{name} is not in the database'
            return jsonify(err)

         return Response(file['data'], mimetype=file['mimetype'])
      except Exception as e:
         err['err'] = str(e)
         return jsonify(err)

   @app.route('/<db_name>/cdn')
   def cdn_route():
      err = {}
      err['success'] = False
      err['err'] = 'INVALID_NAME'
      err['msg'] = 'add a name after (/cdn/<name>)'

      return jsonify(err)

   return app
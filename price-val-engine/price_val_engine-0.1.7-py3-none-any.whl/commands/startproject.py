import os, stat
import string
from importlib import import_module
from shutil import ignore_patterns, copy2, copystat, move
from argparse import ArgumentError

from price_val_engine.commands import BaseCommand


class Command(BaseCommand):
    
    def add_arguments(self, parser):
        parser.add_argument('name', help='Name of the application or project.')
        parser.add_argument('directory', nargs='?', help='Optional destination directory')
    
    def validate_projectname(self, projectname):
        if projectname is None:
            raise ArgumentError('you must provide project "name"'.format(name=projectname))
        # Check it's a valid project directory name.
        if not projectname.isidentifier():
            raise ArgumentError("'{name}' is not a valid project name." 
                                "Please make sure the name begin with letter " 
                                "and may contains number[0-9] and underscore only".format(name=projectname))
        # Check it cannot be imported.
        try:
            import_module(projectname)
        except ImportError:
            pass
        else:
            raise ArgumentError(
                "'{name}' conflicts with the name of an existing Python module. Please use different name".format(projectname)
            )
    
    @property
    def templates_dir(self):
        import price_val_engine
        return os.path.join(
            os.path.join(price_val_engine.__path__[0], 'conf'),
            'project_template'
        )
    
    def render_templatefile(self, path, **kwargs):
        with open(path, 'rb') as fp:
            raw = fp.read().decode('utf8')
        content = string.Template(raw).substitute(**kwargs)
        render_path = path[:-len('.tmpl')] if path.endswith('.tmpl') else path
        
        if path.endswith('.tmpl'):
            os.rename(path, render_path)
        
        with open(render_path, 'wb') as fp:
            fp.write(content.encode('utf8'))
            
        
    def set_write_permission(self, path):
        os.chmod(path, os.stat(path).st_mode | stat.S_IWUSR)
    
    def copy_templates(self, template_dir, project_dir, project_name):
        file_names = os.listdir(template_dir)
        ignore_files_func = ignore_patterns('*.pyc', '__pycache__', '.svn')
        ignore_files = ignore_files_func(template_dir, file_names)
        
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

        for file_name in file_names:
            if file_name not in ignore_files:            
                src = os.path.join(template_dir, file_name)
                #print("src =>", src)
                dst = os.path.join(project_dir, file_name)
                # print("dst =>", dst)
                if os.path.isdir(src):
                    self.copy_templates(src, dst, project_name=project_name)
                else:
                    copy2(src, dst)
                    self.set_write_permission(dst)
                    # rename files
                    self.render_templatefile(dst, project_name=project_name)
                    #if dst.endswith('.tmpl'):
                    #    new_file_path =  dst[:-len('.tmpl')]
                    #    os.rename(dst, new_file_path)
                    
        # copy PERNISSIONS
        copystat(template_dir, project_dir)
        self.set_write_permission(project_dir)
        
    def handle(self, *args, **options):
        project_name = options.pop('name')
        target = options.pop('directory')
        self.validate_projectname(project_name)
        if target is None:
            project_dir = os.path.join(os.getcwd(), str(project_name).replace("_", "-"))        
        else:
            project_dir = os.path.abspath(os.path.expanduser(target))
            if not os.path.exists(project_dir):
                raise ArgumentError("Destination directory '%s' does not exist." % project_dir)
        self.copy_templates(self.templates_dir, project_dir, project_name=project_name)
        # rename project_name foler with actual project_name
        move(os.path.join(project_dir, 'project_name'), os.path.join(project_dir, project_name))
        print("New [price_val_engine] Project created.")
    
    
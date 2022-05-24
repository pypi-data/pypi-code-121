from logging import root
import re
import uuid
from markdown import Markdown
from mkdocs import utils as mkdocs_utils
from mkdocs.config import config_options, Config
from mkdocs.plugins import BasePlugin
from jinja2 import Environment, FileSystemLoader
import os
from pathlib import Path

DIR_PATH = Path(os.path.dirname(os.path.realpath(__file__)))
class BrAsHelpIndexGenerator(BasePlugin):
    config_scheme = (
        ('ComponentName', config_options.Type(str, default='')),
        ('HelpID', config_options.Type(str, default='')),
        ('Version', config_options.Type(str, default='0.0.0.0')),
        ('ParentGuid', config_options.Type(str, default='982bdaef-8fd0-40bd-a348-c999b1816a79')),
        ('TargetPath', config_options.Type(str, default='technologysolutions\\')),
        ('OutputPath', config_options.Type(str, default=''))
    )
    helpPageToc = ''
    helpUpgradeXml = ''

    def on_config(self, config):
        if self.config['OutputPath']:
            config['site_dir'] = self.config['OutputPath'] + '\\Help\\Help-EN\\' + self.config['ComponentName'] + '\\' + self.config['ComponentName']
        if self.config['ComponentName']:
            self.config['ComponentNameLowerCase'] = self.config['ComponentName'].lower()
        #AS Help links will not work if we use directory URLs, so have to change the option if the user has not enabled this setting
        if config['use_directory_urls']:
            config['use_directory_urls'] = False
    def on_nav(self, nav, config, files):
        #Build GUIDs for the navigation pages
        for itm in nav:
            self.buildGuids(itm)
        self.renderPage(nav,config)
        return nav
    
    def renderPage(self,_nav,config):

        search_path = os.path.join(DIR_PATH, "Templates")
        file_loader = FileSystemLoader(search_path)
            
        env = Environment(loader = file_loader,trim_blocks=True,lstrip_blocks=True)
        template = env.get_template("helpContentsTemplate.xml")
        self.helpPageToc = template.render(nav = _nav,config = self.config)
        template = env.get_template("HelpUpgradeTemplate.xml")
        self.helpUpgradeXml = template.render(nav = _nav,config = self.config)
                
    def buildGuids(self,itm):
        if itm.children is not None:
            for child in itm.children:
                self.buildGuids(child)
        else:
            itm.Guid = uuid.uuid5(uuid.NAMESPACE_URL,itm.url)

    def on_post_build(self,config):
        with open('./{0}{1}.xml'.format(self.config['OutputPath'] + '\\Help\\','HelpUpgrade'),"w") as f:
            f.write(self.helpUpgradeXml)
        tmp = '{0}_{1}'.format(self.config['ComponentName'].lower(),self.config['Version'])
        with open('./{0}{1}.xml'.format(self.config['OutputPath'] + '\\Help\\Help-en\\' + self.config['ComponentName'] + '\\',tmp),"w") as f:
            f.write(self.helpPageToc)
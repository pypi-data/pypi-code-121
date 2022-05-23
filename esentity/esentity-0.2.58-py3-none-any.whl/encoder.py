#coding: utf-8
from flask.json import JSONEncoder                                                                                                    
from datetime import date
from html.parser import HTMLParser


class IsoJSONEncoder(JSONEncoder):                                                                                                    
    def default(self, obj):                                                                                                           
        try:                                                                                                                          
            if isinstance(obj, date):                                                                                                 
                return obj.isoformat().replace('+00:00', 'Z')
            iterable = iter(obj)                                                                                                      
        except TypeError:                                                                                                             
            pass                                                                                                                      
        else:                                                                                                                         
            return list(iterable)                                                                                                     
        return JSONEncoder.default(self, obj)  


class TelegramContentParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.content = []
        self.line = ''
        self.process = False

    def handle_starttag(self, tag, attrs):
        if self.process:
            _s = ' '.join([f'{k}="{v}"' for k, v in attrs])
            _a = f' {_s}' if _s else ''
            self.line += f'<{tag}{_a}>'
        if (tag == 'p'):
            self.line = ''
            self.process = True

    def handle_endtag(self, tag):
        if (tag == 'p'):
            self.process = False
            self.content.append(self.line)
        if self.process:
            self.line += f'</{tag}>'

    def handle_data(self, data):
        if self.process:
            self.line += data        
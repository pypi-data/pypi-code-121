'''
BLURB GOES HERE.

Copyright (c) 2015 - 2022 Rob "N3X15" Nelson <nexisentertainment@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''
import codecs

from buildtools.utils import img2blob

#from ruamel.yaml import YAML
#yaml = YAML(typ='safe', pure=True)

#@YAML.register_class
class SerializableLambda:
    yaml_tag = '!lambda'

    def __init__(self, text):
        self.string=text

    def __call__(self, arg):
        return self.string

#@YAML.register_class
class SerializableFileLambda:
    yaml_tag = '!filelambda'

    def __init__(self, filename: str, outformat: str='{FILEDATA}', encoding: str='utf-8-sig', as_blob: bool=False):
        self.filename = filename
        self.outformat = outformat
        self.encoding = encoding
        self.as_blob = as_blob

    def __call__(self, arg):
        if self.as_blob:
            return self.outformat.format(FILEDATA=img2blob(self.filename).strip())

        with codecs.open(self.filename, 'r', encoding=self.encoding) as f:
            return self.outformat.format(FILEDATA=f.read())

def callLambda(var):
    if isinstance(var, SerializableLambda):
        var = var()
    elif isinstance(var, SerializableFileLambda):
        var = var()
    return var

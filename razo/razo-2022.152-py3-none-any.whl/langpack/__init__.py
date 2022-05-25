pack=['''
Copyright (c) 2022 The Razo Community

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
''','Razo first use setting.','Do you agree the license above?[y/n][y in default]','Because you do not agree the license,it is shutting down.',
'Please set root password(remember to let others cannot know):','What is your username(in English)?',
'Type help for help.','Still testing,please know.',
'''
help:Show help.
su:Ask for superuser license.
shutdown:Shutdown razo.
info:Show info.
setting:Run setting.
time:Get time.
sudo(add before commands):Let the command after sudo get temp root.
[ANYTHING ELSE]:Run it in the prompt of the host system.
''', 'Please enter root password:' ,'su:Sorry',  'Do you REALLY want to shutdown?[y/n]',
'Shutting down.',{6:'Sun.',0:'Mon.',1:'Tue.',2:'Wed.',3:'Thu.',4:'Fri',5:'Sat.'},
'%Y-%m-%d %H:%M:%S','Not able until root.','SYS1001:There is not command {}.',
'Hello,{}.','Sorry.','You need to restart to get the settings ready.','Done,return {}.']

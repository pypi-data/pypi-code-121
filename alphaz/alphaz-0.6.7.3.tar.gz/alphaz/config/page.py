import os

def get_sub_html(key, value):
    if type(value) == dict:
        content = '<li><span class="caret">%s</span><ul class="nested">'%key

        for sub_key, sub_value in value.items():
            content += get_sub_html(sub_key, sub_value)

        content += "</ul></li>"
    else:
        content = '<li>%s: <sub style="color:blue">%s<sub></li>'%(key,value)
    return content

def get_html_content(config):
    root = os.path.dirname(__file__)

    data = config.data

    content = '<ul id="myUL">'

    for key, value in data.items():
        content += get_sub_html(key,value)

    content += '</ul>'

    with open(root + os.sep + 'source.html','r') as f:
        html_content = f.read()

    with open(root + os.sep + 'config.html','w') as f:
        f.write(html_content.replace('{{content}}',content))
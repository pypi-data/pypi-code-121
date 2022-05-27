from common_util import *
from crawler_util import *
from document_util import *


from crawler_util import *


basic_config(logs_style="print")
for times in ["2019", "2020", "2021"]:
    html = random_proxy_header_access("https://openaccess.thecvf.com/CVPR{}".format(times), random_proxy=False)
    attr_list = get_attribute_of_html(html, {'href': IN, 'CVPR': IN, "py": IN, "day": IN})
    for ele in attr_list:
        path = ele.split("<a href=\"")[1].split("\">")[0]
        path = "https://openaccess.thecvf.com/" + path
        html = random_proxy_header_access(path, random_proxy=False)
        attr_list = get_attribute_of_html(html,
                                          {'href': "in", 'CVPR': "in", "content": "in", "papers": "in"})
        for eles in attr_list:
            pdf_path = eles.split("<a href=\"")[1].split("\">")[0]
            work_path = local_path_generate("cvpr{}".format(times))
            retrieve_file("https://openaccess.thecvf.com/" + pdf_path, work_path)

from django.shortcuts import render
from appointment.templatetags.appointment_tags import make_post_context
from _data import context

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)


def buildup(request, lang=None):
    # django-base-ds에 아래 코드가 이미 포함되어 있음. 링크만 추가하면됨
    # <link rel="preconnect" href="https://fonts.googleapis.com">
    # <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    font_link_for_kor = "https://fonts.googleapis.com/css2?" \
                        "family=Dongle:wght@300;400;700&" \
                        "family=Hahmlet:wght@100;200;300;400;500;600;700;800;900&" \
                        "family=Noto+Sans+KR:wght@100;300;400;500;700;900&" \
                        "family=Noto+Serif+KR:wght@200;300;400;500;600;700;900&display=swap"
    font_link_for_eng = "https://fonts.googleapis.com/css2?"\
                         "family=Open+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,300;1,400;1,500;1,600;1,700;1,800&"\
                         "family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&"\
                         "family=Raleway:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap"
    if lang == 'kor':
        c = context.context_kor
        c['lang']['selected'] = 'kor'
        c['font_link'] = font_link_for_kor
    elif lang == 'eng':
        c = context.context_eng
        c['lang']['selected'] = 'eng'
        c['font_link'] = font_link_for_eng
    else:
        # 페이지 로딩시 초기 언어
        c = context.context_eng
        c['lang']['selected'] = 'eng'
        c['font_link'] = font_link_for_eng
    logger.debug(c)
    if request.method == 'GET':
        return render(request, f"mentor_ds/base.html", c)
    elif request.method == "POST":
        # appointment가 contact에 포함된 경우는 anchor를 contact으로 설정한다.
        c.update(make_post_context(request.POST, c['basic_info']['consult_email'], anchor='contact'))
        return render(request, f"mentor_ds/base.html", c)

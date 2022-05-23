from django.template import Library, loader

from util_demian import utils
from ..forms import AppointmentForm

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.ERROR)


register = Library()

# 인클루전 태그는 동적으로 html파일을 할당할 수 없어서..
# https://localcoder.org/django-inclusion-tag-with-configurable-template

# 일반적인 방식의 심플태그는 csrf_token을 처리할 수 없어서...
# https://stackoverflow.com/questions/43787700/django-1-11-typeerror-context-must-be-a-dict-rather-than-context


@register.simple_tag(takes_context=True)
def make_appointment(context):
    t = loader.get_template(f"appointment/{context['theme']}.html")
    context.update({
        'form': AppointmentForm(),
        'post_message': context.get('post_message', None),
        'naver_link': context.get('naver', None),
    })
    logger.info(context)
    return t.render(context.flatten())


def make_post_context(request_post, consult_mail, anchor='appointment'):
    logger.info(request_post)
    context = {}
    # appointment 앱에서 post 요청을 처리함.
    logger.info(f'request.POST : {request_post}')
    form = AppointmentForm(request_post)
    # 템플릿 렌더링 후 바로 appointment 앵커로 이동시키기 위해 설정
    context['anchor'] = anchor
    if form.is_valid():
        name = form.cleaned_data['name']
        phone = form.cleaned_data['phone']
        date = form.cleaned_data['date']
        message = form.cleaned_data['message']
        logger.info(f'Pass validation test -  {name} {phone} {date} {message}')
        is_sendmail = utils.mail_to(title=f'{name} 고객 상담 문의',
                                    text=f'이름: {name}\n연락처: {phone}\n예약일: {date}\n메시지: {message}',
                                    mail_addr=consult_mail)
        if is_sendmail:
            context['post_message'] = '담당자에게 예약신청이 전달되었습니다. 확인 후 바로 연락드리겠습니다. 감사합니다.'
        else:
            context['post_message'] = '메일 전송에서 오류가 발생하였습니다. 카카오톡이나 전화로 문의주시면 감사하겠습니다. 죄송합니다.'
        return context
    else:
        logger.error('Fail form validation test')
        context['post_message'] = '입력 항목이 유효하지 않습니다. 다시 입력해 주십시요.'
        return context
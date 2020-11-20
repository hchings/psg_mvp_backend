"""
Celery tasks for sending out email.
TODO: WIP

"""

import coloredlogs, logging
from celery import shared_task

from django.template.loader import render_to_string
# from django.utils.html import strip_tags
from django.core.mail import send_mail


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


#  TODO: WIP
@shared_task
def send_case_in_review_confirmed(case_instance):
    msg_html = render_to_string('beefree.html', {'WTF': 'hello world!'})

    tags = case_instance.surgeries or []
    first_tag = '' if not tags else tags[0]
    case_title = case_instance.title or "無標題"
    username = case_instance.author.name

    subject = "🚀 %s, Surgi正在檢閱你的%s整型案例" % (username.capitalize(), first_tag)

    try:
        send_mail(subject, "text body", "founders@surgi.fyi",
                ["hchings@gmail.com"], html_message=msg_html)
    except Exception as e:
        logger.error("[Error] send_case_in_review_confirmed: %s" % str(e))

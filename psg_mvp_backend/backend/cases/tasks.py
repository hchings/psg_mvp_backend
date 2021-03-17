"""
Celery tasks for sending out email.
TODO: WIP

"""

import coloredlogs, logging
from celery import shared_task
import html2text

from django.template.loader import render_to_string
# from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives # the underlying class of send_mail
from django.contrib.auth import get_user_model

from backend.settings import EMAIL_WITH_DISPLAY_NAME, BCC_EMAIL

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

User = get_user_model()


#  TODO: WIP
@shared_task
def send_case_in_review_confirmed(user_uuid, first_tag, title, case_id):
    # get user obj
    try:
        user_obj = User.objects.get(uuid=user_uuid)
        email = user_obj.email
        # print("user email", email)
    except Exception as e:
        logger.error("[Error]send_case_in_review_confirmed 1: %s" % str(e))
        return

    title = title or ""
    username = user_obj.username
    # TODO: need to recheck w/ social auth
    signature = ''
    try:
        signature = user_obj.email.split('@')[0] + user_uuid
    except Exception as e:
        logger.error('[Error] send_case_in_review_confirmed :%s' % str(e))
        pass

    msg_html = render_to_string('cases/case_in_review.html', {'first_tag': first_tag,
                                                              'username': username.capitalize(),
                                                              'case_title': title,
                                                              'case_id': case_id,
                                                              'signature': signature})
    msg_text = html2text.html2text(msg_html)

    subject = "🚀 Surgi正在檢閱你的%s整型案例" % first_tag

    try:
        # send_mail(subject, msg_text, EMAIL_WITH_DISPLAY_NAME,
        #           [email], html_message=msg_html)

        # send_mail does not support BCC,
        # need to use this class instead.
        email = EmailMultiAlternatives(
            subject,
            msg_text,
            EMAIL_WITH_DISPLAY_NAME,
            [email],
            [BCC_EMAIL],
            reply_to=[BCC_EMAIL]
        )
        email.attach_alternative(msg_html, "text/html")
        email.send(fail_silently=False)
    except Exception as e:
        logger.error("[Error] send_case_in_review_confirmed 2: %s" % str(e))


@shared_task
def send_case_published_notice(user_uuid, first_tag, title, case_id):
    try:
        user_obj = User.objects.get(uuid=user_uuid)
        email = user_obj.email
        # print("user email", email)
    except Exception as e:
        logger.error("[Error]send_case_published_notice 1: %s" % str(e))
        return

    title = title or ""
    username = user_obj.username
    # TODO: need to recheck w/ social auth
    signature = ''
    try:
        signature = user_obj.email.split('@')[0] + user_uuid
    except Exception as e:
        logger.error('[Error] send_case_published_notice :%s' % str(e))
        pass

    msg_html = render_to_string('cases/case_published.html', {'first_tag': first_tag,
                                                              'username': username.capitalize(),
                                                              'case_title': title,
                                                              'case_id': case_id,
                                                              'signature': signature})
    msg_text = html2text.html2text(msg_html)

    subject = "🥳 你的%s整型案例已成功刊登在Surgi" % first_tag

    try:
        send_mail(subject, msg_text, EMAIL_WITH_DISPLAY_NAME,
                  [email], html_message=msg_html)
    except Exception as e:
        logger.error("[Error] send_case_published_notice 2: %s" % str(e))


# TODO: WIP
@shared_task
def send_case_invite(username, invitee_email, invite_url):
    logger.info("send_case_invite: %s, %s, %s" % (username, invitee_email, invite_url) )
    subject = "%s 邀請你分享整型經驗" % username
    msg_html = render_to_string('cases/case_invite.html', {'username': username,
                                                           'invite_url': invite_url})

    msg_text = html2text.html2text(msg_html)

    try:
        send_mail(subject, msg_text, EMAIL_WITH_DISPLAY_NAME,
                  [invitee_email], html_message=msg_html)
    except Exception as e:
        logger.error("[Error] send_case_invite: %s" % str(e))

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
from backend.settings import EMAIL_WITH_DISPLAY_NAME


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


@shared_task
def send_otp_code(email, otp_code):
    """
    Send out otp code email in registration process.

    :param email:
    :param otp_code:
    :return:
    """
    msg_html = render_to_string('email_confirm_otp.html', {'otp_code': otp_code})
    msg_text = html2text.html2text(msg_html)
    # print("msg text", msg_text)

    subject = "Hi 👋🏻, 你的Surgi註冊驗證碼是%s" % otp_code

    try:
        send_mail(subject, msg_text, EMAIL_WITH_DISPLAY_NAME,
                [email], html_message=msg_html)
    except Exception as e:
        logger.error("[Error] send_otp_code: %s" % str(e))


@shared_task
def send_registration_success(email):
    """
    Send out otp code email in registration process.

    :param email:
    :param otp_code:
    :return:
    """
    msg_html = render_to_string('success_register.html')
    msg_text = html2text.html2text(msg_html)

    subject = "你已成功註冊Surgi！開始評估適合你的醫美項目"

    try:
        send_mail(subject, msg_text, EMAIL_WITH_DISPLAY_NAME,
                [email], html_message=msg_html)
    except Exception as e:
        logger.error("[Error] send_registration_success: %s" % str(e))


@shared_task
def send_forget_pw_reset(email):
    """
    Send out forget pw email in registration process.

    :param email:
    :param otp_code:
    :return:
    """
    msg_html = render_to_string('email_confirm_otp.html')
    msg_text = html2text.html2text(msg_html)

    subject = "Surgi帳戶重設密碼"

    try:
        send_mail(subject, msg_text, EMAIL_WITH_DISPLAY_NAME,
                [email], html_message=msg_html)
    except Exception as e:
        logger.error("[Error] send_registration_success: %s" % str(e))

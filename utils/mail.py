"""
Module for sending a emails
"""
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import get_template

from core.models import User


def send_activation_link(recipient, uid, token):
    """Send user activation email with link on signup"""

    user = User.objects.get(pk=uid)
    base = settings.AAD_BASE_URL
    subject = settings.AAD_SUBJECT
    full_url = "{}uid={}&token={}".format(base, uid, token)
    context = {"name": user.first_name, "activation_link": full_url}
    html_content = get_template(
        "activate_account.html").render(context)

    mail = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=settings.EMAIL_HOST_USER,
        to=[recipient]
        # reply_to=[settings.EMAIL_HOST_USER]
    )
    mail.content_subtype = 'html'
    return mail.send()


def send_password_reset_link(token, email):
    """Sending the Password Reset Link"""

    base = settings.PRD_BASE_URL
    subject = settings.PRD_SUBJECT
    user = User.objects.get(email=email)
    full_url = "{}?token={}".format(
        base,
        token,
    )
    context = {"name": user.first_name, "password_reset_link": full_url}
    html_content = get_template(
        "reset_password.html").render(context)

    mail = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=settings.EMAIL_HOST_USER,
        to=[email]
        # reply_to=[settings.EMAIL_HOST_USER]
    )
    mail.content_subtype = 'html'
    return mail.send()

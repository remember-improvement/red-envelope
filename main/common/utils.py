from curses.ascii import US
from datetime import datetime, timezone
from django.core.exceptions import ValidationError
from redenvelopes.models import RedenvelopeReward
from django.contrib.auth.models import User
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.template.loader import render_to_string
from smtplib import SMTPException
from django.template.loader import get_template
def get_current_time_in_utc_timezone():
    return datetime.now(timezone.utc)

def validate_username(value):
        is_username_exist=User.objects.filter(username=value).exists()
        if is_username_exist:
            raise ValidationError("username is existed")
        
def validate_bank_account(value):
    is_bankaccount_exist = RedenvelopeReward.objects.filter(bank_account=value).exists()
    if is_bankaccount_exist:
        raise ValidationError("bank account is existed")

def validate_ip_address(value):
    is_ipaddress_exist = RedenvelopeReward.objects.filter(ip_address=value)
    if is_ipaddress_exist.count() > 2:
        raise ValidationError("ip address is existed")
def validate_email_address(value):
    is_email_exist = User.objects.filter(email=value).exists()
    if is_email_exist:
        raise ValidationError("email is existed")
def render_and_il(subject, recipient_list, placeholders, template_name):
    sender = settings.EMAIL_HOST_USER
    plaintext = get_template(f'{template_name}.txt').render(placeholders)
    html = get_template(f'{template_name}.html').render(placeholders)
    send_mail(subject, plaintext, sender, recipient_list, html_message=html)
def send_success_email(receiver_email,receiver_name,prize):
    subject = "恭喜發財，您的紅包來啦！"
    receiver_list = [receiver_email]
    content = {
        'username':receiver_name,
        'prize':prize,
    }
    template_name = 'success_reminder_letter'
    try:
        render_and_il(subject,receiver_list,content,template_name)
    except Exception as e:
        print(e)

from http.client import OK
from ipaddress import ip_address
from django.contrib.messages.api import error
from redenvelopes.serializers import AddRewardPayloadSerailizer
from django.shortcuts import render,redirect
from redenvelopes.models import RedenvelopeReward
from rest_framework import serializers, viewsets
from django.http import HttpResponse, JsonResponse, HttpRequest
from redenvelopes.serializers import AddRewardPayloadSerailizer
from django.db import transaction
from rest_framework.response import Response
from redenvelopes.forms import LoginPostForm
from django.shortcuts import render
import datetime
from django.views.generic import TemplateView
import random
from django.core.exceptions import ValidationError
from common.utils import validate_username,validate_bank_account,validate_ip_address,validate_email_address,send_success_email
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator
from django.core.mail import get_connection, send_mail
from django.db.models import Max

# Create your views here.
   


def login_and_get_redenvelope(request):
    login_template_name = 'login.html'
    success_template_name = 'success.html'
    if request.method == 'GET':
        # is_ipaddress_exist = RedenvelopeReward.objects.filter(ip_address='127.0.0.1')
        # if is_ipaddress_exist.count() > 3:
        #     return HttpResponse("fail")
        # return HttpResponse("OK")
        #form = LoginPostForm()
        query_set = RedenvelopeReward.objects.order_by('-prize')
        query_set_first = query_set.first()
        if query_set_first is None:
            lucky_guy = ""
        else:
            lucky_guy_obj = User.objects.get(id=query_set_first.user_id)
            lucky_guy = lucky_guy_obj.username
        return render(request,login_template_name,{'lucky_guy':lucky_guy})
    if request.method == "POST":
        form = LoginPostForm(request.POST)
        if form.is_valid():
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0] 
            else:
                ip = request.META.get('REMOTE_ADDR')
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            bank_account = form.cleaned_data['bank_account']
            # try:
            #     validate_username(username)
            # except:
            #     return render(request,login_template_name,{'message':'使用者名稱不能重複喔～','error':True})
            # try:
            #     validate_bank_account(bank_account)
            # except:
            #     return render(request,login_template_name,{'message':'銀行帳號不能重複喔～','error':True})
            # try:
            #     validate_email_address(email)
            # except:
            #     return render(request,login_template_name,{'message':'電子郵件不能重複喔～','error':True})
            try:
                validate_ip_address(ip)
            except:
                return render(request,login_template_name,{'message':'你已經抽過囉～','error':True})
            username_dict = {'王兆安':2000,'陳盈臻':666,'吳祖昀':500,'常亦頡':666,'潘彥翰':500,'李宛亭':888,'李仲嘉':2000,'李佳縈':500,'蔡汶翰':999,'彭瑀芊':500,'石智瑋':1000,'吳予茿':300}
            is_user_exist = User.objects.filter(username=username).exists()
            if username in username_dict:
                    guaranteed = username_dict[username]
                    prize = random.randrange(int(guaranteed*0.5), int(guaranteed*2), 50)
            else:
                return render(request,login_template_name,{'message':'用戶名稱要用本名喔！','error':True})
            if not is_user_exist:
                user = User.objects.create(username=username,email=email)
                user.save()
            user = User.objects.filter(username=username).first()  
            RedenvelopeReward.objects.create(bank_account=bank_account,user=user,ip_address=ip,prize=prize)
            send_success_email(receiver_email=email,receiver_name=username,prize=prize)
            

            return render(request,success_template_name,{'prize':prize})
   

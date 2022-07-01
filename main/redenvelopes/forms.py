from redenvelopes.models import RedenvelopeReward
from django import forms
from django.contrib.auth.models import User
import random

class LoginPostForm(forms.Form):
    username = forms.CharField(label='username', max_length=100,required=True) #max_length 瀏覽器限制使用者輸入的字串長度
    bank_account = forms.CharField(label='bank_account', max_length=100, required=True)
    email = forms.CharField(label='email',required=True)
    class Meta:
        model = RedenvelopeReward
        fileds=('username','bank_account')



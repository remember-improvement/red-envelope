from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.forms import CharField
# Create your models here.


class Hello(models.Model):
    test = models.CharField(max_length=200)


class RedenvelopeReward(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='redenvelope')
    bank_account = models.CharField(max_length=200,null=True)
    prize = models.IntegerField(validators=[MaxValueValidator(3000),MinValueValidator(1)],null=True)
    ip_address = models.CharField(max_length=200,null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'redenvelopes'
    
    def __str__(self):
        return str(self.user)
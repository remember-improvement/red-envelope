
from common.utils import get_current_time_in_utc_timezone
from rest_framework.fields import IntegerField
from redenvelopes.models import RedenvelopeReward
from django.conf import settings
import random
from lottery.exception import ErrorEnum
from rest_framework.serializers import Serializer, ListField, ValidationError,\
    CharField, PrimaryKeyRelatedField, ChoiceField


class AddRewardPayloadSerailizer(Serializer):
    username = CharField(required=True)
    bank_account = CharField(required=True)
    
    def validate_username(self,value):
        is_username_exist=RedenvelopeReward.objects.filter(username=value).exists()
        if is_username_exist:
            raise ValidationError("username is existed")
        return value
    def validate_bank_account(self,value):
        is_bankaccount_exist = RedenvelopeReward.objects.filter(bank_account=value).exists()
        if is_bankaccount_exist:
            raise ValidationError("bank account is existed")
        return value
    
    def create(self,validated_data):
        prize= random.randint(1,3000)
        validated_data['prize'] = prize
        validated_data['create_date'] = get_current_time_in_utc_timezone()
        reward = RedenvelopeReward.objects.create(**validated_data)
        return reward
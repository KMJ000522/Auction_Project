# payments/serializers.py
from rest_framework import serializers
from .models import Wallet, Transaction

class DepositSerializer(serializers.Serializer):
    """
    [Level 3] 충전 요청용 시리얼라이저
    - 모델을 그대로 쓰지 않고, 필요한 데이터(amount)만 딱 받기 위해 일반 Serializer 사용
    """
    amount = serializers.IntegerField(min_value=100) # 최소 100원 이상 충전 가능

class TransactionSerializer(serializers.ModelSerializer):
    """
    거래 내역 조회용
    """
    class Meta:
        model = Transaction
        fields = ('amount', 'transaction_type', 'description', 'created_at')
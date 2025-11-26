# auctions/serializers.py
from rest_framework import serializers
from .models import Auction

class AuctionListSerializer(serializers.ModelSerializer):
    # 목록 조회용: 필요한 정보만 가볍게 보여줌
    seller = serializers.ReadOnlyField(source='seller.username')

    class Meta:
        model = Auction
        fields = ('id', 'title', 'seller', 'current_price', 'status', 'end_time')

class AuctionDetailSerializer(serializers.ModelSerializer):
    # 상세 조회용: 모든 정보 포함
    seller = serializers.ReadOnlyField(source='seller.username')

    class Meta:
        model = Auction
        fields = '__all__'
        read_only_fields = ('seller', 'current_price', 'status') # 맘대로 수정 불가
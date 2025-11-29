from rest_framework import serializers
# [수정 포인트] Auction 옆에 Bid를 추가했습니다!
from .models import Auction, Bid 

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

# [추가했던 입찰 시리얼라이저]
class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ('amount',) # 얼마 입찰할 건지만 받음

    def validate_amount(self, value):
        # 최소 1원 이상이어야 함
        if value <= 0:
            raise serializers.ValidationError("입찰액은 0보다 커야 합니다.")
        return value
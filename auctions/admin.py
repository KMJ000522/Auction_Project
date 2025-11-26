from django.contrib import admin
from .models import Auction, Bid

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    # [Level 3] 관리자 목록에서 핵심 정보 한눈에 보기
    list_display = ('id', 'title', 'seller', 'current_price', 'status', 'end_time')
    # 우측에 필터 사이드바 생성 (상태별 보기)
    list_filter = ('status',)
    # 검색 기능 추가
    search_fields = ('title', 'seller__username')

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('id', 'auction', 'bidder', 'amount', 'created_at')
    list_filter = ('auction',)
# auctions/views.py
from rest_framework import viewsets, permissions
from .models import Auction
from .serializers import AuctionListSerializer, AuctionDetailSerializer

class AuctionViewSet(viewsets.ModelViewSet):
    """
    경매 CRUD ViewSet
    - 목록 조회, 상세 조회, 생성, 수정, 삭제를 한번에 처리
    """
    # [Level 3] N+1 문제 해결: 
    # 경매 목록 가져올 때 판매자(seller) 정보도 미리 다 가져옴 (JOIN)
    queryset = Auction.objects.select_related('seller').all()
    
    # 인증된 사람만 글 쓰기 가능, 조회는 누구나
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        # 목록 볼 땐 가볍게, 상세 볼 땐 자세히
        if self.action == 'list':
            return AuctionListSerializer
        return AuctionDetailSerializer

    def perform_create(self, serializer):
        # [Level 3] 글쓴이 자동 할당
        # 프론트에서 보낸 데이터 + 현재 로그인한 유저(request.user)
        serializer.save(seller=self.request.user)
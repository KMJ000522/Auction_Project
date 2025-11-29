# auctions/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Auction, Bid
from .serializers import AuctionListSerializer, AuctionDetailSerializer, BidSerializer
from payments.models import Wallet

class AuctionViewSet(viewsets.ModelViewSet):
    queryset = Auction.objects.select_related('seller').all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'bid':
            return BidSerializer
        if self.action == 'list':
            return AuctionListSerializer
        return AuctionDetailSerializer

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    # 1. 입찰 기능
    @action(detail=True, methods=['post'])
    def bid(self, request, pk=None):
        auction = self.get_object()
        serializer = BidSerializer(data=request.data)

        if serializer.is_valid():
            bid_amount = serializer.validated_data['amount']

            if auction.status != Auction.Status.ACTIVE:
                return Response({"error": "진행 중인 경매가 아닙니다."}, status=400)
            if bid_amount <= auction.current_price:
                return Response({"error": "현재가보다 높게 입찰해야 합니다."}, status=400)
            if auction.seller == request.user:
                return Response({"error": "자신의 경매에는 입찰할 수 없습니다."}, status=400)

            try:
                with transaction.atomic():
                    # 상위 입찰자 환불
                    top_bid = auction.bids.order_by('-amount').first()
                    if top_bid:
                        Wallet.objects.refund_for_outbid(
                            user=top_bid.bidder,
                            amount=top_bid.amount,
                            description=f"경매({auction.title}) 상위 입찰 발생 환불"
                        )
                    
                    # 새 입찰자 결제
                    Wallet.objects.pay_for_bid(
                        user=request.user,
                        amount=bid_amount,
                        description=f"경매({auction.title}) 입찰"
                    )

                    Bid.objects.create(auction=auction, bidder=request.user, amount=bid_amount)
                    auction.current_price = bid_amount
                    auction.save()

                    return Response({
                        "status": "success", 
                        "message": "입찰 성공! (이전 입찰자는 환불되었습니다)",
                        "current_price": auction.current_price
                    }, status=status.HTTP_201_CREATED)

            except ValueError as e:
                return Response({"error": str(e)}, status=400)

        return Response(serializer.errors, status=400)

    # 2. ★ 종료(정산) 기능 [여기에 있어야 합니다!]
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        auction = self.get_object()

        if auction.status != Auction.Status.ACTIVE:
            return Response({"error": "이미 종료된 경매입니다."}, status=400)

        if auction.seller != request.user:
            return Response({"error": "판매자만 경매를 종료할 수 있습니다."}, status=403)

        top_bid = auction.bids.order_by('-amount').first()
        
        try:
            with transaction.atomic():
                if top_bid:
                    # 정산 로직 호출 (models.py에 있는 걸 가져다 씀)
                    Wallet.objects.settle_winning_bid(
                        winner=top_bid.bidder,
                        seller=auction.seller,
                        amount=top_bid.amount,
                        description=f"경매({auction.title}) 낙찰"
                    )
                    auction.status = Auction.Status.CLOSED
                    message = f"경매가 종료되었습니다. 낙찰자: {top_bid.bidder.username}, 금액: {top_bid.amount}"
                else:
                    auction.status = Auction.Status.NO_BIDS
                    message = "입찰자가 없어 유찰되었습니다."
                
                auction.save()
                return Response({"status": "success", "message": message})

        except Exception as e:
            return Response({"error": str(e)}, status=400)
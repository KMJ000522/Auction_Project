# payments/views.py (수정본)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Wallet
from .serializers import DepositSerializer

class PaymentViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    # 내 지갑 조회
    @action(detail=False, methods=['get'])
    def balance(self, request):
        wallet = request.user.wallet
        return Response({
            "user": request.user.username,
            "balance": wallet.balance,
            "locked": wallet.locked_balance
        })

    # 충전하기 
    @action(detail=False, methods=['post'])
    def deposit(self, request):
        serializer = DepositSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            
            # [Level 3] Manager 메서드 호출 (Transaction Atomic 적용됨)
            Wallet.objects.deposit(
                user=request.user,
                amount=amount,
                description="앱 내 충전"
            )
            
            # 갱신된 정보 다시 가져오기
            request.user.wallet.refresh_from_db()
            
            return Response({
                "status": "success",
                "charged_amount": amount,
                "current_balance": request.user.wallet.balance
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
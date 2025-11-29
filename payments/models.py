# payments/models.py
from django.db import models
from django.conf import settings
from django.db import transaction
from django.dispatch import receiver

class WalletManager(models.Manager):
    @transaction.atomic
    def deposit(self, user, amount, description=""):
        wallet = self.select_for_update().get(user=user)
        wallet.balance += amount
        wallet.save()
        Transaction.objects.create(
            wallet=wallet, amount=amount, transaction_type='DEPOSIT', description=description
        )
        return wallet

    @transaction.atomic
    def pay_for_bid(self, user, amount, description=""):
        wallet = self.select_for_update().get(user=user)
        if wallet.balance < amount:
            raise ValueError("잔액 부족")
        wallet.balance -= amount
        wallet.locked_balance += amount
        wallet.save()
        Transaction.objects.create(
            wallet=wallet, amount=-amount, transaction_type='BID_LOCK', description=description
        )
        return wallet

    @transaction.atomic
    def refund_for_outbid(self, user, amount, description=""):
        wallet = self.select_for_update().get(user=user)
        wallet.locked_balance -= amount
        wallet.balance += amount
        wallet.save()
        Transaction.objects.create(
            wallet=wallet, amount=amount, transaction_type='BID_REFUND', description=description
        )
        return wallet

    # ★ 여기가 중요합니다! (Manager 안에 있어야 함)
    @transaction.atomic
    def settle_winning_bid(self, winner, seller, amount, description=""):
        """낙찰 정산 로직"""
        # 1. 낙찰자 처리 (돈 나감)
        winner_wallet = self.select_for_update().get(user=winner)
        winner_wallet.locked_balance -= amount
        winner_wallet.save()
        Transaction.objects.create(
            wallet=winner_wallet, amount=-amount, transaction_type='BID_WIN', description=f"{description} (낙찰 차감)"
        )

        # 2. 판매자 처리 (돈 들어옴)
        seller_wallet = self.select_for_update().get(user=seller)
        seller_wallet.balance += amount
        seller_wallet.save()
        Transaction.objects.create(
            wallet=seller_wallet, amount=amount, transaction_type='BID_WIN', description=f"{description} (판매 수익)"
        )

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.PositiveIntegerField(default=0)
    locked_balance = models.PositiveIntegerField(default=0)
    objects = WalletManager()

class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.IntegerField()
    transaction_type = models.CharField(max_length=20)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

@receiver(models.signals.post_save, sender=settings.AUTH_USER_MODEL)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)
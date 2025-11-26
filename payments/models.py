from django.db import models
from django.conf import settings
from django.db import transaction
from django.dispatch import receiver  # <--- [수정] 이 줄이 빠져서 에러가 났었습니다!

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
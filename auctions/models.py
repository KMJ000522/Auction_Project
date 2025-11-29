from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Auction(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', '예정'
        ACTIVE = 'ACTIVE', '진행중'
        CLOSED = 'CLOSED', '종료'
        CANCELED = 'CANCELED', '취소'
        NO_BIDS = 'NO_BIDS', '유찰'  # <--- [추가] 이 줄을 꼭 넣어주세요!

    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='opened_auctions')
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_price = models.PositiveIntegerField()
    current_price = models.PositiveIntegerField(default=0)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    # max_length가 10인데 NO_BIDS는 7글자라 DB 변경 없이 그대로 써도 됩니다.
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("종료 시간 오류")
        if self.start_price < 0:
            raise ValidationError("시작가 오류")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.current_price = self.start_price
        self.full_clean()
        super().save(*args, **kwargs)

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
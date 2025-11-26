# auctions/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuctionViewSet

router = DefaultRouter()
router.register(r'', AuctionViewSet) # /auctions/ 로 접속

urlpatterns = [
    path('', include(router.urls)),
]
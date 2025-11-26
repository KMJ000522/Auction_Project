from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

# 1. User 모델 등록 (기본 UserAdmin 상속받아 비밀번호 관리 기능 유지)
admin.site.register(User, UserAdmin)

# 2. Profile 모델 등록
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'credit_score', 'phone_number') # 목록에 보여줄 필드
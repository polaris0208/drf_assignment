from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일은 필수입니다")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField("이메일", unique=True)
    username = models.CharField("닉네임", max_length=150, unique=True)
    profile_image = models.ImageField(
        "프로필 이미지", default='profile/default.png', upload_to="profile/", blank=True, null=True
    )

    followings = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followers",  # 역참조 이름
        through="Follow",  # 중간 테이블
        blank=True,
    )

    USERNAME_FIELD = "email"  # 로그인 시 이메일 사용
    REQUIRED_FIELDS = []  # 기본값 email

    objects = CustomUserManager()

    def __str__(self):
        return self.email


# 중간 테이블
class Follow(models.Model):
    follower = models.ForeignKey(
        User, related_name="followed_users", on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        User, related_name="following_users", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")  # 중복 팔로우 방지

    def __str__(self):
        return f"{self.follower} follows {self.following}"

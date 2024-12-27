from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import re

def extract_hashtags(content):
    hashtags = re.findall(r"#([0-9a-zA-Z가-힣_]+)", content)  # # 뒤에 오는 단어들 찾기
    return hashtags

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

def products_image_path(instance, filename):
    return f"products/{instance.user.username}/{filename}"

def validation_hashtag(value):
    if not re.match(r"^[0-9a-zA-Z가-힣_]+$", value):
        raise ValidationError("올바르지 않은 해시태그 형식.")

class HashTag(models.Model):
    name = models.CharField(max_length=50, unique=True, validators=[validation_hashtag])

    def __str__(self):
        return f"#{self.name}"

class Products(models.Model):
    title = models.CharField(max_length=50)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    product_name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to=products_image_path, blank=True, null=True)
    like_user = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="like_products",
        blank=True
    )
    hashtags = models.ManyToManyField(HashTag, related_name='products', blank=True)
    views = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', blank=True)

    def __str__(self):
        return self.title

    @property
    def like_user_counter(self):
        return self.like_user.count()

    def view_counter(self):
        self.views += 1
        self.save()
        return self.views

    def add_like(self, user):
        if self.author == user:
            raise ValidationError("자신의 상품은 좋아요/찜 불가")
        self.like_user.add(user)

    def remove_like(self, user):
        if self.author == user:
            raise ValidationError("자신의 상품은 좋아요/찜 취소 불가.")
        self.like_user.remove(user)

    def save(self, *args, **kwargs):
        # 해시태그 자동 추출
        hashtags = extract_hashtags(self.content)  # content에서 해시태그 추출
        hashtag_objects = []
        
        # 해시태그 객체가 없으면 생성하여 리스트에 추가
        for hashtag in hashtags:
            hashtag_obj, created = HashTag.objects.get_or_create(name=hashtag)
            hashtag_objects.append(hashtag_obj)
        
        # 먼저 객체를 저장
        super().save(*args, **kwargs)
        
        # 그 후에 해시태그 연결
        self.hashtags.set(hashtag_objects)
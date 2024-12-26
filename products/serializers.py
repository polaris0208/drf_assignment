from rest_framework import serializers
from .models import Category, HashTag, Products, extract_hashtags

class HashTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HashTag
        fields = ['id', 'name']  # id와 name을 반환

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']  # id와 name을 반환

class ProductSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    like_user_counter = serializers.ReadOnlyField()
    hashtags = HashTagSerializer(many=True, read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all()) # Post에만 작동 / DB에 간섭

    class Meta:
        model = Products
        exclude = ['like_user', 'views']  # 'views'와 'like_user'는 직렬화에서 제외

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 'request'가 context에 존재하는지 확인
        request = self.context.get('request')
        if request and request.method == 'POST':
            self.fields.pop('hashtags', None)

    def create(self, validated_data):
        # 새로운 상품을 생성할 때 현재 사용자 자동 설정
        validated_data['author'] = self.context['request'].user  # 요청한 사용자가 author로 자동 설정
        validated_data['views'] = 0  # 조회수 초기값 설정 (상품 생성 시 자동으로 0으로 설정)
        product = super().create(validated_data)
        
        # 해시태그 자동 추출 처리
        hashtags = extract_hashtags(product.content)  # content에서 해시태그 추출
        hashtag_objects = []
        for hashtag in hashtags:
            hashtag_obj, created = HashTag.objects.get_or_create(name=hashtag)
            hashtag_objects.append(hashtag_obj)
        product.hashtags.set(hashtag_objects)  # 해시태그 연결
        product.save()

        return product

    def update(self, instance, validated_data):
        # 기존 상품 수정 시 작성자 정보, 해시태그, 조회수, 좋아요는 수정하지 않음
        validated_data.pop('author', None)
        validated_data.pop('hashtags', None)  # 해시태그 수정은 제외
        validated_data.pop('views', None)
        validated_data.pop('like_user', None)

        # 상품을 업데이트한 후, 해시태그 자동 추출
        instance = super().update(instance, validated_data)
        
        # content에서 해시태그 추출 및 업데이트
        hashtags = extract_hashtags(instance.content)  # content에서 해시태그 추출
        hashtag_objects = []
        for hashtag in hashtags:
            hashtag_obj, created = HashTag.objects.get_or_create(name=hashtag)
            hashtag_objects.append(hashtag_obj)
        
        instance.hashtags.set(hashtag_objects)  # 해시태그 연결
        instance.save()

        return instance

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "password", "password2", "username", "profile_image")

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "비밀번호 불일치"})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):

    class FollowSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ("id", "email", "username", "profile_image")

    followers = FollowSerializer(many=True, read_only=True)
    followings = FollowSerializer(many=True, read_only=True)
    follower_count = serializers.IntegerField(source="followers.count", read_only=True)
    following_count = serializers.IntegerField(
        source="followings.count", read_only=True
    )
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "profile_image",
            "followings",
            "followers",
            "follower_count",
            "following_count",
        ]

    def get_profile_image(self, obj):
        request = self.context.get("request")
        if obj.profile_image:
            return request.build_absolute_uri(obj.profile_image.url)
        return None


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "profile_image")


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    # 현재 비밀번호 확인
    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise ValidationError("올바르지 않은 비밀번호")
        return value

    # 새 비밀번호 확인
    def validate_new_password(self, value):
        user = self.context["request"].user
        if user.check_password(value):
            raise ValidationError("동일한 비밀번호")

        try:
            validate_password(value)
        except ValidationError as e:
            raise ValidationError(f'유효하지 않은 비밀번호 : {", ".join(e.messages)}')

        return value

    def save(self):
        user = self.context["request"].user
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save()

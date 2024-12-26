from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import (
    SignupSerializer,
    UserUpdateSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer,
)
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import OpenApiExample

User = get_user_model()

"""
@authentication_classes([]) : 전역 인증 설정 무시
@permission_classes([AllowAny]) : 전역 IsAuthenticated 설정 무시
"""


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "회원가입 성공"},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])  # 인증이 필요한 경우 인증 클래스 추가
@permission_classes([IsAuthenticated])  # 로그인된 사용자만 접근 가능
def resign(request):
    password = request.data.get("password")  # 요청 데이터에서 비밀번호 받기
    user = request.user  # 현재 요청을 보낸 사용자 정보

    # 비밀번호 확인
    user = authenticate(email=user.email, password=password)
    if user is None:
        return Response(
            {"message": "비밀번호가 일치하지 않습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # 비밀번호가 일치하면 계정 삭제
        user.delete()
        return Response(
            {"message": "회원 탈퇴가 완료되었습니다."},
            status=status.HTTP_204_NO_CONTENT,
        )
    except User.DoesNotExist:
        return Response(
            {"message": "사용자를 찾을 수 없습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def login(request):
    email = request.POST.get("email")
    password = request.POST.get("password")

    user = authenticate(request, email=email, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return JsonResponse(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "message": "로그인 성공",
            },
            status=200,
        )
    else:
        return JsonResponse({"error": "올바르지 않은 이메일"}, status=400)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "로그아웃 성공"})
    except Exception:
        return Response({"error": "로그아웃 실패"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH"])
def profile(request):
    user = request.user

    if request.method == "GET":
        serializer = UserProfileSerializer(user, context={"request": request})
        return Response(serializer.data, status=200)

    if request.method in ("PUT", "PATCH"):
        serializer = UserUpdateSerializer(
            instance=user, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "회원정보 수정 성공",
                    "user": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def follow(request, user_pk):
    profile_user = get_object_or_404(User, pk=user_pk)
    me = request.user

    if me == profile_user:
        return Response(
            {"error": "자신은 팔로우 불가"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if me.followings.filter(pk=profile_user.pk).exists():
        me.followings.remove(profile_user)
        is_followed = False
        message = f"{profile_user.email} 팔로우 취소"
    else:
        me.followings.add(profile_user)
        is_followed = True
        message = f"{profile_user.email} 팔로우"

    return Response(
        {
            "is_followed": is_followed,
            "message": message,
        },
        status=status.HTTP_200_OK,
    )


from rest_framework.views import APIView


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "비밀번호 변경 성공"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

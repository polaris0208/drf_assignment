from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404  # 추가: get_object_or_404 임포트
from .models import Products, Category
from .serializers import ProductSerializer, CategorySerializer
from drf_spectacular.utils import extend_schema
from rest_framework.pagination import PageNumberPagination


class ProductListCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]  # 인증된 사용자만 접근 가능
    
    def get(self, request):
        # 모든 상품 목록 조회
        products = Products.objects.all().order_by("-created_at")

        paginator = PageNumberPagination()
        paginator.page_size = 5
        paginated_products = paginator.paginate_queryset(products, request)

        serializer = ProductSerializer(paginated_products, many=True)
        # return Response(serializer.data)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        # 새로운 상품 생성
        serializer = ProductSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()  # 자동으로 author가 현재 사용자로 설정됨
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]  # 인증된 사용자만 접근 가능

    def get(self, request, pk):
        # 특정 상품 조회 및 조회수 증가
        product = get_object_or_404(Products, pk=pk)  # get_object_or_404 사용

        # 조회수 증가
        views = product.view_counter()

        # 상품 정보를 반환
        serializer = ProductSerializer(product)
        return Response({"product": serializer.data, "views": views})

    def put(self, request, pk):
        # 상품 정보 수정
        product = get_object_or_404(Products, pk=pk)  # get_object_or_404 사용

        # 상품 수정 권한 체크 (자신의 상품만 수정 가능)
        if product.author != request.user:
            return Response(
                {"detail": "You do not have permission to edit this product."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # 상품 삭제
        product = get_object_or_404(Products, pk=pk)  # get_object_or_404 사용

        # 상품 삭제 권한 체크 (자신의 상품만 삭제 가능)
        if product.author != request.user:
            return Response(
                {"detail": "You do not have permission to delete this product."},
                status=status.HTTP_403_FORBIDDEN,
            )

        product.delete()
        return Response(
            {"detail": "Product deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class ProductLikeView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def post(self, request, pk):
        # 좋아요 추가
        product = get_object_or_404(Products, pk=pk)  # get_object_or_404 사용

        # 자신이 작성한 상품에는 좋아요를 추가할 수 없음
        if product.author == request.user:
            return Response(
                {"detail": "You cannot like your own product."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product.add_like(request.user)
        return Response({"detail": "Liked successfully."}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        # 좋아요 제거
        product = get_object_or_404(Products, pk=pk)  # get_object_or_404 사용

        # 자신이 작성한 상품에는 좋아요를 제거할 수 없음
        if product.author == request.user:
            return Response(
                {"detail": "You cannot unlike your own product."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product.remove_like(request.user)
        return Response({"detail": "Unliked successfully."}, status=status.HTTP_200_OK)


class CategoryListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        categories = Category.objects.all()  # 모든 카테고리 가져오기
        serializer = CategorySerializer(categories, many=True)  # 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)

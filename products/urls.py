from django.urls import path
from .views import ProductListCreateView, ProductDetailView, ProductLikeView, CategoryListView

app_name = "products"
urlpatterns = [
    path('', ProductListCreateView.as_view(), name='products'),
    path('<int:pk>/', ProductDetailView.as_view(), name='detail'),
    path('<int:pk>/like/', ProductLikeView.as_view(), name='like'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
]
from django.contrib import admin
from .models import Products, Category


class ProductAdmin(admin.ModelAdmin):
    list_display = ["title", "price", "quantity", "category"]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]


admin.site.register(Products, ProductAdmin)
admin.site.register(Category, CategoryAdmin)

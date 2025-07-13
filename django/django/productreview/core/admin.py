from django.contrib import admin
from .models import Product, Review

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user__username', 'product__name')

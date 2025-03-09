from django.contrib import admin
from . import models
from mptt.admin import DraggableMPTTAdmin

# Custom filter for deleted status
class DeletedFilter(admin.SimpleListFilter):
    title = 'Deleted Status'
    parameter_name = 'is_deleted'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Deleted'),
            ('no', 'Not Deleted'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(is_deleted=True)
        if self.value() == 'no':
            return queryset.filter(is_deleted=False)
        return queryset

# Custom filter for publish status
class PublishedFilter(admin.SimpleListFilter):
    title = 'Published Status'
    parameter_name = 'is_published'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Published'),
            ('no', 'Not Published'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(is_published=True)
        if self.value() == 'no':
            return queryset.filter(is_published=False)
        return queryset

# Product Admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'created_at', 'is_deleted', 'is_published']  # Ensure these fields exist
    search_fields = ['name', 'description']
    list_filter = ['created_at', DeletedFilter, PublishedFilter, 'size', 'color']  # Add custom filters
    ordering = ['-created_at']

# Favorite Product Admin
class FavoriteProductAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['user', 'product']
    ordering = ['-created_at']

# Color Product Admin
class ColorProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']  # Ensure 'name' exists
    search_fields = ['name']
    ordering = ['name']

# Size Product Admin
class SizeProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'size']  # Ensure 'size' exists
    search_fields = ['size']
    ordering = ['id']

# Images Product Admin
class ImagesProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'image', 'uploaded_at']  # Ensure these fields exist
    list_filter = ['product']
    ordering = ['-uploaded_at']

# Specifications Product Admin
class SpecificationsProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'title', 'desc']  # Ensure these fields exist
    list_filter = ['product']
    ordering = ['product']

# Comment Product Admin
class CommentProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'created_at', 'is_approved']  # Ensure these fields exist
    list_filter = ['product', 'user', 'is_approved']
    search_fields = ['comment']
    ordering = ['-created_at']

# Vote Comment Admin
class VoteCommentAdmin(admin.ModelAdmin):
    list_display = ['comment', 'user', 'vote_type', 'created_at']
    list_filter = ['vote_type']
    ordering = ['-created_at']

# Category Product Admin
class CategoryProductAdmin(DraggableMPTTAdmin):
    list_display = ['tree_actions', 'indented_title']
    list_filter = ['is_active']
    list_display_links = ['indented_title']
    search_fields = ['name']
    ordering = ['name']

# Register models
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.FavoriteProduct, FavoriteProductAdmin)
admin.site.register(models.ColorProduct, ColorProductAdmin)
admin.site.register(models.SizeProduct, SizeProductAdmin)
admin.site.register(models.ImagesProduct, ImagesProductAdmin)
admin.site.register(models.SpecificationsProduct, SpecificationsProductAdmin)
admin.site.register(models.CommentProduct, CommentProductAdmin)
admin.site.register(models.VoteComment, VoteCommentAdmin)
admin.site.register(models.CategoryProduct, CategoryProductAdmin)
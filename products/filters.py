from django_filters import rest_framework as filters
from .models import Product, CategoryProduct


class ProductFilter(filters.FilterSet):
    order_by = filters.OrderingFilter(
        fields=('price', 'favorites_count', 'avg_rating', 'name', 'comments_count', 'created_at')
        )
    price = filters.RangeFilter()
    category = filters.CharFilter(method='filter_by_category')
    color = filters.CharFilter(field_name='color__name', lookup_expr='iexact')
    size = filters.CharFilter(field_name='size__size', lookup_expr='iexact')


    def filter_by_category(self, queryset, name, value):
        try:
            category = CategoryProduct.objects.get(slug=value)
            descendants = category.get_descendants(include_self=True)
            return queryset.filter(category__in=descendants)
        except CategoryProduct.DoesNotExist:
            return queryset.none()

    class Meta:
        model = Product
        fields = ['order_by', 'price', 'category', 'color', 'size']

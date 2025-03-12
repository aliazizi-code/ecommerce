from django.urls import path
from products import views


urlpatterns = [
    # Products
    path('', views.ProductsListViewSet.as_view({'get': 'list'}), name='product-list'),
    path('<int:id>/', views.ProductDetailView.as_view(), name='product-detail'),
    
    # Categories
    path('categories/', views.CategoriesListView.as_view(), name='category-list'),

    # Favorites
    path('favorites/', views.FavoriteProductView.as_view(), name='favorite-product'),

    # Comments
    path('<int:id>/comments/', views.ProductCommentsListView.as_view(), name='comments-list'),
    path('comments/vote/', views.VoteCommentView.as_view(), name='vote-comment'),
    path('comments/create/', views.CreateCommentView.as_view(), name='create-comment'),

    # Colors and Sizes
    path('colors/', views.ColorListView.as_view(), name='color-list'),
    path('sizes/', views.SizeListView.as_view(), name='size-list'),
]
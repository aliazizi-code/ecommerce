from django.urls import path
from products import views


urlpatterns = [
    path('', views.ProductsListViewSet.as_view({'get': 'list'}), name='product-list'),
    path('detail/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('category/', views.CategoriesListView.as_view(), name='category'),
    path('like/', views.FavoriteProductView.as_view(), name='like'),
    path('vote-comment/', views.VoteCommentView.as_view(), name='vote-comment'),
    path('comments/<slug:slug>/', views.ProductCommentsView.as_view(), name='comments'),
    path('color-list/', views.ColorListViewSet.as_view({'get': 'list'}), name='color-list'),
]
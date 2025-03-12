from django.urls import path
from products import views


urlpatterns = [
    path('', views.ProductsListViewSet.as_view({'get': 'list'}), name='product-list'),
    path('detail/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('category/', views.CategoriesListView.as_view(), name='category'),
    path('like/', views.FavoriteProductView.as_view(), name='like'),
    path('vote-comment/', views.VoteCommentView.as_view(), name='vote-comment'),
    path('comments/<slug:slug>/', views.ProductCommentsListView.as_view(), name='comments-list'),
    path('color-list/', views.ColorListView.as_view(), name='color-list'),
    path('size-list/', views.SizeListView.as_view(), name='size-list'),
    path('create-comment/', views.CreateCommentView.as_view(), name='create-comment'),
]
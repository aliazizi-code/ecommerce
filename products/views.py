from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404, get_list_or_404
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from products.models import (
    Product,
    CategoryProduct,
    FavoriteProduct,
    VoteComment,
    ColorProduct,
    SizeProduct,
)
from products.serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    CategoryWithChildrenSerializer,
    FavoriteProductSerializer,
    VoteCommentSerializer,
    CommentWithRepliesSerializer,
    ColorProductSerializer,
    SizeProductSerializer,
    CommentOrReplySerializer,
)


class ProductsListViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_published=True, is_deleted=False)
    serializer_class = ProductListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter


class ProductDetailView(generics.ListAPIView):
    serializer_class = ProductDetailSerializer

    def get_queryset(self):
        product_id = self.kwargs['id']
        return get_list_or_404(Product, id=product_id, is_published=True, is_deleted=False)


class CategoriesListView(generics.ListAPIView):
    serializer_class = CategoryWithChildrenSerializer
    queryset = CategoryProduct.objects.filter(parent=None, is_active=True)


@method_decorator(ratelimit(key='user', rate='5/s', method='POST', block=True), name='dispatch')
class FavoriteProductView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteProductSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            product = get_object_or_404(Product, id=data['product_id'], is_published=True, is_deleted=False)

            like, created = FavoriteProduct.objects.get_or_create(user=request.user, product_id=product.id)  

            action = 'added to favorite' if created else 'removed from favorite' 
            if not created:
                like.delete()

            return Response({"message": f"You have {action} this product."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@method_decorator(ratelimit(key='user', rate='5/s', method='POST', block=True), name='dispatch')
class VoteCommentView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VoteCommentSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            result = VoteComment.toggle_vote(comment_id=data['comment_id'], user=request.user, vote_type=data['vote_type'])

            message = {
                "VOTE_REGISTERED": "Your vote has been registered.",
                "VOTE_REMOVED": "Your vote has been removed.",
                "VOTE_CHANGED": "Your vote has been changed.",
                "COMMENT_NOT_FOUND": "Comment not found"
            }.get(result, "Unexpected result.")

            return Response({"message": message}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductCommentsListView(generics.ListAPIView):
    serializer_class = CommentWithRepliesSerializer

    def get_queryset(self):
        product_id = self.kwargs['id']
        product = get_object_or_404(Product, id=product_id, is_published=True, is_deleted=False)
        return product.comments.filter(is_approved=True, parent_comment__isnull=True).order_by('-created_at')


class ColorListView(generics.ListAPIView):
    queryset = ColorProduct.objects.all()
    serializer_class = ColorProductSerializer
    

class SizeListView(generics.ListAPIView):
    queryset = SizeProduct.objects.all()
    serializer_class = SizeProductSerializer


class CreateCommentView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentOrReplySerializer

    def perform_create(self, serializer):
        serializer.save()


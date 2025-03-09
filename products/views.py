from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from products.models import Product, CategoryProduct, FavoriteProduct, VoteComment, ColorProduct, SizeProduct
from django.shortcuts import get_list_or_404
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from products.serializers import (
    ProductsListSerializer,
    ProductDetailSerializer,
    CategorySerializer,
    FavoriteProductSerializer,
    VoteCommentSerializer,
    CommentsAndRepliesSerializer,
    ColorProductSerializer,
    SizeProductSerializer,
)


class ProductsListViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_published=True, is_deleted=False)
    serializer_class = ProductsListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter


class ProductDetailView(APIView):
    serializer_class = ProductDetailSerializer

    def get(self, request, slug):
        product = get_list_or_404(Product, slug=slug, is_published=True, is_deleted=False)
        serializer = self.serializer_class(product, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoriesListView(APIView):
    serializer_class = CategorySerializer

    def get(self, request):
        category = CategoryProduct.objects.filter(parent=None, is_active=True)
        serializer = self.serializer_class(category, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(ratelimit(key='user', rate='5/s', method='POST', block=True), name='dispatch')
class FavoriteProductView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteProductSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            product = get_list_or_404(Product, slug=data['product_slug'], is_published=True, is_deleted=False)

            like, created = FavoriteProduct.objects.get_or_create(user=request.user, product_id=product[0].id)  

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


class ProductCommentsView(APIView):
    serializer_class = CommentsAndRepliesSerializer

    def get(self, request, slug):
        product = get_list_or_404(Product, slug=slug, is_published=True, is_deleted=False)

        comments = product[0].comments.filter(is_approved=True, parent_comment__isnull=True).order_by('-created_at')

        serializer = self.serializer_class(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ColorListView(generics.ListAPIView):
    queryset = ColorProduct.objects.all()
    serializer_class = ColorProductSerializer
    

class SizeListView(generics.ListAPIView):
    queryset = SizeProduct.objects.all()
    serializer_class = SizeProductSerializer


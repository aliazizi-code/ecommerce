from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from products.models import Product, CategoryProduct, FavoriteProduct, VoteComment
from django.shortcuts import get_list_or_404
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from products.serializers import (
    ProductsListSerializer,
    ProductDetailSerializer,
    CategorySerializer,
    FavoriteProductSerializer,
    VoteCommentSerializer,
    CommentProductSerializer
)



class ProductsListView(APIView):
    serializer_class = ProductsListSerializer

    def get(self, request):
        products = Product.objects.filter(is_published=True, is_delete=False)
        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductDetailView(APIView):
    serializer_class = ProductDetailSerializer

    def get(self, request, slug):
        product = get_list_or_404(Product, slug=slug, is_published=True, is_delete=False)
        serializer = self.serializer_class(product, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoriesListView(APIView):
    serializer_class = CategorySerializer

    def get(self, request):
        category = CategoryProduct.objects.all()
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
            product = get_list_or_404(Product, slug=data['product_slug'], is_published=True, is_delete=False)

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
    serializer_class = CommentProductSerializer

    def get(self, request, slug):
        product = get_list_or_404(Product, slug=slug, is_published=True)

        comments = product[0].comments.filter(is_published=True, parent_comment__isnull=True).order_by('-created_at')

        serializer = self.serializer_class(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

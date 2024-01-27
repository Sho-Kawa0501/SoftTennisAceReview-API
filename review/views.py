from rest_framework import viewsets,generics,serializers
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from review import serializers
from review import models
from review.models import UserReview
from rest_framework import status,permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from reviewsite.utils.image import resize_image,delete_image_from_s3
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound
from PIL import Image
import io
import jwt
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError
from django.conf import settings
from django.db import transaction

User = get_user_model()
logger = logging.getLogger(__name__)


#ログインしているユーザー以外のユーザーが投稿したレビューを取得
class OtherUsersReviewListView(APIView):
  serializer_class = serializers.ReviewSerializer
  authentication_classes = ()

  def get_queryset(self):
    item_id = self.kwargs.get('item_id', None)
    if item_id:
      return models.Review.objects.exclude(user=self.request.user).filter(item__id=item_id).order_by('-created_at')
    return models.Review.objects.exclude(user=self.request.user).order_by('-created_at')

  def get(self, request, *args, **kwargs):
    queryset = self.get_queryset()
    serializer = self.serializer_class(queryset, many=True, context={'request': request})
    return Response(serializer.data)


class ReviewListItemFilterView(APIView):
  serializer_class = serializers.ReviewSerializer
  permission_classes = (AllowAny,)

  def get_queryset(self):
    item_id = self.kwargs.get('item_id', None)
    return models.Review.objects.filter(item__id=item_id).order_by('-created_at')

  def get(self, request, *args, **kwargs):
    queryset = self.get_queryset()
    serializer = self.serializer_class(queryset, many=True, context={'request': request})
    return Response(serializer.data)


class MyReviewListView(APIView):
  serializer_class = serializers.ReviewSerializer
  authentication_classes = [JWTAuthentication,]

  def get_queryset(self):
    return models.Review.objects.filter(user=self.request.user,).order_by('-created_at')

  def get(self, request, *args, **kwargs):
    queryset = self.get_queryset()
    serializer = self.serializer_class(queryset, many=True, context={'request': request})
    return Response(serializer.data)


class CreateReviewView(generics.CreateAPIView):
  queryset = models.Review.objects.all()
  serializer_class = serializers.ReviewSerializer
  authentication_classes = (JWTAuthentication,)
  parser_classes = (MultiPartParser, FormParser)

  def perform_create(self, serializer):
    image = self.request.FILES.get('image')
    image_file = None
    if image:
      with Image.open(image) as img:
        resized_image = resize_image(img)
      image_io = io.BytesIO()
      resized_image.save(image_io, format='JPEG', quality=85)
      image_io.seek(0)
      image_file = InMemoryUploadedFile(
        image_io,
        None,
        image.name,
        'image/jpeg',
        image_io.getbuffer().nbytes, None
      )

    item_id = self.kwargs.get('item_id')
    with transaction.atomic():
      review = serializer.save(user=self.request.user, image=image_file, item_id=item_id)

      try:
        UserReview.objects.create(user=self.request.user, review=review)
      except Exception as e:
        raise ValidationError(f"Error creating UserReview: {str(e)}")


#新規投稿、編集、削除
class ReviewViewSet(viewsets.ModelViewSet):
  queryset = models.Review.objects.all()
  serializer_class = serializers.ReviewSerializer
  authentication_classes = (JWTAuthentication,)

  def perform_update(self, serializer):
    review = serializer.instance
    old_image = review.image
    new_image = self.request.FILES.get('image')

    if new_image:
      # 新しい画像が提供された場合
      if old_image:
        # 古い画像をS3から削除
        image_path = 'static/' + old_image.name
        delete_image_from_s3(image_path)
      with Image.open(new_image) as img:
        resized_image = resize_image(img)
      image_io = io.BytesIO()
      resized_image.save(image_io, format='JPEG', quality=85)
      image_io.seek(0)
      image_file = InMemoryUploadedFile(
        image_io,
        None,
        new_image.name,
        'image/jpeg',
        image_io.getbuffer().nbytes, None
      )
      serializer.validated_data['image'] = image_file
    elif 'image' in serializer.validated_data and not new_image:
      serializer.validated_data['image'] = None
      # 投稿の画像が設定されておらず、既存の画像がある場合、画像を削除
      if old_image:
        image_path = 'static/' + old_image.name
        delete_image_from_s3(image_path)
      serializer.save()
    else:
      serializer.save()

    # レビューの編集内容を保存
    if not review.is_edited:
      serializer.save(is_edited=True)
    else:
      serializer.save()

  def perform_destroy(self, instance):
    # レビューに関連する画像があれば、それをS3から削除
    if instance.image:
      image_path = 'static/' + instance.image.name
      delete_image_from_s3(image_path)

    # データベースからレビューを削除
    with transaction.atomic():
      super().perform_destroy(instance)
      

class GetFavoriteReviewCountView(generics.RetrieveAPIView):
  queryset = models.Favorite.objects.all()
  serializer_class = serializers.FavoriteCountSerializer
  permission_classes = (AllowAny,)
  authentication_classes = ()

  def get_object(self):
    review_id = self.kwargs['review_id']
    review = models.Review.objects.get(id=review_id)
    count = models.Favorite.objects.filter(review=review).count()
    return {'favorites_count': count}


#ログインユーザーのお気に入りをしたレビュー一覧
class GetFavoriteListView(generics.ListAPIView):
  serializer_class = serializers.ReviewSerializer
  authentication_classes = (JWTAuthentication,)

  def get_queryset(self):
    user = self.request.user
    favorite_review_ids = models.Favorite.objects.filter(user=user).values_list('review_id', flat=True)
    return models.Review.objects.filter(id__in=favorite_review_ids).order_by('-created_at')

#reviewIdを受け取り、それと一致するレビューのいいねの数を返す
class GetFavoriteReviewCountView(generics.RetrieveAPIView):
  serializer_class = serializers.FavoriteCountSerializer
  permission_classes = (AllowAny,)
  authentication_classes = ()

  def get_object(self):
    review_id = self.kwargs['review_id']
    try:
      review = models.Review.objects.get(id=review_id)
    except models.Review.DoesNotExist:
      raise NotFound('Review does not exist.')
    count = models.Favorite.objects.filter(review=review).count()
    return {'favorites_count': count}

#review_idとuser_idを受け取り、レビューにいいねをしているかしていないかを返す
class GetFavoriteReviewView(generics.RetrieveAPIView):
  serializer_class = serializers.FavoriteSerializer
  permission_classes = (IsAuthenticated,)

  #Favoriteモデルからユーザーがログインユーザー、取得したreviewidのオブジェクトを持ってくる
  def get_queryset(self):
    review_id = self.kwargs['review_id']
    return models.Favorite.objects.filter(user=self.request.user, review_id=review_id)
  
  def get(self, *args, **kwargs):
    favorite = self.get_queryset().exists()
    if favorite:
      return Response({'isFavorite': True})
    else:
      return Response({'isFavorite': False})
      

#いいね登録削除機能
class FavoriteViewSet(viewsets.ViewSet):
  serializer_class = serializers.FavoriteSerializer
  authentication_classes = (JWTAuthentication,)

  def create(self, request, review_id=None):
    review = get_object_or_404(models.Review, pk=review_id)
    models.Favorite.objects.create(user=request.user, review=review)
    review.favorites_count = models.Favorite.objects.filter(review=review).count()
    review.save()
    return Response({'status': 'favorite set'}, status=status.HTTP_201_CREATED)

  def destroy(self, request, review_id=None):
    review = get_object_or_404(models.Review, pk=review_id)
    favorite = get_object_or_404(models.Favorite, user=request.user, review=review)
    favorite.delete()
    review.favorites_count = models.Favorite.objects.filter(review=review).count()
    review.save()
    return Response({'status': 'favorite removed'}, status=status.HTTP_204_NO_CONTENT)
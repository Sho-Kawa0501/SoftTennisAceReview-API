from rest_framework import response
from django.contrib.auth import get_user_model
from rest_framework import permissions,status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from account import serializers
from django.conf import settings
import jwt
import logging
from rest_framework.exceptions import ValidationError,APIException,NotFound,PermissionDenied
from rest_framework_simplejwt.exceptions import TokenError,InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt import views as jwt_views,exceptions as jwt_exp
from PIL import Image
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.parsers import MultiPartParser, FormParser
from reviewsite.utils.image import resize_image,delete_image_from_s3
from django.db import transaction
from review.models import UserReview
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.generics import RetrieveAPIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer


logger = logging.getLogger(__name__)
User = get_user_model()


class RegisterView(APIView):
  permission_classes = (permissions.AllowAny, )
  authentication_classes = ()

  def post(self, request):
    data = request.data
    email = data.get('email', '').lower()
    password = data.get('password', '')

    if not email or not password:
      raise ValidationError('メールアドレスとパスワードは必須です。')

    if User.objects.filter(email=email).exists():
      # 既に存在するメールアドレスである場合
      return Response(
        {"detail": "既に登録されているメールアドレスです。"},
        status=status.HTTP_400_BAD_REQUEST
      )

    try:
      User.objects.create_user(email=email, password=password)
      return Response(status=status.HTTP_201_CREATED)
    except Exception as e:
      raise e.APIException('アカウント登録時に問題が発生しました。')
      
#ログイン
class MyTokenObtainPairView(jwt_views.TokenObtainPairView):
  serializer_class = serializers.MyTokenObtainPairSerializer
  permission_classes = (permissions.AllowAny, )
  authentication_classes = ()

  def post(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    access_token = serializer.validated_data["access"]
    refresh_token = serializer.validated_data["refresh"]

    try:
      return Response({
        "access_token": access_token,
        "refresh_token": refresh_token,
      }, status=status.HTTP_200_OK)
   
    except Exception as e:
      raise e.APIException("アクセストークン取得に失敗しました。")
    
class CheckAuthView(RetrieveAPIView):
  serializer_class = serializers.UserSerializer

  def get_object(self):
    return self.request.user

class RefreshTokenView(APIView):
  serializer_class = TokenRefreshSerializer
  #↓ 要修正
  def post(self, request, *args, **kwargs):
    serializer = self.serializer_class(data=request.data)
    if serializer.is_valid():
      try:
        refresh = RefreshToken(serializer.validated_data['refresh'])
        new_access_token = str(refresh.access_token)
        return Response({
          'access_token': new_access_token,
        }, status=status.HTTP_200_OK)

      except TokenError as e:
        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    else:
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(ModelViewSet):
  queryset = User.objects.all()
  serializer_class = serializers.UserSerializer
  authentication_classes = (JWTAuthentication,)

  def perform_update(self, serializer):
    login_user = serializer.instance
    old_image = login_user.image
    default_image_path = 'default/default.png'

    new_image = self.request.FILES.get('image', None)

    if new_image and new_image != '':
      # 新しい画像が提供された場合
      if old_image and old_image.name != default_image_path:
        # 元々設定してある画像がデフォルト画像でない場合、S3から削除
        image_path = 'static/' + old_image.name
        delete_image_from_s3(image_path)

      with Image.open(new_image) as img:
        # resize_imageは適切なリサイズ処理を行う関数
        resized_image = resize_image(img)
      image_io = io.BytesIO()
      resized_image.save(image_io, format='JPEG', quality=85)
      image_io.seek(0)
      image_file = InMemoryUploadedFile(
        image_io, None, new_image.name,
        'image/jpeg', image_io.getbuffer().nbytes, None
      )
      serializer.validated_data['image'] = image_file
    else:
      # 画像がリセットされた場合の処理
      if old_image and old_image.name != default_image_path:
        # 既存の画像がデフォルト画像でない場合、S3から削除
        image_path = 'static/' + old_image.name
        delete_image_from_s3(image_path)

      serializer.validated_data['image'] = default_image_path

    serializer.save()

class LogoutView(APIView):
  permission_classes = (AllowAny,)

  def post(self, request, *args, **kwargs):
    try:
      refresh_token = request.data.get('refresh_token')
      token = RefreshToken(refresh_token)
      token.blacklist()  # リフレッシュトークンをブラックリストに追加
      return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
    except (InvalidToken, TokenError) as e:
      return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
  # def post(self, request, *args, **kwargs):
  #   res = Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
  #   return res


class DeleteUserView(APIView):
  authentication_classes = (JWTAuthentication,)

  def delete(self, request):
    user = request.user
    if user is None:
      raise NotAuthenticated("ユーザーが認証されていません。")

    try:
      with transaction.atomic():
        if user.image and not user.image.name.endswith('default/default.png'):
          user_image_path = 'static/' + user.image.name
          delete_image_from_s3(user_image_path)

        user_reviews = UserReview.objects.filter(user=user)
        for user_review in user_reviews:
          if user_review.review.image:
            if user_review.review.image and not user_review.review.image.name.endswith('default/default.png'):
              review_image_path = 'static/' + user_review.review.image.name
              delete_image_from_s3(review_image_path)
        user.delete()
      return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
      raise e.APIException(f"ユーザーの削除に問題が発生しました。: {str(e)}")
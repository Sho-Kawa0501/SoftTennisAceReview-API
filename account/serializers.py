from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
  def validate(self, attrs):
    authenticate_kwargs = {
      'email': attrs.get('email'),
      'password': attrs.get('password'),
    }
    user = authenticate(**authenticate_kwargs)
    
    if not user:
      raise AuthenticationFailed('メールアドレスまたはパスワードが間違っています。')
    
    # email,passwordのバリデーションが通ったら、
    # 継承元のTokenObtainPairSerializerのvalidate関数により、refresh,accessトークンが生成される
    data = super().validate(attrs)
    return data

class TokenRefreshSerializer(serializers.Serializer):
  refresh = serializers.CharField()

  def validate(self, attrs):
    refresh = attrs.get('refresh')
    try:
      RefreshToken(refresh)
    except TokenError as e:
      raise serializers.ValidationError(str(e))
    return attrs

class UserSerializer(serializers.ModelSerializer):
  image = serializers.ImageField(default='default/default.png')
  
  class Meta:
    model = User
    fields = ('id','name','email','image','favorite_reviews')


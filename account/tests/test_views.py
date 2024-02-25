from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
import io
from PIL import Image
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken


User = get_user_model()

class RegisterViewTests(APITestCase):
  def test_register_user_successfully(self):
    """
    新規ユーザー登録が成功することを確認します。
    """
    url = reverse('accounts:register')
    data = {
      'email': 'newuser@example.com',
      'password': 'newpassword123'
    }
    response = self.client.post(url, data, format='json')
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

  def test_user_exists(self):
    """
    既存のメールアドレスで新規ユーザー登録を試みた場合、エラーが返されることを確認します。
    """
    User.objects.create_user(email='existing@example.com', password='password123')
    url = reverse('accounts:register')
    data = {
      'email': 'existing@example.com',
      'password': 'password123'
    }
    response = self.client.post(url, data, format='json')
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

  def test_create_user_with_no_password(self):
    """
    パスワードを指定せずに新規ユーザー登録を試みた場合、エラーが返されることを確認します。
    """
    url = reverse('accounts:register')
    data = {
      'email': 'userwithoutpass@example.com',
      'password': ''
    }
    response = self.client.post(url, data, format='json')
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class MyTokenObtainPairViewTests(APITestCase):
  @classmethod
  def setUpTestData(cls):
    cls.user = User.objects.create_user(email='test@example.com', password='testpassword')
    cls.url = reverse('accounts:login')

  def test_obtain_token_pair_success(self):
    """
    正しい資格情報でトークンペアを取得できることを確認します。
    """
    data = {
      'email': 'test@example.com',
      'password': 'testpassword'
    }
    response = self.client.post(self.url, data, format='json')
    self.assertIn('access_token', response.data)  # 'access' を 'access_token' に変更
    self.assertIn('refresh_token', response.data)
 

  def test_obtain_token_with_invalid_credentials(self):
    """
    無効な資格情報でトークンペアを取得しようとした場合、エラーが返されることを確認します。
    """
    data = {
      'email': 'test@example.com',
      'password': 'wrongpassword'
    }
    response = self.client.post(self.url, data, format='json')
    self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST])


class CheckAuthViewTests(APITestCase):
  def setUp(self):
    self.user = User.objects.create_user(email='test@example.com', password='testpassword')
    self.url = reverse('accounts:check-auth')

  def test_get_user_info(self):
    """認証されたユーザーが自身の情報を取得できるかテスト"""
    # ユーザーを認証
    self.client.force_authenticate(user=self.user)
    
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data['email'], self.user.email)


class UserViewSetTest(APITestCase):
  def setUp(self):
    # テスト用ユーザーの作成
    self.user = User.objects.create_user(email='test@example.com', password='testpassword')
    self.url = reverse('accounts:user-detail', kwargs={'pk': self.user.pk})
    self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(AccessToken.for_user(self.user)))

  def test_update_user_without_image(self):
    # 画像なしでユーザー情報を更新
    data = {'name': 'New Name', 'email': 'newemail@example.com'}
    response = self.client.patch(self.url, data)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.user.refresh_from_db()
    self.assertEqual(self.user.email, 'newemail@example.com')

  def test_update_user_with_new_image(self):
    # 新しい画像を含むユーザー情報を更新
    new_image = self.generate_image_file()
    data = {'name': 'New Name', 'email': 'newemail@example.com', 'image': new_image}
    response = self.client.patch(self.url, data, format='multipart')
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertNotEqual(response.data['image'], 'default/default.png')

  def test_reset_user_image_to_default(self):
    # ユーザー画像をデフォルトにリセットするリクエストを送信
    response = self.client.patch(self.url, {'image': ''}, format='multipart')
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.user.refresh_from_db()
    self.assertEqual(self.user.image, 'default/default.png')

  def generate_image_file(self):
    # ダミー画像ファイルの生成
    file = io.BytesIO()
    image = Image.new('RGB', (100, 100), color='red')
    image.save(file, 'png')
    file.name = 'test.png'
    file.seek(0)
    return file

class LogoutViewTest(APITestCase):
  def setUp(self):
    self.user = User.objects.create_user(email='logouttest@example.com', password='testpassword')
    self.url = reverse('accounts:logout')  # accountsはapp_name、logoutはurlpatternsでのname

  def test_logout_success(self):
    # ユーザーに対するリフレッシュトークンを取得N
    refresh = RefreshToken.for_user(self.user)
    response = self.client.post(self.url, {'refresh_token': str(refresh)})
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(BlacklistedToken.objects.count(), 1)

  def test_logout_invalid_token(self):
    response = self.client.post(self.url, {'refresh_token': 'invalid_token'})
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class DeleteUserViewTest(APITestCase):
  def setUp(self):
    self.user = User.objects.create_user(email='deletetest@example.com', password='testpassword')
    self.url = reverse('accounts:user-delete')  # accountsはapp_name、user-deleteはurlpatternsでのname
    self.client.force_authenticate(user=self.user)

  def test_delete_user(self):
    response = self.client.delete(self.url)
    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    self.assertEqual(User.objects.filter(email='deletetest@example.com').exists(), False)

  def test_delete_user_not_authenticated(self):
    self.client.force_authenticate(user=None)  # 認証を解除
    response = self.client.delete(self.url)
    self.assertNotEqual(response.status_code, status.HTTP_204_NO_CONTENT)


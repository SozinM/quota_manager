from django.test import TestCase
from rest_framework.test import APIClient, force_authenticate
from api.models import Quota, QuotaUser, Resource


class AdminTests(TestCase):
    def setUp(self) -> None:
        self.settings()
        pass


class UserTests(TestCase):
    def setUp(self) -> None:

        self.user = QuotaUser.objects.create_user(username="test", email="test@test.com", password="password")
        Quota.objects.create(id=self.user)
        self.user2 = QuotaUser.objects.create_user(username="test2", email="test2@test.com", password="password")
        Quota.objects.create(id=self.user2)
        self.admin = QuotaUser.objects.create_superuser(username="admin", email="admin@admin.com", password="password")
        Quota.objects.create(id=self.admin)

    def test_user_creation(self):
        client = APIClient()
        request = client.post('/register/',
                                   {'username': "test3", 'email': "test3@test.com", 'password': "password"},
                                   format='json')
        self.assertTrue(request.status_code == 201)
        user = QuotaUser.objects.filter(username='test3')
        self.assertTrue(user)
        self.assertTrue(Quota.objects.filter(id=user.last()))

    def test_user_login(self):
        client = APIClient()
        request = client.post('/login/',
                              {'email': "test@test.com", 'password': "password"},
                              format='json')
        self.assertTrue(request.status_code == 200)

    def test_resource_basics(self):
        client = APIClient()
        client.force_authenticate(self.user)
        request = client.post('/resources/', {'resource': "test_1_resource"}, format='json')
        self.assertTrue(request.status_code == 201)
        request = client.get('/resources/', format='json')
        self.assertTrue(request.data[0]['resource'] == 'test_1_resource')
        request = client.put('/resources/1/', {'resource': "test_2_resource"}, format='json')
        self.assertTrue(request.status_code == 200)
        request = client.delete('/resources/1/', format='json')
        self.assertTrue(request.status_code == 204)
        self.assertFalse(Resource.objects.all())

    def test_resource_create(self):
        client = APIClient()
        client.force_authenticate(self.user)
        request = client.post('/resources/',
                              {'resource': "test_1_resource"},
                              format='json')
        self.assertTrue(request.status_code == 201)


# Create your tests here.

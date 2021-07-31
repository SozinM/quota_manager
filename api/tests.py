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
        self.quoted_user = QuotaUser.objects.create_user(username="quoted_user", email="quoted_user@test.com",
                                                         password="password")
        Quota.objects.create(id=self.quoted_user, quota=1)
        self.restricted_user = QuotaUser.objects.create_user(username="restricted_user",
                                                             email="restricted_user@test.com", password="password")
        Quota.objects.create(id=self.restricted_user, allowed=False)
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
        self.assertTrue(Resource.objects.filter(resource='test_1_resource').count() == 1)

        request = client.get('/resources/', format='json')
        self.assertTrue(request.data[0]['resource'] == 'test_1_resource')

        request = client.put('/resources/1/', {'resource': "test_2_resource"}, format='json')
        self.assertTrue(request.status_code == 200)
        self.assertTrue(Resource.objects.filter(resource='test_2_resource').count() == 1)

        request = client.patch('/resources/1/', {'resource': "test_3_resource"}, format='json')
        self.assertTrue(request.status_code == 200)
        self.assertTrue(Resource.objects.filter(resource='test_3_resource').count() == 1)

        request = client.delete('/resources/1/', format='json')
        self.assertTrue(request.status_code == 204)
        self.assertFalse(Resource.objects.all())

    def test_resource_quoted(self):
        client = APIClient()
        client.force_authenticate(self.quoted_user)

        request = client.post('/resources/', {'resource': "test_1_resource"}, format='json')
        self.assertTrue(request.status_code == 201)
        self.assertTrue(Resource.objects.filter(resource='test_1_resource').count() == 1)

        # test that user prohibited to create resources that exceeds quota
        request = client.post('/resources/', {'resource': "test_2_resource"}, format='json')
        self.assertTrue(request.status_code == 400)
        self.assertTrue(Resource.objects.all().count() == 1)

        # test that functionality which should not be affected by quota still works
        request = client.get('/resources/', format='json')
        self.assertTrue(request.data[0]['resource'] == 'test_1_resource')

        request = client.put('/resources/1/', {'resource': "test_2_resource"}, format='json')
        self.assertTrue(request.status_code == 200)
        self.assertTrue(Resource.objects.filter(resource='test_2_resource').count() == 1)

        request = client.patch('/resources/1/', {'resource': "test_3_resource"}, format='json')
        self.assertTrue(request.status_code == 200)
        self.assertTrue(Resource.objects.filter(resource='test_3_resource').count() == 1)

        request = client.delete('/resources/1/', format='json')
        self.assertTrue(request.status_code == 204)
        self.assertFalse(Resource.objects.all())

    def test_resource_restricted(self):
        client = APIClient()
        client.force_authenticate(self.restricted_user)

        # test that user prohibited to create resources that exceeds quota
        request = client.post('/resources/', {'resource': "test_1_resource"}, format='json')
        self.assertTrue(request.status_code == 400)
        self.assertTrue(Resource.objects.all().count() == 0)

        # object testing other functionality
        Resource.objects.create(resource='test_1_resource', user_id=self.restricted_user)

        # test that functionality which should not be affected by quota still works
        request = client.get('/resources/', format='json')
        self.assertTrue(request.data[0]['resource'] == 'test_1_resource')

        request = client.put('/resources/1/', {'resource': "test_2_resource"}, format='json')
        self.assertTrue(request.status_code == 200)
        self.assertTrue(Resource.objects.filter(resource='test_2_resource').count() == 1)

        request = client.patch('/resources/1/', {'resource': "test_3_resource"}, format='json')
        self.assertTrue(request.status_code == 200)
        self.assertTrue(Resource.objects.filter(resource='test_3_resource').count() == 1)

        request = client.delete('/resources/1/', format='json')
        self.assertTrue(request.status_code == 204)
        self.assertFalse(Resource.objects.all())

    def test_user_retrieve_delete(self):
        client = APIClient()
        client.force_authenticate(self.user)

        request = client.get(f'/users/{self.user.id}/', format='json')
        self.assertTrue(request.status_code == 200)

        request = client.delete(f'/users/{self.user.id}/', format='json')
        self.assertTrue(request.status_code == 204)
        self.assertFalse(QuotaUser.objects.filter(id=self.user.id))




# Create your tests here.

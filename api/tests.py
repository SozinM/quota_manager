from django.test import TestCase
from rest_framework.test import APIClient
from api.models import Quota, QuotaUser, Resource


class AdminTests(TestCase):
    def setUp(self) -> None:
        self.user = QuotaUser.objects.create_user(username="test", email="test@test.com", password="password")
        Quota.objects.create(id=self.user)

        self.admin = QuotaUser.objects.create_superuser(username="admin", email="admin@admin.com", password="password")
        Quota.objects.create(id=self.admin)

    def test_admin_set_quota(self):
        client = APIClient()
        client.force_authenticate(self.admin)

        request = client.get('/admin/quotas/', format='json')
        self.assertTrue(request.status_code == 200)
        self.assertTrue(len(request.data) == 2)

        request = client.put(f'/admin/quotas/{self.user.id}/', {'id': self.user.id, 'quota': f'{pow(2,63) -1}', 'allowed': 'true'},
                             format='json')
        quota = Quota.objects.filter(id=self.user).last()
        self.assertTrue(request.status_code == 200)
        self.assertTrue(request.data == {'id': self.user.id, 'quota': pow(2,63) -1, 'allowed': True})
        self.assertTrue(quota.quota == pow(2,63) -1)
        self.assertTrue(quota.allowed)

        request = client.patch(f'/admin/quotas/{self.user.id}/', {'quota': '1', 'allowed': 'false'},
                               format='json')
        quota = Quota.objects.filter(id=self.user).last()
        self.assertTrue(request.status_code == 200)
        self.assertTrue(request.data == {'id': self.user.id, 'quota': 1, 'allowed': False})
        self.assertTrue(quota.quota == 1)
        self.assertFalse(quota.allowed)

        request = client.patch(f'/admin/quotas/{self.user.id}/', {'quota': '-1', 'allowed': 'false'},
                               format='json')
        quota = Quota.objects.filter(id=self.user).last()
        self.assertTrue(request.status_code == 400)
        self.assertTrue(request.data['quota'][0].code == 'min_value')
        # quota is unchanged
        self.assertTrue(quota.quota == 1)
        self.assertFalse(quota.allowed)

        request = client.patch(f'/admin/quotas/{self.user.id}/', {'quota': f'{pow(2,63)}', 'allowed': 'false'},
                               format='json')
        quota = Quota.objects.filter(id=self.user).last()
        self.assertTrue(request.status_code == 400)
        self.assertTrue(request.data['quota'][0].code == 'max_value')
        # quota is unchanged
        self.assertTrue(quota.quota == 1)
        self.assertFalse(quota.allowed)

        request = client.patch(f'/admin/quotas/{self.user.id}/', {'quota': '1', 'allowed': 'not_bool'},
                               format='json')
        quota = Quota.objects.filter(id=self.user).last()
        self.assertTrue(request.status_code == 400)
        self.assertTrue(request.data['allowed'][0].code == 'invalid')
        # quota is unchanged
        self.assertTrue(quota.quota == 1)
        self.assertFalse(quota.allowed)

        # self.assertTrue(request.status_code == 200)

    def test_admin_resources_basic(self):
        client = APIClient()
        client.force_authenticate(self.admin)

        user_res = Resource.objects.create(resource='1', user_id=self.user)
        admin_res = Resource.objects.create(resource='2', user_id=self.admin)

        request = client.post('/admin/resources/', {'resource': '3', 'user_id': self.user.id}, format='json')
        self.assertTrue(request.status_code == 201)
        self.assertTrue(Resource.objects.filter(resource='3'))

        request = client.get('/admin/resources/', format='json')
        self.assertTrue(request.status_code == 200)
        self.assertTrue(len(request.data) == Resource.objects.all().count())

        request = client.put(f'/admin/resources/{user_res.id}/', {'id': user_res.id, 'resource': 'Putted resource',
                                                                  'user_id': self.user.id}, format='json')
        self.assertTrue(request.status_code == 200)
        self.assertTrue(Resource.objects.filter(id=user_res.id).last().resource == "Putted resource")

        request = client.patch(f'/admin/resources/{user_res.id}/', {'resource': 'Some res'}, format='json')
        self.assertTrue(request.status_code == 200)
        self.assertTrue(Resource.objects.filter(id=user_res.id).last().resource == "Some res")

        request = client.delete(f'/admin/resources/{user_res.id}/', format='json')
        self.assertTrue(request.status_code == 204)
        self.assertFalse(Resource.objects.filter(id=user_res.id))

    def test_admin_user_basic(self):
        client = APIClient()
        client.force_authenticate(self.admin)

        request = client.get('/admin/users/', format='json')
        self.assertTrue(request.status_code == 200)
        self.assertTrue(len(request.data) == QuotaUser.objects.all().count())

        request = client.post('/admin/users/', {'username': "test3", 'email': "test3@test.com", 'password': "password"},
                              format='json')
        self.assertTrue(request.status_code == 201)
        test3 = QuotaUser.objects.filter(username='test3').last()
        self.assertTrue(test3)

        request = client.delete(f'/admin/users/{test3.id}/', format='json')
        self.assertTrue(request.status_code == 204)
        self.assertFalse(QuotaUser.objects.filter(username='test3'))




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
        users_creds = ({'email': "test@test.com", 'password': "password"},
                       {'email': "admin@admin.com", 'password': "password"})
        for credentials in users_creds:
            with self.subTest(f"Test auth for {credentials}"):
                client = APIClient()
                request = client.post('/login/',
                                      credentials,
                                      format='json')
                self.assertTrue(request.status_code == 200)

    def test_resource_basics(self):
        users = (self.admin, self.user)

        for user in users:
            with self.subTest(f"Test resources usage for user {user}"):
                client = APIClient()
                client.force_authenticate(user)

                request = client.post('/resources/', {'resource': "test_1_resource"}, format='json')
                self.assertTrue(request.status_code == 201)
                resource = Resource.objects.filter(resource='test_1_resource').last()
                self.assertTrue(resource)

                request = client.get('/resources/', format='json')
                self.assertTrue(request.data[0]['resource'] == 'test_1_resource')

                request = client.get(f'/resources/{resource.id}/', format='json')
                self.assertTrue(request.data['resource'] == 'test_1_resource')

                request = client.put(f'/resources/{resource.id}/', {'resource': "test_2_resource"}, format='json')
                self.assertTrue(request.status_code == 200)
                self.assertTrue(Resource.objects.filter(resource='test_2_resource'))

                request = client.patch(f'/resources/{resource.id}/', {'resource': "test_3_resource"}, format='json')
                self.assertTrue(request.status_code == 200)
                self.assertTrue(Resource.objects.filter(resource='test_3_resource'))

                request = client.delete(f'/resources/{resource.id}/', format='json')
                self.assertTrue(request.status_code == 204)
                self.assertFalse(Resource.objects.all())

    def test_resource_quoted(self):
        client = APIClient()
        client.force_authenticate(self.quoted_user)

        request = client.post('/resources/', {'resource': "test_1_resource"}, format='json')
        self.assertTrue(request.status_code == 201)
        self.assertTrue(Resource.objects.filter(resource='test_1_resource'))

        # test that user prohibited to create resources that exceeds quota
        request = client.post('/resources/', {'resource': "test_2_resource"}, format='json')
        self.assertTrue(request.status_code == 400)
        self.assertTrue(Resource.objects.all().count() == 1)

        # test that functionality which should not be affected by quota still works
        request = client.get('/resources/', format='json')
        self.assertTrue(request.data[0]['resource'] == 'test_1_resource')

        request = client.put('/resources/1/', {'resource': "test_2_resource"}, format='json')
        self.assertTrue(request.status_code == 200)
        self.assertTrue(Resource.objects.filter(resource='test_2_resource'))

        request = client.patch('/resources/1/', {'resource': "test_3_resource"}, format='json')
        self.assertTrue(request.status_code == 200)
        self.assertTrue(Resource.objects.filter(resource='test_3_resource'))

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
        self.assertTrue(Resource.objects.filter(resource='test_2_resource'))

        request = client.patch('/resources/1/', {'resource': "test_3_resource"}, format='json')
        self.assertTrue(request.status_code == 200)
        self.assertTrue(Resource.objects.filter(resource='test_3_resource'))

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

    def test_cross_user_resources(self):
        client = APIClient()
        client2 = APIClient()
        client.force_authenticate(self.user)
        client2.force_authenticate(self.quoted_user)

        request = client.post('/resources/', {'resource': "test_1_resource"}, format='json')
        self.assertTrue(request.status_code == 201)
        self.assertTrue(Resource.objects.filter(resource='test_1_resource'))

        request = client2.get('/resources/1/', format='json')
        self.assertTrue(request.status_code == 404)

        request = client2.get('/resources/', format='json')
        self.assertFalse(request.data)

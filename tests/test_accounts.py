from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User

test_email = 'kblackwelder08@gmail.com'
password = 'testpassword'

# Registration payload
registration_payload = {
    'email': test_email,
    'password': password,
    'first_name': 'Keith',
    'last_name': 'Blackwelder',
}

# Login Payload
login_payload = {
    'email': test_email,
    'password': password,
}


class RegisterViewTest(TestCase):
    """ Test module for RegisterView """

    def setup(self):
        self.client = APIClient()

    def test_register_valid_payload(self):
        response = self.client.post(
            reverse('register'),
            data=registration_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_invalid_payload(self):
        # Modify the registration payload to not include the last name
        registration_payload = {
            'email': test_email,
            'password': 'testpassword',
            'first_name': 'Kevin',
        }
        response = self.client.post(
            reverse('register'),
            data=registration_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginViewTest(TestCase):
    """ Test module for LoginView """

    def setUp(self):
        self.client = APIClient()
        # Create a user
        self.user = User.objects.create_user(**registration_payload)

    def test_login_valid_payload(self):
        response = self.client.post(
            reverse('token_obtain_pair'),
            data=login_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_invalid_payload(self):
        # Modify the login payload to use an invalid password
        login_payload = {
            'email': test_email,
            'password': 'invalidpassword',
        }
        response = self.client.post(
            reverse('token_obtain_pair'),
            data=login_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutTestView(TestCase):
    """ Test module for LogoutView """

    def setUp(self):
        self.client = APIClient()
        # Create a user
        self.user = User.objects.create_user(**registration_payload)

        # Get the token
        response = self.client.post(
            reverse('token_obtain_pair'),
            data=login_payload,
            format='json'
        )
        # Set the token
        self.token = response.data['access']
        # Store the refresh token
        self.refresh_token = response.data['refresh']

    def test_logout_valid_payload(self):
        # Add the token to the header
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        #  Create the payload
        payload = {
            'refresh_token': self.refresh_token
        }
        response = self.client.post(
            reverse('logout'),
            data=payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_invalid_payload(self):
        """ Test logout with invalid payload """
        # Add the token to the header
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        #  Create the payload
        payload = {
            'invalid_token': self.refresh_token
        }
        response = self.client.post(
            reverse('logout'),
            data=payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_no_token(self):
        """ Test logout without token """
        #  Create the payload
        payload = {
            'refresh_token': self.refresh_token
        }
        response = self.client.post(
            reverse('logout'),
            data=payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestUsersCRUD(APITestCase):
    """ Test module for User CRUD operations """

    token = None

    def setUp(self):
        self.client = APIClient()
        # Create a superuser
        admin_payload = {
            'email': 'anotheruser@gmail.com',
            'password': 'testpassword',
            'first_name': 'Admin',
            'last_name': 'User',
        }

        self.user = User.objects.create_superuser(**admin_payload)

        # Get the token
        # Make sure to update the email in the login payload
        anotheruser_login_payload = {
            'email': 'anotheruser@gmail.com',
            'password': 'testpassword',
        }
        response = self.client.post(
            reverse('token_obtain_pair'),
            data=anotheruser_login_payload,
            format='json'
        )
        # Set the token
        self.token = response.data['access']

    def teardown(self):
        self.client.logout()
        # Delete the user
        self.user.delete()

    def test_create_admin_user(self):
        """ Test create admin user """
        # Add the token to the header
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        # Create the payload
        payload = {
            'email': 'admin@codingblindtech.com',
            'password': 'testpassword',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
        }
        response = self.client.post(
            reverse('user-create'),
            data=payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_as_not_admin(self):
        """ Try to create user as non admin """
        self.user = User.objects.create_user(**registration_payload)
        # Get the token
        response = self.client.post(
            reverse('token_obtain_pair'),
            data=login_payload,
            format='json'
        )
        # Set the token
        token = response.data['access']
        # Add the token to the header
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        # Create the payload
        payload = {
            'email': 'normaluser@codingblindtech.com',
            'password': 'testpassword',
            'first_name': 'Normal',
            'last_name': 'User',
        }
        response = self.client.post(
            reverse('user-create'),
            data=payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_normal_user(self):
        """ Test create normal user """
        # Add the token to the header
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        # Create the payload
        payload = {
            'email': 'normaluser@gmail.com',
            'password': 'testpassword',
            'first_name': 'Normal',
            'last_name': 'User',
        }
        response = self.client.post(
            reverse('user-create'),
            data=payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_all_users(self):
        """ Test to get all users """
        # Add the token to the header
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        # Create the payload
        # Retreive all users
        response = self.client.get(
            reverse('user-list'),
            format='json'
        )
        # print the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_user(self):
        """ Test to get single user """
        # Add the token to the header
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(
            reverse('user-detail', kwargs={'pk': self.user.pk}),
            format='json'
        )
        # Print the data
        print(response.data)
        # Print the length of the list returned by the API
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user(self):
        """ Test to update user """
        # Add the token to the header
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        # Create the payload
        payload = {
            'email': 'updatedemail@gmail.com',
            'password': 'testpassword',
            'first_name': 'Updated',
            'last_name': 'User',
        }
        response = self.client.put(
            reverse('user-detail', kwargs={'pk': self.user.pk}),
            data=payload,
            format='json'
        )
        # Print the data
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user(self):
        """ Test to delete a user   """
        # Add the token to the header
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.delete(
            reverse('user-detail', kwargs={'pk': self.user.pk}),
            format='json',
            follow=True
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

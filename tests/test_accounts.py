from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from rest_framework import status
from accounts.models import User

# Test email and admin email
test_email = 'kblackwelder08@gmail.com'
admin_email = 'keith.blackwelder@codingblindtech.com'

# Password for both test and admin users
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


class UserViewTest(TestCase):
    """ Test user read, create, update and delete """

    def setup(self):
        self.client = APIClient()
        # Create a user
        self.user = User.objects.create_user(**registration_payload)
        # Create admin user for testing
        self.admin_user = User.objects.create_superuser(
            email=admin_email,
            password=password,
            first_name='Keith',
            last_name='Blackwelder',
        )

    
    def test_user_read(self):
        """ Test user read """

        # Only admin users can read users
        login_payload = {
            'email': admin_email,
            'password': password,
        }
        # Get the token
        response = self.client.post(
            reverse('token_obtain_pair'),
            data=login_payload,
            format='json'
        )
        # Set the token
        self.token = response.data['access']
        # Add the token to the header
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        # Get the user
        response = self.client.get(
            reverse('user'),
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

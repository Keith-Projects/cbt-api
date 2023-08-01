from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from rest_framework import status
from accounts.models import User

# Registration payload
registration_payload= {
    'email': 'kblackwelder08@gmail.com',
    'password': 'testpassword',
    'first_name': 'Kevin',
    'last_name': 'Blackwelder',
}

# Login Payload
login_payload = {
    'email': 'kblackwelder08@gmail.com',
    'password': 'testpassword',
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
            'email': 'kblackwelder08@gmail.com',
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

class LogoutTestView(TestCase):

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

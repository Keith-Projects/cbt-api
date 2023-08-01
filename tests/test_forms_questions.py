from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

# import the Question model
from cbtforms.models import Question

# import the User model
from accounts.models import User

admin_email = 'kblackwelder08@gmail.com'
admin_password = 'adminpassword'

user_email = 'nolimits1120@gmail.com'
user_password = 'testpassword'


class TestQuestions(TestCase):
    """ Test module for QuestionsCreateView """

    def setUp(self):
        self.client = APIClient()
        # Create a super user
        super_user = {
            'email': admin_email,
            'password': admin_password,
            'first_name': 'Kevin',
            'last_name': 'Blackwelder',
        }
        self.super_user = User.objects.create_superuser(**super_user)
        # Create a user
        user = {
            'email': user_email,
            'password': user_password,
            'first_name': 'Keith',
            'last_name': 'Blackwelder',
        }
        self.user = User.objects.create_user(**user)

    def login(self, email, password):
        # Login the user
        response = self.client.post(
            reverse('token_obtain_pair'),
            data={
                'email': email,
                'password': password,
            },
            format='json'
        )
        # return the data
        return response.data

    def test_create_question_valid_payload(self):
        # Login the user and get the token
        token = self.login(user_email, user_password)['access']

        # Request create a question
        question_data = {
            'question_text': 'What is the capital of California?',
            'user': self.user.id,
        }
        # Add the token to the headers
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.post(
            reverse('question_create'),
            data=question_data,
            format='json',
        )
        # Assert the status
        self.assertEqual(response.status_code, 201)
        # Assert the return data
        self.assertEqual(
            response.data['question_text'], question_data['question_text'])
        # Assert that the user is the same
        self.assertEqual(response.data['user'], self.user.id)

    def test_create_question_invalid_payload(self):
        # login the user and get the token
        token = self.login(user_email, user_password)['access']

        # Request create a question
        question_data = {
            'question_text': 'What is the capital of California?',
        }
        # Add the token to the headers
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.post(
            reverse('question_create'),
            data=question_data,
            format='json',
        )
        # Assert the status

        self.assertEqual(response.status_code, 400)

    def test_create_question_unauthorized(self):
        # Request create a question
        question_data = {
            'question_text': 'What is the capital of California?',
        }
        response = self.client.post(
            reverse('question_create'),
            data=question_data,
            format='json',
        )
        # Assert the status
        self.assertEqual(response.status_code, 401)

    def test_get_question(self):
        # login as normal user and get the token
        token = self.login(user_email, user_password)['access']

        # Create a list of questions
        questions = [
            {
                'question_text': 'What is the capital of California?',
                'user': self.user.id,
            },
            {
                'question_text': 'What is the capital of Texas?',
                'user': self.user.id,
            },
            {
                'question_text': 'What is the capital of Florida?',
                'user': self.user.id,
            },
        ]
        # Create the questions
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        for question in questions:
            # using the client
            self.client.post(
                reverse('question_create'),
                data=question,
                format='json',
            )

        # Get the questions
        # Need to be admin
        token = self.login(admin_email, admin_password)['access']
        # Add the token to the headers
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.get(
            reverse('question_list'),
            format='json',
        )
        # Assert the status
        self.assertEqual(response.status_code, 200)
        # Assert the length of the response
        self.assertEqual(len(response.data), 3)

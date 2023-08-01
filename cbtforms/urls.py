from django.urls import path
from .views import (
    QuestionCreateView,
    QuestionListView,
)


urlpatterns = [
    path('question/create/', QuestionCreateView.as_view(), name='question_create'),
    path('question/list/', QuestionListView.as_view(), name='question_list'),
]

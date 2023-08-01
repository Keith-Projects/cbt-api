from django.db import models

# Model for question form
class Question(models.Model):
    question_text = models.CharField(max_length=10000)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created_at',)

from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()

class HealthRecord(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='record')
    unique_id = models.CharField(max_length=51)
    ehr = models.TextField(null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(self.user)
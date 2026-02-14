import secrets

from django.db import models


def generate_uid():
    return secrets.token_urlsafe(6)


class Valentine(models.Model):
    uid = models.CharField(max_length=12, unique=True, db_index=True, default=generate_uid)
    sender_name = models.CharField(max_length=50)
    recipient_name = models.CharField(max_length=50)
    acrostic_mode = models.CharField(max_length=10, default="default")
    custom_acrostic = models.JSONField(null=True, blank=True)
    poem_mode = models.CharField(max_length=10, default="default")
    custom_poem = models.TextField(null=True, blank=True)
    music_mode = models.CharField(max_length=10, default="default")
    youtube_id = models.CharField(max_length=20, null=True, blank=True)
    sender_ip = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender_name} -> {self.recipient_name} ({self.uid})"

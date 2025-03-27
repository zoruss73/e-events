from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
# Create your models here.

class Room(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user2")
    created_at = models.DateTimeField(default=now)
    
    class Meta:
        unique_together = ('user1', 'user2')
    
    def __str__(self):
        return f"Chat room: {self.user1.first_name} - {self.user2.first_name}"


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    message = models.TextField()
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"From {self.sender}: {self.message[:30]}"
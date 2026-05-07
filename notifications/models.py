from django.db import models
from reservations.models import Reservation

class Notification(models.Model):
    message = models.TextField()
    dateEnvoi = models.DateField(auto_now_add=True)

    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)

    def __str__(self):
        return self.message
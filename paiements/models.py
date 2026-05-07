from django.db import models
from reservations.models import Reservation

class Facture(models.Model):
    montant = models.FloatField()
    statut = models.CharField(max_length=50)

    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE)

    def __str__(self):
        return f"Facture {self.id}"
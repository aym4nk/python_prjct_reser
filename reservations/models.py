from django.db import models
from users.models import Client
from salles.models import Salle

class Reservation(models.Model):
    dateDebut = models.DateField()
    dateFin = models.DateField()
    statut = models.CharField(max_length=50)

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.client} - {self.salle}"
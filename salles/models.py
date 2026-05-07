from django.db import models


class Salle(models.Model):

    type = models.CharField(max_length=100)

    prix = models.FloatField()

    def __str__(self):
        return self.type


class Disponibilite(models.Model):

    date = models.DateField()

    estDisponible = models.BooleanField(default=True)

    salle = models.OneToOneField(
        Salle,
        on_delete=models.CASCADE,
        related_name='disponibilite'
    )

    def verifierDisponibilite(self):
        return self.estDisponible

    def __str__(self):
        return f"{self.salle} - {self.date}"
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from reservations.models import Reservation
from salles.models import Salle, Disponibilite
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.conf import settings
import os
from users.models import Client
from datetime import date
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont



# 🏠 Accueil
def acceuil(request):
    return render(request, 'base/acceuil.html')


# 🔐 Login
def login_view(request):

    if request.user.is_authenticated:
        return redirect('main')

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            if hasattr(user, 'profile') and user.profile.role == "admin":
                return redirect('admin_dashboard')

            return redirect('main')

        return render(request, 'base/login.html', {
            'error': 'Username ou mot de passe incorrect'
        })

    return render(request, 'base/login.html')


# 📝 Register
def register_view(request):

    if request.user.is_authenticated:
        return redirect('main')

    if request.method == "POST":

        username = request.POST.get('username')

        email = request.POST.get('email')

        password = request.POST.get('password')

        confirm = request.POST.get('confirm')

        if password != confirm:

            return render(request, 'base/register.html', {
                'error': 'Les mots de passe ne correspondent pas'
            })

        if User.objects.filter(username=username).exists():

            return render(request, 'base/register.html', {
                'error': 'Username déjà utilisé'
            })

        # 🔥 create django user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # 🔥 create client
        Client.objects.create(
            nom=username,
            prenom=username,
            email=email
        )

        login(request, user)

        return redirect('main')

    return render(request, 'base/register.html')


# 👤 Main
@login_required
def main(request):

    salles = Salle.objects.all()

    data = []

    today = date.today()

    for salle in salles:

        reserved = Reservation.objects.filter(
            salle=salle,
            statut__in=["En attente", "Confirmée"],
            dateDebut__lte=today,
            dateFin__gte=today
        ).exists()

        data.append({
            'salle': salle,
            'disponible': not reserved
        })

    return render(request, 'base/main.html', {
        'data': data
    })



# Dashboard admin
@login_required
def admin_dashboard(request):

    salles = Salle.objects.all()

    users = User.objects.all()

    reservations = Reservation.objects.all().order_by('-id')

    data = []

    today = date.today()

    for salle in salles:

        reserved = Reservation.objects.filter(
            salle=salle,
            statut__in=["En attente", "Confirmée"],
            dateDebut__lte=today,
            dateFin__gte=today
        ).exists()

        data.append({
            'salle': salle,
            'disponible': not reserved
        })

    return render(request, 'base/admin.html', {

        'data': data,

        'users': users,

        'reservations': reservations

    })
# Logout
def logout_view(request):

    logout(request)

    return redirect('acceuil')


# Toggle disponibilité
@login_required
def toggle_dispo(request, salle_id):

    dispo = Disponibilite.objects.filter(salle_id=salle_id).first()

    if dispo:
        dispo.estDisponible = not dispo.estDisponible
        dispo.save()

    return redirect('admin_dashboard')


#  Modifier salle
@login_required
def edit_salle(request, salle_id):

    if not hasattr(request.user, 'profile') or request.user.profile.role != "admin":
        return redirect('main')

    salle = get_object_or_404(Salle, id=salle_id)

    dispo = salle.disponibilite

    if request.method == "POST":

        salle.type = request.POST.get('type')

        salle.prix = request.POST.get('prix')

        salle.save()

        dispo.date = request.POST.get('date')

        disponible = request.POST.get('disponible')

        dispo.estDisponible = True if disponible == "True" else False

        dispo.save()

        return redirect('admin_dashboard')

    return render(request, 'base/edit_salle.html', {
        'salle': salle
    })


# Supprimer salle
@login_required
def delete_salle(request, salle_id):

    if not hasattr(request.user, 'profile') or request.user.profile.role != "admin":
        return redirect('main')

    salle = get_object_or_404(Salle, id=salle_id)

    salle.delete()

    return redirect('admin_dashboard')


#  Delete user
@login_required
def delete_user(request, user_id):

    user = get_object_or_404(User, id=user_id)

    if user.username != request.user.username:
        user.delete()

    return redirect('admin_dashboard')



@login_required
def reserver_salle(request, salle_id):

    salle = get_object_or_404(Salle, id=salle_id)

    if request.method == "POST":

        date_debut = request.POST.get('date_debut')

        date_fin = request.POST.get('date_fin')

        reservation_exist = Reservation.objects.filter(
            salle=salle,
            dateDebut__lte=date_fin,
            dateFin__gte=date_debut
        ).exists()

        if reservation_exist:

            return render(request, 'base/reservation.html', {
                'salle': salle,
                'error': 'Salle déjà réservée pour cette période'
            })

        # client lié
        client = Client.objects.filter(
            email=request.user.email
        ).first()

        # create reservation
        Reservation.objects.create(
            salle=salle,
            client=client,
            dateDebut=date_debut,
            dateFin=date_fin,
            statut='En attente'
        )

        return redirect('main')

    return render(request, 'base/reservation.html', {
        'salle': salle
    })
    
    
@login_required
def panier(request):

    client = Client.objects.filter(
        email=request.user.email
    ).first()

    reservations = Reservation.objects.filter(
        client=client
    )

    return render(request, 'base/panier.html', {
        'reservations': reservations
    })
    
    
@login_required
def annuler_reservation(request, reservation_id):

    reservation = get_object_or_404(
        Reservation,
        id=reservation_id
    )

    reservation.delete()

    return redirect('panier')


    
@login_required
def notifications_admin(request):

    reservations = Reservation.objects.filter(
        statut="En attente"
    ).order_by('-id')

    return render(
        request,
        'base/notifications.html',
        {
            'reservations': reservations
        }
    )
    
@login_required
def confirmer_reservation(request, reservation_id):

    reservation = get_object_or_404(
        Reservation,
        id=reservation_id
    )

    reservation.statut = "Confirmée"

    reservation.save()

    return redirect('notifications_admin')

@login_required
def rejeter_reservation(request, reservation_id):

    reservation = get_object_or_404(
        Reservation,
        id=reservation_id
    )

    reservation.statut = "Rejetée"

    reservation.save()

    dispo = Disponibilite.objects.filter(
        salle=reservation.salle
    ).first()

    if dispo:

        dispo.estDisponible = True

        dispo.save()

    return redirect('notifications_admin')




@login_required
def telecharger_facture(request, reservation_id):

    reservation = get_object_or_404(
        Reservation,
        id=reservation_id
    )

    response = HttpResponse(
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        f'attachment; filename=\"facture_{reservation.id}.pdf\"'
    )



    pdfmetrics.registerFont(
        TTFont(
            'Handwritten',
            'C:/Windows/Fonts/seguisb.ttf'
        )
    )

    p = canvas.Canvas(response)

    # BACKGROUND
    p.setFillColorRGB(0.96, 0.95, 0.93)

    p.rect(
        0,
        0,
        600,
        850,
        fill=1
    )

    # HEADER
    p.setFillColorRGB(0.72, 0.58, 0.35)

    p.rect(
        0,
        760,
        600,
        90,
        fill=1
    )

    # TITLE
    p.setFillColorRGB(1, 1, 1)

    p.setFont(
        "Handwritten",
        30
    )

    p.drawString(
        180,
        795,
        "GST.HOTEL"
    )

    p.setFont(
        "Handwritten",
        16
    )

    p.drawString(
        240,
        770,
        "FACTURE"
    )

    # WHITE BOX
    p.setFillColorRGB(1, 1, 1)

    p.roundRect(
        60,
        160,
        480,
        540,
        20,
        fill=1
    )

    # TEXT COLOR
    p.setFillColorRGB(0.1, 0.1, 0.1)

    # TITLE INFO
    p.setFont(
        "Handwritten",
        20
    )

    p.drawString(
        100,
        650,
        "Informations"
    )

    # CONTENT
    p.setFont(
        "Handwritten",
        15
    )

    p.drawString(
        100,
        600,
        f"Client : {reservation.client.nom}"
    )

    p.drawString(
        100,
        555,
        f"Salle : {reservation.salle.type}"
    )

    p.drawString(
        100,
        510,
        f"Prix : {reservation.salle.prix} DH"
    )

    p.drawString(
        100,
        465,
        f"Date debut : {reservation.dateDebut}"
    )

    p.drawString(
        100,
        420,
        f"Date fin : {reservation.dateFin}"
    )

    p.drawString(
        100,
        375,
        f"Statut : {reservation.statut}"
    )

    # GOLD LINE
    p.setStrokeColorRGB(0.72, 0.58, 0.35)

    p.line(
        100,
        345,
        500,
        345
    )
    #qr code
    qr_path = os.path.join(
        settings.BASE_DIR,
        'base',
        'static',
        'images',
        'qr.png'
    )

    p.drawImage(
        qr_path,
        350,
        190,
        width=130,
        height=130
    )

    # FOOTER
    p.setFillColorRGB(0.45, 0.45, 0.45)

    p.setFont(
        "Handwritten",
        11
    )

    p.drawString(
        170,
        110,
        "Merci pour votre confiance - GST HOTEL"
    )

    p.save()

    return response

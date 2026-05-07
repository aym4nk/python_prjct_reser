from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from salles.models import Salle, Disponibilite



from reservations.models import Reservation
from salles.models import Salle
from users.models import Client
from datetime import date


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
from users.models import Client


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
from datetime import date
from reservations.models import Reservation

@login_required
def main(request):

    salles = Salle.objects.all()

    data = []

    today = date.today()

    for salle in salles:

        reserved = Reservation.objects.filter(
            salle=salle,
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

# 👑 Dashboard admin
@login_required
def admin_dashboard(request):

    salles = Salle.objects.all()

    users = User.objects.all()

    data = []

    today = date.today()

    for salle in salles:

        reserved = Reservation.objects.filter(
            salle=salle,
            dateDebut__lte=today,
            dateFin__gte=today
        ).exists()

        data.append({
            'salle': salle,
            'disponible': not reserved
        })

    return render(request, 'base/admin.html', {
        'data': data,
        'users': users
    })
# 🚪 Logout
def logout_view(request):

    logout(request)

    return redirect('acceuil')


# 🔄 Toggle disponibilité
@login_required
def toggle_dispo(request, salle_id):

    dispo = Disponibilite.objects.filter(salle_id=salle_id).first()

    if dispo:
        dispo.estDisponible = not dispo.estDisponible
        dispo.save()

    return redirect('admin_dashboard')


# ✏️ Modifier salle
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


# ❌ Supprimer salle
@login_required
def delete_salle(request, salle_id):

    if not hasattr(request.user, 'profile') or request.user.profile.role != "admin":
        return redirect('main')

    salle = get_object_or_404(Salle, id=salle_id)

    salle.delete()

    return redirect('admin_dashboard')


# ❌ Delete user
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

        # 🔥 client lié
        client = Client.objects.filter(
            email=request.user.email
        ).first()

        # 🔥 create reservation
        Reservation.objects.create(
            salle=salle,
            client=client,
            dateDebut=date_debut,
            dateFin=date_fin,
            statut='Confirmée'
        )

        return redirect('main')

    return render(request, 'base/reservation.html', {
        'salle': salle
    })
    
    
from reservations.models import Reservation
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
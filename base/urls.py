from django.urls import path

from .views import (
    acceuil,
    login_view,
    register_view,
    main,
    logout_view,
    admin_dashboard,
    toggle_dispo,
    edit_salle,
    delete_salle,
    delete_user,
    reserver_salle,
    panier,
    annuler_reservation
)

urlpatterns = [

    path('', acceuil, name='acceuil'),

    path('login/', login_view, name='login'),

    path('register/', register_view, name='register'),

    path('main/', main, name='main'),

    path('logout/', logout_view, name='logout'),

    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),

    path(
        'toggle-dispo/<int:salle_id>/',
        toggle_dispo,
        name='toggle_dispo'
    ),

    path(
        'edit-salle/<int:salle_id>/',
        edit_salle,
        name='edit_salle'
    ),

    path(
        'delete-salle/<int:salle_id>/',
        delete_salle,
        name='delete_salle'
    ),

    path(
        'delete-user/<int:user_id>/',
        delete_user,
        name='delete_user'
    ),
    path(
    'reservation/<int:salle_id>/',
    reserver_salle,
    name='reserver_salle'
),
    path('panier/', panier, name='panier'),
    path(
    'annuler-reservation/<int:reservation_id>/',
    annuler_reservation,
    name='annuler_reservation'
),
]
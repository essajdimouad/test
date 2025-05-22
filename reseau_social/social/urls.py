from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed, name='home'),  # Accueil avec les publications
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('users/', views.user_list, name='user_list'),
    path('messages/<int:user_id>/', views.send_message, name='messages'),
    path('inbox/', views.inbox, name='inbox'),
  

    # Routes pour le profil personnel
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # ✅ Voir le profil d’un autre utilisateur
    path('profile/<str:username>/', views.profile_detail, name='profile_detail'),

    # ✅ Follow / Unfollow
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),

    # ✅ Like publication
    path('like/<int:pub_id>/', views.like_publication, name='like_publication'),

    # ✅ Commenter une publication
    path('comment/<int:pub_id>/', views.add_comment, name='add_comment'),
]

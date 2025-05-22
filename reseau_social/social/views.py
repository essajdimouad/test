from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Publication, Message, Profile, Commentaire
from .forms import PublicationForm, ProfileForm, UserForm, MessageForm

@login_required
def feed(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    following_users = [profile.user for profile in request.user.profile.follows.all()]
    following_users.append(request.user)  # Include user's own posts

    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES)
        if form.is_valid():
            pub = form.save(commit=False)
            pub.auteur = request.user
            pub.save()
            messages.success(request, "Publication ajoutée avec succès.")
            return redirect('home')
        else:
            messages.error(request, "Erreur lors de la publication.")
    else:
        form = PublicationForm()

    publications = Publication.objects.filter(auteur__in=following_users).order_by('-date_creation')

    return render(request, 'social/feed.html', {
        'form': form,
        'publications': publications,
        'profile': profile,
    })

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)  # Create profile automatically
            messages.success(request, "Inscription réussie. Connectez-vous maintenant.")
            return redirect('login')
        else:
            messages.error(request, "Erreur dans le formulaire. Veuillez réessayer.")
    else:
        form = UserCreationForm()
    return render(request, 'social/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Connexion réussie.")
            return redirect('home')
        else:
            messages.error(request, "Identifiants invalides.")
    else:
        form = AuthenticationForm()
    return render(request, 'social/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Vous êtes déconnecté.")
    return redirect('login')

@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id)
    following = request.user.profile.follows.all()
    return render(request, 'social/user_list.html', {
        'users': users,
        'following': following
    })

@login_required
def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    publications = Publication.objects.filter(auteur=user).order_by('-date_creation')
    
    return render(request, 'social/profile_detail.html', {
        'profile': profile,
        'publications': publications,
    })

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow != request.user:
        request.user.profile.follows.add(user_to_follow.profile)
        messages.success(request, f"Vous suivez maintenant {username}")
    return redirect('profile_detail', username=username)

@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    request.user.profile.follows.remove(user_to_unfollow.profile)
    messages.success(request, f"Vous ne suivez plus {username}")
    return redirect('profile_detail', username=username)

@login_required
def like_publication(request, pub_id):
    publication = get_object_or_404(Publication, id=pub_id)
    if request.user in publication.likes.all():
        publication.likes.remove(request.user)
    else:
        publication.likes.add(request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('home')))

@login_required
def add_comment(request, pub_id):
    publication = get_object_or_404(Publication, id=pub_id)
    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        if contenu:
            Commentaire.objects.create(
                publication=publication,
                auteur=request.user,
                contenu=contenu
            )
            messages.success(request, "Commentaire ajouté avec succès.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('home')))

@login_required
def send_message(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.save()
            messages.success(request, "Message envoyé avec succès.")
            return redirect('messages', user_id=user_id)
    else:
        form = MessageForm()
    
    messages_list = Message.objects.filter(
        Q(sender=request.user, receiver=receiver) |
        Q(sender=receiver, receiver=request.user)
    ).order_by('timestamp')
    
    return render(request, 'social/messages.html', {
        'form': form,
        'messages': messages_list,
        'other_user': receiver
    })

@login_required
def inbox(request):
    received = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    sent = Message.objects.filter(sender=request.user).order_by('-timestamp')
    return render(request, 'social/inbox.html', {
        'received': received,
        'sent': sent
    })

@login_required
def profile_edit(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('profile_view')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'social/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def profile_view(request):
    return render(request, 'social/profile_view.html', {
        'profile': request.user.profile
    })
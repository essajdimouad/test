from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Publication, Message, Profile
from .forms import PublicationForm, ProfileForm, UserForm

@login_required
def feed(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

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

    publications = Publication.objects.all().order_by('-date_creation')

    return render(request, 'social/feed.html', {
        'form': form,
        'publications': publications,
        'profile': profile,
    })

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
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

def logout_view(request):
    logout(request)
    messages.info(request, "Vous êtes déconnecté.")
    return redirect('login')

@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'social/user_list.html', {'users': users})

@login_required
def inbox(request):
    received_messages = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    return render(request, 'social/inbox.html', {
        'messages': received_messages
    })

@login_required
def send_message(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=request.user, receiver=other_user, content=content)
            messages.success(request, "Message envoyé.")
            return redirect('messages', user_id=other_user.id)

    all_messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')

    return render(request, 'social/messages.html', {
        'messages': all_messages,
        'other_user': other_user
    })

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'social/profile_view.html', {'profile': profile})

@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('profile_view')
        else:
            messages.error(request, "Erreur lors de la mise à jour du profil.")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'social/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

# Voir le profil d’un autre utilisateur
@login_required
def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
    is_following = request.user.profile.follows.filter(id=user.id).exists()
    publications = Publication.objects.filter(auteur=user).order_by('-date_creation')
    return render(request, 'social/profile_detail.html', {
        'profile_user': user,
        'profile': profile,
        'is_following': is_following,
        'publications': publications,
    })

# Suivre un utilisateur
@login_required
def follow_user(request, username):
    target_user = get_object_or_404(User, username=username)
    request.user.profile.follows.add(target_user)
    return redirect('profile_detail', username=username)

# Ne plus suivre un utilisateur
@login_required
def unfollow_user(request, username):
    target_user = get_object_or_404(User, username=username)
    request.user.profile.follows.remove(target_user)
    return redirect('profile_detail', username=username)

# Aimer une publication
@login_required
def like_publication(request, pub_id):
    publication = get_object_or_404(Publication, id=pub_id)
    if request.user in publication.likes.all():
        publication.likes.remove(request.user)
    else:
        publication.likes.add(request.user)
    return HttpResponseRedirect(reverse('home'))

# Commenter une publication
@login_required
def add_comment(request, pub_id):
    publication = get_object_or_404(Publication, id=pub_id)
    content = request.POST.get('comment')
    if content:
        publication.comment_set.create(auteur=request.user, contenu=content)
    return HttpResponseRedirect(reverse('home'))
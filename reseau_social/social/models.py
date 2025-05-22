from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    ville = models.CharField(max_length=100, blank=True)
    date_naissance = models.DateField(blank=True, null=True)
    loisirs = models.CharField(max_length=255, blank=True)  # Nouveau champ ajouté
    
    # Ajout ManyToMany pour les abonnements
    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True
    )

    def __str__(self):
        return self.user.username

    def is_following(self, other_profile):
        """Retourne True si ce profil suit other_profile"""
        return self.following.filter(pk=other_profile.pk).exists()

    def followers_count(self):
        """Compte le nombre de followers"""
        return self.followers.count()

    def following_count(self):
        """Compte le nombre de profils suivis"""
        return self.following.count()


class Publication(models.Model):
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='publications')
    contenu = models.TextField()
    image = models.ImageField(upload_to='publications', blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def __str__(self):
        return f"{self.auteur.username} - {self.date_creation.strftime('%Y-%m-%d %H:%M')}"


class Commentaire(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='commentaires')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.auteur.username} sur {self.publication.id} : {self.contenu[:20]}"


class Like(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='likes')
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('publication', 'utilisateur')  # Un utilisateur ne peut liker une publication qu’une fois

    def __str__(self):
        return f"{self.utilisateur.username} aime {self.publication.id}"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username} : {self.content[:20]}"

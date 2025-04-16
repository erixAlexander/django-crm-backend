from django.db import models
from django.contrib.auth.models import AbstractUser


class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=150)

    def __str__(self):
        return self.title


class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    industry = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("agent", "Agent"),
        ("client", "Client"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="client")

    # ✅ This line connects the user to the organization
    organization = models.ForeignKey(
        Organization,  # model being related to
        on_delete=models.CASCADE,  # if org is deleted, delete its users
        related_name="users",  # lets you do org.users.all()
        null=True,
        blank=False,
    )

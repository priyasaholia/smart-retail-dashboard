from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    ACCOUNT_TYPES = [
        ("customer", "Customer"),
        ("retailer", "Retailer"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default="customer")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.account_type})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Alert(models.Model):
    # 🔑 USER OWNERSHIP (ADDED)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="alerts",
        null=True,
        blank=True
    )

    message = models.CharField(max_length=255)
    source = models.CharField(max_length=100, default="system")
    created_at = models.DateTimeField(auto_now_add=True)

    priority = models.CharField(
        max_length=20,
        choices=[
            ("critical", "Critical"),
            ("medium", "Medium"),
            ("low", "Low"),
        ],
        default="medium"
    )

    ai_explanation = models.TextField(blank=True, null=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.message


class NotebookEntry(models.Model):
    # 🔑 USER OWNERSHIP (ADDED)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notebook_entries",
        null=True,
        blank=True
    )

    ENTRY_TYPES = [
        ("sale", "Sale"),
        ("expense", "Expense"),
        ("purchase", "Purchase"),
        ("note", "General Note"),
    ]

    entry_type = models.CharField(
        max_length=20,
        choices=ENTRY_TYPES
    )

    amount = models.FloatField(
        null=True,
        blank=True,
        help_text="Amount involved (if applicable)"
    )

    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.entry_type.upper()} | {self.amount}"

from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Alert(models.Model):
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


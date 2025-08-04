from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cash_balance = models.DecimalField(max_digits=15, decimal_places=2, default=10000.00)
    gold_balance = models.DecimalField(max_digits=15, decimal_places=4, default=0.0000)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=4)  # Gold amount
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per unit
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {self.type} {self.amount} gold at {self.price}"


# Signal to create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save() 
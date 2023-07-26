from django.contrib.auth.models import AbstractUser
from django.db import models

# for watch list to be auto created for each user.
from django.db.models.signals import post_save
from django.dispatch import receiver

from decimal import Decimal


class User(AbstractUser):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    
    def __str__(self):
        return f"{self.username} | {self.first_name} {self.last_name}"

class Category(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.name}"
    
class Listing(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits = 10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True, max_length=300) # optional
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings", blank=True, null=True) #optional
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "listings")
    created_at = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)  # Indicates if the auction is closed
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="won_auctions", null=True, blank=True)  # Tracks the winner of the auction (if any)
    
    def __str__(self):
        return f"{self.title}: {self.starting_bid}"
    
    @property
    def current_bid(self):
        highest_bid = self.bids.order_by('-amount').first()
        
        if highest_bid:
            return Decimal(highest_bid.amount).quantize(Decimal('0.00'))
        
        return Decimal(0).quantize(Decimal('0.00'))

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.listing.title}: {self.bidder}: {self.amount}"

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name = "comments")
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.listing.title}: {self.commenter}: {self.text}"
    
class WatchList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="watch_list")
    listings = models.ManyToManyField(Listing)
    
    def __str__(self):
        return str(self.user)

@receiver(post_save, sender=User)
def create_watchlist(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'watch_list'):
        WatchList.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_watchlist(sender, instance, **kwargs):
    if hasattr(instance, 'watch_list'):
        instance.watch_list.save()

    
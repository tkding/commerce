from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import User, Listing, Bid, WatchList, Category, Comment
from .forms import ListingForm, BidForm, CommentForm

def index(request):
    active_listings = Listing.objects.filter(closed=False)
    return render(request, "auctions/index.html", {
        "active_listings": active_listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
def create_listing(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))


    if request.method == "POST":
        form = ListingForm(request.POST) 
        if form.is_valid():
            listing = Listing(
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                starting_bid=form.cleaned_data["starting_bid"],
                image_url=form.cleaned_data["image_url"],
                category=form.cleaned_data["category"],
                creator=request.user
            )
            
            listing.save()
            return HttpResponseRedirect(reverse("index"))
        
        else:
            form = ListingForm()
        
    return render(request, "auctions/create_listing.html", {
        'form' : ListingForm()
    })
    
def listing(request, listing_id):
    # Clicking on a listing should take users to a page specific to that listing. On that page, users should be able to view all details about the listing, including the current price for the listing.
    listing = get_object_or_404(Listing, pk=listing_id)
    current_bid = listing.current_bid
    watchlisted = False
    is_creator = False
    won_auction = False
        
    bid_form = BidForm()
    comment_form = CommentForm()
    
    if request.user.is_authenticated:
        user = request.user
        watchlist = None
        try:
            watchlist = user.watch_list
        except WatchList.DoesNotExist:
            # create a WatchList for the user if it doesn't exist
            watchlist = WatchList(user=user)
            watchlist.save()
        
        
        watchlisted = watchlist.listings.filter(pk=listing_id).exists()
        is_creator = request.user == listing.creator
        won_auction = listing.winner == request.user if listing.winner else False
    
    if request.method == "POST":
        # If the user is signed in, the user should be able to add the item to their “Watchlist.” If the item is already on the watchlist, the user should be able to remove it.
        if "add_to_watchlist" in request.POST:
            watchlist.listings.add(listing)
            watchlist.save() 
            return HttpResponseRedirect(reverse("listing", args=(listing.id, )))
        
        elif "remove_from_watchlist" in request.POST:
            watchlist.listings.remove(listing)
            watchlist.save() 
            return HttpResponseRedirect(reverse("listing", args=(listing.id, )))
        
        # If the user is signed in, the user should be able to bid on the item. The bid must be at least as large as the starting bid, and must be greater than any other bids that have been placed (if any). If the bid doesn’t meet those criteria, the user should be presented with an error.
        elif "place_bid" in request.POST:
            form = BidForm(request.POST)
            if form.is_valid():
                bid_amount = form.cleaned_data["amount"]
                if bid_amount >= listing.starting_bid and bid_amount > current_bid:
                    print("bid_amount:", bid_amount)
                    print("starting bid:", listing.starting_bid)
                    print("current bid:", current_bid)
                    bid = Bid(listing=listing, bidder=request.user, amount=bid_amount)
                    bid.save()
                    current_bid = bid_amount
                    
                else:
                    error_message = "Invalid bid. The bid amount must be at least as large as the starting bid and greater than the current highest bid"
                    return render(request, "auctions/listing.html", {
                        "listing": listing,
                        "current_bid": current_bid,
                        "bid_form": form,
                        "watchlisted": watchlisted,
                        "is_creator": is_creator,
                        "won_auction": won_auction,
                        "error_message": error_message,
                        "comment_form": comment_form   
                    })
        
        # If the user is signed in and is the one who created the listing, the user should have the ability to “close” the auction from this page, which makes the highest bidder the winner of the auction and makes the listing no longer active.
        # If a user is signed in on a closed listing page, and the user has won that auction, the page should say so.
        elif "close_auction" in request.POST and is_creator:
            if not listing.closed: # TODO add close attribute
                if listing.bids.exists():
                    highest_bid = listing.bids.order_by("-amount").first()
                    listing.winner = highest_bid.bidder
                    listing.closed = True
                    listing.save()
                else:
                    error_message = "Cannot close the auction. There are no bids on this listing."
                    return render(request, "auctions/listing.html", {
                        "listing": listing,
                        "current_bid": current_bid,
                        "bid_form": form,
                        "watchlisted": watchlisted,
                        "is_creator": is_creator,
                        "won_auction": won_auction,
                        "error_message": error_message,
                        "comment_form": comment_form   
                    })
            else:
                error_message = "The auction is already closed."
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "current_bid": current_bid,
                    "bid_form": form,
                    "watchlisted": watchlisted,
                    "is_creator": is_creator,
                    "won_auction": won_auction,
                    "error_message": error_message,
                    "comment_form": comment_form   
                })
                
        # Users who are signed in should be able to add comments to the listing page. The listing page should display all comments that have been made on the listing.
        elif "add_comment" in request.POST:
            form = CommentForm(request.POST)
            
            if form.is_valid():
                print("comment is valid")
                comment_text = form.cleaned_data["text"]
                comment = Comment(listing=listing, commenter=request.user, text=comment_text)
                comment.save()
                return HttpResponseRedirect(reverse("listing", args=(listing.id, )))

            else:
                error_message = "Invalid comment."
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "current_bid": current_bid,
                    "bid_form": form,
                    "watchlisted": watchlisted,
                    "is_creator": is_creator,
                    "won_auction": won_auction,
                    "error_message": error_message,
                    "comment_form": comment_form   
                })


    return render(request, "auctions/listing.html", {
        "listing": listing,
        "current_bid": current_bid,
        "bid_form": bid_form,
        "watchlisted": watchlisted,
        "is_creator": is_creator,
        "won_auction": won_auction,
        "comment_form": comment_form   
    })
    
    
def watchlist(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    watchlist = request.user.watch_list
    listings = watchlist.listings.all()
    
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

def category_list(request):
    categories = Category.objects.all()
    return render(request, "auctions/category_list.html", {
        "categories": categories
    })

def category_detail(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    active_listings = Listing.objects.filter(category=category, closed=False)
    return render(request, "auctions/category_detail.html", {
        "category": category,
        "active_listings": active_listings
    })
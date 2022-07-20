from asyncio.constants import LOG_THRESHOLD_FOR_CONNLOST_WRITES
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from .models import User, Listing, Bid
from .forms import ListingForm


def index(request):
    return render(request, "auctions/index.html", {
        'listings': Listing.objects.all()
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


def new_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.owner = request.user
            instance.save()
            return redirect('/')
    form = ListingForm()
    return render(request, "auctions/new_listing.html", {
        "form": form
    })

def listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if listing.watchlist.filter(id=request.user.id).exists():
        added = True
    else:
        added = False

    context = {
        "listing": listing, 
        "added": added 

    }
    return render(request, "auctions/listing.html", context )

def add_remove_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    added = False
    if listing.watchlist.filter(id=request.user.id).exists():
        listing.watchlist.remove(request.user)
        added = False
    else:
        listing.watchlist.add(request.user)
        added = True
    return redirect('listing', listing_id)
    
    
    
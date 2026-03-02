from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from .models import home, Property, Booking, Profile
from .forms import (
    PropertyForm,
    homeForm,
    UserRegistrationForm,
    UserUpdateForm,
    ProfileUpdateForm,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

def index(request):
    return render(request, 'index.html')


def home_list(request):
    homes = home.objects.all().order_by('-created_at')
    return render(request, 'home_list.html', {'homes': homes})

@login_required
def home_create(request):
    if request.method == "POST":
        form = homeForm(request.POST, request.FILES)
        if form.is_valid():
            home_obj = form.save(commit=False)
            home_obj.user = request.user
            home_obj.save()
            return redirect('home_list')
    else:
        form = homeForm()
    return render(request, 'home_form.html', {'form': form})

@login_required
def home_edit(request, home_id):
    home_obj = get_object_or_404(home, pk=home_id, user=request.user)
    if request.method == 'POST':
        form = homeForm(request.POST, request.FILES, instance=home_obj)
        if form.is_valid():
            home_obj = form.save(commit=False)
            home_obj.user = request.user
            home_obj.save()
            return redirect('home_list')
    else:
        form = homeForm(instance=home_obj)
    return render(request, 'home_form.html', {'form': form})

@login_required
def home_delete(request, home_id):
    home_obj = get_object_or_404(home, pk=home_id, user=request.user)
    if request.method == 'POST':
        home_obj.delete()
        return redirect('home_list')
    return render(request, 'home_confirm_delete.html', {'home': home_obj})

# for the  login gistration
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form':form})


# For the property.html
@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.user = request.user
            prop.save()
            return redirect('properties')
    else:
        form = PropertyForm()

    return render(request, 'add_property.html', {'form': form})


def property_list(request):
    properties = Property.objects.all()
    sort_option = request.GET.get('sort')

    properties = Property.objects.all()

    if sort_option == 'low_to_high':
        properties = properties.order_by('price')
    elif sort_option == 'high_to_low':
        properties = properties.order_by('-price')

    context = {
        'properties': properties
    }

    # return render(request, 'home/property_list.html', context)
    return render(request, 'property_list.html',{'properties':properties})

def property_detail(request, property_id):
    property_obj = get_object_or_404(Property, pk=property_id)
    is_compact_view = request.GET.get('view') == 'compact'
    return render(request, 'property_detail.html', {
        'property': property_obj,
        'is_compact_view': is_compact_view,
    })


@login_required
def property_edit(request, property_id):
    prop = get_object_or_404(Property, pk=property_id, user=request.user)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=prop)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.user = request.user
            prop.save()
            return redirect('properties')
    else:
        form = PropertyForm(instance=prop)
    return render(request, 'add_property.html', {'form': form})


@login_required
def property_delete(request, property_id):
    prop = get_object_or_404(Property, pk=property_id, user=request.user)
    if request.method == 'POST':
        prop.delete()
        return redirect('properties')
    return render(request, 'property_confirm_delete.html', {'property': prop})


@login_required
def book_property(request, property_id):
    property = get_object_or_404(Property, id=property_id)

    if request.user != property.user:
        Booking.objects.create(
            property=property,
            booked_by=request.user,
            owner=property.user
        )

    return redirect('properties')

@login_required
def notifications(request):
    notifications = request.user.owner_bookings.all().order_by('-booked_at')
    return render(request, 'notifications.html', {
        'notifications': notifications
    })


@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        Booking, pk=notification_id, owner=request.user
    )

    if request.method == 'POST':
        notification.is_read = True
        notification.save(update_fields=['is_read'])

    return redirect('notifications')


@login_required
def mark_all_notifications_read(request):
    if request.method == 'POST':
        Booking.objects.filter(owner=request.user, is_read=False).update(is_read=True)

    return redirect(request.META.get('HTTP_REFERER', 'notifications'))


@login_required
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=profile_obj
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("profile")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile_obj)

    return render(
        request,
        "profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
        },
    )

from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from .models import home, Property
from .forms import PropertyForm, homeForm, UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
# from .models import property

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
        UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit= False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
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

@login_required
def property_edit(request, property_id):
    prop_obj = get_object_or_404(Property, pk=property_id, user=request.user)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=prop_obj)
        if form.is_valid():
            prop_obj = form.save(commit=False)
            prop_obj.user = request.user
            prop_obj.save()
            return redirect('properties')
    else:
        form = PropertyForm(instance=prop_obj)
    return render(request, 'add_property.html', {'form': form, 'is_edit': True})


@login_required
def property_delete(request, property_id):
    prop_obj = get_object_or_404(Property, pk=property_id, user=request.user)
    if request.method == 'POST':
        prop_obj.delete()
        return redirect('properties')
    return render(request, 'property_confirm_delete.html', {'property': prop_obj})

def property_list(request):
    properties = Property.objects.all()
    return render(request, 'property_list.html',{'properties':properties})

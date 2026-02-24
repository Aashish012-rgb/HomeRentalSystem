from django.shortcuts import render
from .models import home
from .forms import homeForm
from django.shortcuts import get_object_or_404, redirect
# Create your views here.
def index(request):
    return render(request, 'index.html') 


def home_list(request):
    homes = home.objects.all().order_by('-created_at')
    return render(request, 'home_list.html',{'homes': homes})

def homes_create(request):
    if request.method =="POST":
        form= homeForm(request.POST, request.FILES)
        if form.is_valid():
            home = form.save(commit=False)
            home.user = request.user
            home.save()
            return redirect('home_list')
    else:
        form = homeForm()
    return render(request,'home_form.html',{'form':form})

def home_edit(request, home_id):
    home = get_object_or_404(home, pk=home_id, user = request.user)
    if request.method=='POST':
        form= homeForm(request.POST, request.FILES, instance= home)
        if form.is_valid():
            home =form.save(commit =False)
            home.user= request.user
            home.save()
            return redirect('home_list')
            
    else:
        form = homeForm(instance=home)
    return render(request, 'home_form.html',{'form':form})


def home_delete(request, home_id):
    home = get_object_or_404(home, pk=home_id, user = request.user)
    if request.method =='POST':
        home.delete()
        return redirect('home_list')
    return render(request, 'home_confirm_delete.html',{'home':home})

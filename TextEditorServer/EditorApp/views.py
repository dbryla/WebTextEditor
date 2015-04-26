from forms import UserForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from mongoengine.django.auth import User
from django.contrib.auth import logout

def createUser(request):
    print request.POST
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = User.create_user(form.username, form.password)
            return HttpResponseRedirect('/')
        else:
            return render(request, 'registration/createUser.html', {'form': UserForm(), 'error': form.error}) 
    else:
        form = UserForm() 

    return render(request, 'registration/createUser.html', {'form': form}) 

def logoutUser(request):
    logout(request)
    return HttpResponseRedirect("/") 
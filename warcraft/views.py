from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader, Context
from django.shortcuts import render, render_to_response, redirect
from django.contrib import auth
from django.core.context_processors import csrf
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import JsonResponse
import re
from simple_email_confirmation import *
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.core.mail import send_mail
from warcraft.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from .models import LoggedUser, Friends
from django.contrib.auth.decorators import login_required

from .forms import AuthenticationForm, RegistrationForm, EditProfileForm, ChangePasswordForm, FriendsForm

from .tasks import *

media = '/home/alysamc/ecs160/media/'


# Create your views here.

def index(request):
    template = loader.get_template('warcraft/index.html')
    return HttpResponse(template.render())
    
def ranking(request):
    top_players = User.objects.order_by('-rating')
    current_index = 1
    for player in top_players:
        player.ranking = current_index
        player.save()
        current_index = current_index + 1
    return render(request, 'warcraft/ranking.html', {'players': top_players})
    
def updateScores(request, winningPlayer, losingPlayer):
    k = 10 #The K value is an arbitrary value we choose based on how much we want
    #a player's score to increase/decrease after a match
    Ea = 1 / (1 + 10** ((winningPlayer.rating - losingPlayer.rating) / 400))
    Eb = 1 / (1 + 10** ((losingPlayer.rating - winningPlayer.rating) / 400))
    winningPlayer.rating = winningPlayer.rating + k * (1 - Ea)
    losingPlayer.rating = losingPlayer.rating + k * (0 - Eb)
    
def prototype_form(request):
    template = loader.get_template('warcraft/prototype_form.html')
    return HttpResponse(template.render())

def prototype(request):
    error = False
    message=""
    if 'q' in request.GET:
        q = request.GET['q']
        if not q:
            error = True
            message = "BAD INPUT"
            return render(request, 'warcraft/prototype_form.html', {'error':error, 'message':message})
        else:
            message = '%s' %request.GET['q']
            if message == "":
                message = "BAD INPUT"
                return render(request, 'warcraft/prototype_form.html', {'error':True, 'message':message})
            else:
                return render(request, 'warcraft/prototype_form.html', {'error':error, 'message':message})
    else:
        return render(request, 'warcraft/prototype_form.html', {'error':error, 'message':message})

def activate(request):
    if request.method == 'POST':
        return render(request, 'warcraft/activate.html')
    else:
        return render(request, 'warcraft/activate.html')
        


def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(userName=request.POST['userName'], password=request.POST['password'])
            if user is not None:
                if user.is_active:
                    user.login_web = True
                    django_login(request, user)
                    return redirect('/accounts/loggedin')
                else:
                    message = "You are not a verified user, please check your email."
                    return render(request, 'warcraft/invalid_login.html', {'user_name': "",'message':message})
            else:
                return HttpResponseRedirect('/accounts/invalid')
        else:
            print form.errors
    else:
        form = AuthenticationForm()
    return render_to_response('warcraft/login.html', {'form': form,}, context_instance=RequestContext(request))

'''def auth_view(request):
    username = request.POST.get('username','')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        if user.is_active is not False:
            auth.login(request, user)
            return HttpResponseRedirect('/accounts/loggedin')
        else:
            message="You are not a verified user, please check your email."
            return render(request, 'warcraft/invalid_login.html', {'user_name': request.user.username,'message':message})  
    else:
        return HttpResponseRedirect('/accounts/invalid')'''
        
        
def activate(request, userName, activation_key):
    confirmed = "Your account and email have been confirmed!"
    exception = "Sorry confirmation key does not match email on file"
    not_found = "Sorry user name not found" 
    ACuser = User.objects.get(userName = userName)
    if ACuser is not None:
        if ACuser.email  == ACuser.confirm_email(activation_key):
            ACuser.is_active = True
            ACuser.save()
            return render(request, 'warcraft/activate.html', {'message': confirmed}) 
        else:
            return render(request, 'warcraft/activate.html', {'message': exception})
    else:
        return render(request, 'warcraft/activate.html', {'message': not_found})

def logout(request):
    django_logout(request)
    return render_to_response('warcraft/logout.html')

def loggedin(request):
    picture = request.user.picture
    fname = request.user.firstName
    lname = request.user.lastName
    wins = request.user.get_wins
    losses = request.user.get_losses
    rating = request.user.get_rating
    ranking = request.user.get_ranking
    return render(request, 'warcraft/loggedin.html', {'full_name': fname+" "+lname, 'avatar':picture, 'wins': wins, 'losses': losses, 'rating': rating, 'ranking': ranking})

def invalid_login(request):
    message= "Invalid login credentials"
    emptystring=""
    return render(request, 'warcraft/invalid_login.html', {'user_name':emptystring, 'message':message})
    
@login_required(login_url='/accounts/login/')    
def edit_profile(request):
    if request.method == "POST":
        form = EditProfileForm(data=request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            if 'picture' in request.FILES:
              user.picture = request.FILES['picture']
            user.save()
            picture = request.user.picture
            fname = request.user.firstName
            lname = request.user.lastName
            email = request.user.email
            return render(request, 'warcraft/edit_profile_success.html', {'full_name': fname+" "+lname, 'picture':picture, 'email':email})
    else:
        form = EditProfileForm(instance=request.user)
        currentUser = request.user
        friendsList = currentUser.friends_set.values_list('name', flat=True)
        friendsname = []
        for name in friendsList:
            userobj = User.objects.get(userName = name)
            if userobj.login_web:
                friendsname.append((userobj.userName, "Online", userobj.picture))
            elif userobj.login_internal:
                friendsname.append((userobj.userName, "In the game", userobj.picture))
            else:
                friendsname.append((userobj.userName,"Offline", userobj.picture))
    return render(request, 'warcraft/edit_profile.html', {'form': form, 'friendsname': friendsname})

    
def edit_profile_success(request):
    fname = request.user.firstName
    lname = request.user.lastName
    email = request.user.email
    picture = request.user.picture
    return render(request, 'warcraft/edit_profile_success.html', {'full_name': fname+" "+lname, 'email': email, 'picture':picture})

def change_password(request,):
    if request.method == "POST":
        form = ChangePasswordForm(data=request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            return render(request, 'warcraft/change_password_success.html')
    else:
        form = ChangePasswordForm(instance=request.user)
    return render_to_response('warcraft/change_password.html', {'form': form}, context_instance=RequestContext(request))

def change_password_success (request):
    return render(request, 'warcraft/change_password_success.html')
    
    

def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            link = "http://alysamc.koding.io/accounts/activate/%s/%s/" %(user.userName, user.confirmation_key)
            picture = user.picture
            d = Context({'username':user.userName, 'link':link, 'avatar':picture}) 
            message = "%s please visit http://apmishra100.koding.io/accounts/activate/%s/%s/ to activate your account." %(user.userName, user.userName, user.confirmation_key)
            plaintext = get_template('warcraft/email.txt')
            htmly = get_template('warcraft/email.html')
            text_content = plaintext.render(d)
            html_content = htmly.render(d)
            subject = "Acivation"
            from_email = "chriscraftecs160@gmail.com"
            msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return redirect('/accounts/register_success')
    else:
        form = RegistrationForm()
    return render_to_response('warcraft/register.html', {'form': form,}, context_instance=RequestContext(request))
    

def register_success (reqest):
    return render_to_response('warcraft/register_success.html')

def internalLogin (request):
    if request.method == 'GET':
        username = request.META['HTTP_USERNAME']
        password = request.META['HTTP_PASSWORD']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_active is not False:
                user.login_internal = True
                django_login(request, user)
                return JsonResponse({'LoginStatus': 'Success'})
            else:
                return JsonResponse({'LoginStatus': 'Unverified'} )
        else:
            return JsonResponse({'LoginStatus': 'Incorrect Credentials'})

def webLoggedIn (request):
    web_users = LoggedUser.objects.all().filter(web=True)
    return render(request, 'warcraft/web_users.html', {'users' : web_users})
    
def internalLoggedIn (request):
    internal_users = LoggedUser.objects.all().filter(internal=True)
    return render(request, 'warcraft/internal_users.html', {'users' : internal_users})
    
def downloads(request):
    template = loader.get_template('warcraft/downloads.html')
    return HttpResponse(template.render())

def compose_success(request):
    x = request.POST.get("recipient", "")
    send_mail('You sent mail!', 'You send a message!', 'chriscraftecs160@gmail.com', [request.user.email], fail_silently=False)
    return render(request, 'warcraft/compose_success.html', {'recipient' : x})

def send_something(request):
    send_something_1()
    return render(request, 'warcraft/send_something.html')

def friends(request):
    message = ''
    if request.method == 'POST':
        form = FriendsForm(request.POST)
        if form.is_valid():
            if User.objects.filter(userName=request.POST['name']):
                friend = User.objects.get(userName=request.POST['name'])
            else:
                message = 'User not found'
                return render(request, 'warcraft/friends.html', {'form': form, 'message': message})
            if friend is not None:
                message = 'User found, added to friends'
                currentUser = request.user
                if currentUser.userName == friend.userName:
                    message = "Sorry you cannot add yourself as a friend"
                    return render(request, 'warcraft/friends.html', {'form': form, 'message': message})
                if 'delete' in request.POST:
                    message = 'User deleted'
                    if Friends.objects.filter(name = friend.userName, friends = currentUser):
                        friend = Friends.objects.get(name = friend.userName, friends = currentUser)
                        currentUser.friends_set.remove(friend)
                        currentUser.save()
                        return render(request, 'warcraft/friends.html', {'form': form, 'message': message})
                    else:
                        message = 'User not found in friend list'
                        return render(request, 'warcraft/friends.html', {'form': form, 'message': message})
                
                
                if Friends.objects.filter(name = friend.userName, friends = request.user):
                    message = 'User is already a friend'
                    return render(request, 'warcraft/friends.html', {'form' : form, 'message' : message})
                  
                else:
                    friendobj = Friends(name = friend.userName, friends = currentUser)
                    currentUser.friends_set.add(friendobj)
                    currentUser.save()
                    return render(request, 'warcraft/friends.html', {'form' : form, 'message' : message})
            else: 
                message = 'User not found, please retry'
                return render(request, 'warcraft/friends.html', {'form':form, 'message' : message})
        else:
            print form.errors
    else:
        form = FriendsForm()
    return render(request, 'warcraft/friends.html', {'form': form, 'message' : message})

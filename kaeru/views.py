from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.context_processors import csrf

import os

# These pages should live in 'kaeru/templates/about/'
# Alternatively, these names could live in a database
#ABOUT_PAGES = [
#    'about',
#    'faq',
#    'people',
#    'support',
#]
#def about_view(request, pagename='about'):
#    # Search for a matching template page, raise 404 if none found.
#    if pagename in ABOUT_PAGES:
#        return render_to_response('about/%s.html' % pagename, {})
#    else:
#        raise Http404

def documentation_view(request):
    return render_to_response('documentation.html', {})

#def index_view(request):
#    return render_to_response('index.html', {})

def people_view(request):
    return render_to_response('people.html', {})

def _get_csrf_cookie(request):
    # Authenticate cookies for django csrf (cross-site reference) forms
    cookie = {}
    cookie.update(csrf(request)) # Required for csrf form protection
    if hasattr(request, 'user'):
        cookie['user'] = request.user
    return cookie

def login_view(request):
    # Log existing user into the system
    cookie = _get_csrf_cookie(request)
    if request.method == "POST":
        # Try to log the user in.
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = auth.authenticate(username=username,password=password)
        if user is None:
            cookie['error_message'] = "Login failed."
        elif not (user.is_active):
            cookie['error_message'] = "Username/Password combo is valid, but the account has been disabled."
        else:
            # User is valid, active, and authenticated. Log in.
            auth.login(request, user)
        return render_to_response('login.html', cookie)
    else:
        # Show the login page.
        return render_to_response('login.html', cookie)

def logout_view(request):
    if request.user.is_authenticated:
        # Successful logout
        username = request.user.username
        auth.logout(request)
        return render_to_response('logout.html', {'username': username})
    else:
        # Logout is a no-op. Nobody was logged in.
        return render_to_response('logout.html', {})

#@login_required
#def secret_view(request):
#    return render_to_response('secret.html', {})
    
#this used to be 'signup_view' and there used to be a separate 'index_view'
def index_view(request):
    cookie = _get_csrf_cookie(request)
    url = 'index.html'
    if request.method == "POST":
        # Create the account
        raw_username = request.POST.get('username', None)
        raw_password = request.POST.get('password', None)
        user, is_new = auth.models.User.objects.get_or_create(
                   username   = raw_username,
                   email      = request.POST.get('email', None),
                   first_name = request.POST.get('first_name', None),
                   last_name  = request.POST.get('last_name', None),
            )
        if is_new:
            # Just made a new user. Welcome aboard!
            user.set_password(raw_password)
            user.groups.add(auth.models.Group.objects.get(name="KaeruUsers"))
            user.save()
            cookie['signup_success'] = True
            cookie['user'] = user
            # log in
            auth.login(request, auth.authenticate(username=raw_username, password=raw_password))
            return render_to_response(url, cookie)
        else:
            # Existing user.
            cookie['duplicate_username'] = True
            return render_to_response(url, cookie)
    else:
        # Show the sign up page
        return render_to_response(url, cookie)

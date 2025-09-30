from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Country
from .forms import UserRegistrationForm, CustomUserForm


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.is_email_verified = True
            user.save()


            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Registration successful! Welcome, {username}!')
                return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()


    countries = Country.objects.all()

    return render(request, 'users/register.html', {
        'form': form,
        'countries': countries,
    })


@login_required
def profile(request):
    return render(request, 'users/profile.html', {
        'user': request.user,
        'countries': Country.objects.all(),
    })


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)


            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)

            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserForm(instance=request.user)

    return render(request, 'users/update_profile.html', {
        'form': form,
        'countries': Country.objects.all(),
    })
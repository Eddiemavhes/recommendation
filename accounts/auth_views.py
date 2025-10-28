from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm

def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please provide both username and password.')
            return render(request, 'accounts/login.html')
            
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}! You have successfully logged in.')
            
            # Redirect to next URL if provided, otherwise to dashboard
            next_url = request.GET.get('next')
            if next_url:
                messages.info(request, 'You were redirected to the page you tried to access.')
                return redirect(next_url)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
            
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You already have an account and are logged in.')
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, 'Account created successfully! Please log in with your credentials.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Registration failed. Please try again. Error: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegisterForm()
        
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def logout_view(request):
    if request.method == 'POST':
        username = request.user.username
        logout(request)
        messages.success(request, f'Goodbye {username}! You have been logged out successfully.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid logout request.')
        return redirect('dashboard')

@login_required
def password_change_view(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        if not all([old_password, new_password1, new_password2]):
            messages.error(request, 'Please fill in all password fields.')
            return render(request, 'accounts/password_change.html')
            
        if new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
            return render(request, 'accounts/password_change.html')
            
        user = request.user
        if not user.check_password(old_password):
            messages.error(request, 'Your old password was entered incorrectly.')
            return render(request, 'accounts/password_change.html')
            
        try:
            user.set_password(new_password1)
            user.save()
            login(request, user)  # Re-login the user with new password
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        except Exception as e:
            messages.error(request, f'Password change failed. Error: {str(e)}')
            
    return render(request, 'accounts/password_change.html')
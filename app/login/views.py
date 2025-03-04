from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required, user_passes_test
from . import forms
from .models import User  # Импортируем твою пользовательскую модель

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    users = User.objects.all()
    return render(request, 'admin_dashboard.html', {'users': users})

@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.all()  # Получаем всех пользователей
    return render(request, 'user_list.html', {'users': users})

@user_passes_test(is_admin)
def create_user(request):
    if request.method == 'POST':
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Используем метод save формы, он уже все делает
            messages.success(request, "Пользователь успешно создан!")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = forms.SignUpForm()
    return render(request, 'create_user.html', {'form': form})

@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = forms.EditUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Данные пользователя успешно обновлены!")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = forms.EditUserForm(instance=user)
    return render(request, 'edit_user.html', {'form': form, 'user': user})

@user_passes_test(is_admin)
def block_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    action = "разблокирован" if user.is_active else "заблокирован"
    messages.success(request, f"Пользователь {user.email} успешно {action}.") # Исправлено: используем email
    return redirect('admin_dashboard')

def user_login(request):
    if request.method == 'POST':
        form = forms.EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']  # Исправлено: используем email
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password) # Важно передать request

            if user is not None:
                login(request, user)
                messages.success(request, "Вы успешно авторизовались!")
                if user.is_superuser:
                    return redirect('user_page')
                return redirect('change_password')
            else:
                messages.error(request, "Неверный email или пароль. Пожалуйста, проверьте введенные данные.") # Исправлено: email
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = forms.EmailAuthenticationForm() # Не передаем request, он нужен только при POST
    return render(request, 'login.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Пароль успешно изменен!")
            return redirect('user_page')  # Замени на страницу пользователя, если она у тебя есть
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

def user_logout(request):
    """Выход пользователя из системы."""
    logout(request)
    messages.success(request, "Вы успешно вышли из системы.")
    return redirect('login')  # Предполагается, что 'login' - это имя URL для страницы входа


@login_required  # Требует авторизации для доступа к странице пользователя
def user_page(request):
    # Получаем текущего пользователя
    user = request.user
    
    # Передаем данные в контекст шаблона
    context = {
        'user': user,
        'full_name': f"{user.first_name} {user.last_name} {user.patronymic}" if user.patronymic else f"{user.first_name} {user.last_name}",
    }
    
    return render(request, 'user_page.html', context)


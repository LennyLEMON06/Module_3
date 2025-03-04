from django import forms
from .models import User  # Импортируем твою пользовательскую модель
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm  # <--- Import AuthenticationForm
from django.contrib.auth.password_validation import CommonPasswordValidator, MinimumLengthValidator, NumericPasswordValidator  # Import password validators

from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

class PasswordFieldWithValidators(forms.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, widget=forms.PasswordInput)

    def validate(self, value):
        super().validate(value)
        try:
            validate_password(value)  # Используем встроенную Django-проверку пароля
        except ValidationError as e:
            raise forms.ValidationError(e.messages)


class SignUpForm(UserCreationForm):
    """Форма регистрации пользователя."""

    email = forms.EmailField(required=True, label=_('Электронная почта'))  # Поле email обязательно
    password1 = PasswordFieldWithValidators(label=_('Пароль'))  # Добавляем валидаторы для основного пароля
    password2 = PasswordFieldWithValidators(label=_('Повторите пароль'))  # Валидаторы и для второго пароля

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')  # Добавляем пароли в форму

    def save(self, commit=True):
        """Сохраняет пользователя, используя email в качестве username."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']  # Задаем email
        user.username = self.cleaned_data['email'] # Используем email в качестве username
        if commit:
            user.save()
        return user

class EmailAuthenticationForm(AuthenticationForm):
    """Форма входа пользователя с использованием email."""

    email = forms.EmailField(label=_("Электронная почта"), max_length=254)
    password = forms.CharField(widget=forms.PasswordInput, label=_("Пароль"))

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        # Убираем поле username и меняем порядок полей
        del self.fields['username']
        self.fields['email'].widget.attrs.update({'autofocus': True})
        
    def clean(self):
        """Проверяет данные пользователя."""
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    _('Неверный логин или пароль. Пожалуйста, проверьте введенные данные.'),
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

class EditUserForm(forms.ModelForm):
    """Форма редактирования пользователя."""

    class Meta:
        model = User  # Используем твою модель User
        fields = [
            'email', 'first_name', 'last_name', 'patronymic', 'login', 'birthday',
            'phone_number', 'serial_passport', 'number_passport', 'address', 'gender',
            'is_staff', 'is_active', 'block', 'first_auth', 'role'
        ]  # Включаем все поля

        labels = {
            'email': _('Электронная почта'),
            'first_name': _('Имя'),
            'last_name': _('Фамилия'),
            'patronymic': _('Отчество'),
            'login': _('Логин'),
            'birthday': _('Дата рождения'),
            'phone_number': _('Номер телефона'),
            'serial_passport': _('Серия паспорта'),
            'number_passport': _('Номер паспорта'),
            'address': _('Адрес'),
            'gender': _('Пол'),
            'is_staff': _('Сотрудник'),
            'is_active': _('Активный'),
            'block': _('Заблокирован'),
            'first_auth': _('Первая аутентификация'),
            'role': _('Роль'),
        }


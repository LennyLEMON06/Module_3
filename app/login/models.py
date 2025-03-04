from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Менеджер для пользовательской модели User, где электронная почта является уникальным идентификатором для аутентификации,
    а не именем пользователя.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Создает и возвращает пользователя с указанным email и паролем.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Создает и возвращает суперпользователя с указанным email и паролем.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Пользовательская модель User."""

    email = models.EmailField(_('email address'), unique=True)  # Используем email как уникальный идентификатор
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    is_staff = models.BooleanField(default=False, verbose_name=_("Статус персонала"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активный"))
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    patronymic = models.CharField(max_length=255, verbose_name="Отчество", blank=True)
    login = models.CharField(max_length=255, verbose_name="Логин", blank=True) # Allow blank if not always required.
    birthday = models.DateField(verbose_name="Дата Рождения", null=True, blank=True)
    phone_number = models.CharField(max_length=255, verbose_name="Номер Телефона", blank=True)
    serial_passport = models.CharField(max_length=255, verbose_name="Серия Паспорта", blank=True)
    number_passport = models.CharField(max_length=255, verbose_name="Номер Паспорта", blank=True)
    block = models.BooleanField(default=False, verbose_name="Заблокирован")
    first_auth = models.BooleanField(default=False, verbose_name="Первая Аутентификация")
    role = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True, verbose_name="Роль", blank=True)  # Связь с Role.  Allow blank if not always required.
    address = models.CharField(max_length=255, verbose_name="Адрес", blank=True)
    gender = models.ForeignKey('Gender', on_delete=models.SET_NULL, null=True, verbose_name="Пол", blank=True) # Связь с Gender.  Allow blank if not always required.


    USERNAME_FIELD = 'email'  # Указываем, какое поле использовать для аутентификации
    REQUIRED_FIELDS = ['first_name', 'last_name'] #  Обязательные поля при создании суперпользователя

    objects = CustomUserManager()  # Используем наш пользовательский менеджер

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email #  Or a combination of fields like f"{self.first_name} {self.last_name} ({self.email})"


class CategoryRoom(models.Model):
    """Категория комнаты."""
    idcategory = models.AutoField(primary_key=True, verbose_name="ID Категории")
    categoryname = models.CharField(max_length=255, verbose_name="Название Категории")

    def __str__(self):
        return self.categoryname

    class Meta:
        verbose_name = "Категория Комнаты"
        verbose_name_plural = "Категории Комнат"


class StatusRoom(models.Model):
    """Статус комнаты (например, Доступна, Занята)."""
    idstatus = models.AutoField(primary_key=True, verbose_name="ID Статуса")
    statusname = models.CharField(max_length=255, verbose_name="Название Статуса")

    def __str__(self):
        return self.statusname

    class Meta:
        verbose_name = "Статус Комнаты"
        verbose_name_plural = "Статусы Комнат"


class Gender(models.Model):
    """Варианты пола для пользователей."""
    idgender = models.AutoField(primary_key=True, verbose_name="ID Пола")
    gendername = models.CharField(max_length=255, verbose_name="Пол")

    def __str__(self):
        return self.gendername

    class Meta:
        verbose_name = "Пол"
        verbose_name_plural = "Пол"


class Role(models.Model):
    """Роль для пользователя"""
    idrole = models.AutoField(primary_key=True, verbose_name="ID Роли")
    rolename = models.CharField(max_length=255, verbose_name="Название Роли")

    def __str__(self):
        return self.rolename

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"



class Room(models.Model):
    """Представляет комнату."""
    idroom = models.AutoField(primary_key=True, verbose_name="ID Комнаты")
    category = models.ForeignKey(CategoryRoom, on_delete=models.CASCADE, verbose_name="Категория")
    floor = models.IntegerField(verbose_name="Этаж")
    status = models.ForeignKey(StatusRoom, on_delete=models.SET_NULL, null=True, verbose_name="Статус")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость")
    description = models.CharField(max_length=255, blank=True, verbose_name="Описание")
    nameroom = models.CharField(max_length=255, verbose_name="Название Комнаты")

    def __str__(self):
        return f"Комната {self.nameroom}"

    class Meta:
        verbose_name = "Комната"
        verbose_name_plural = "Комнаты"


class ElementRoom(models.Model):
    """Элементы, присутствующие в комнате."""
    idelement = models.AutoField(primary_key=True, verbose_name="ID Элемента")
    elementname = models.CharField(max_length=255, verbose_name="Название Элемента")

    def __str__(self):
        return self.elementname

    class Meta:
        verbose_name = "Элемент Комнаты"
        verbose_name_plural = "Элементы Комнаты"


class EquipmentRoom(models.Model):
    """Промежуточная таблица для комнат и их элементов"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    element = models.ForeignKey(ElementRoom, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Оснащение Комнаты"
        verbose_name_plural = "Оснащение Комнат"
        unique_together = ('room', 'element')


class Service(models.Model):
    """Услуга, которую можно заказать"""
    idservice = models.AutoField(primary_key=True, verbose_name="ID Услуги")
    servicename = models.CharField(max_length=255, verbose_name="Название Услуги")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость")
    description = models.CharField(max_length=255, verbose_name="Описание", blank=True)

    def __str__(self):
        return self.servicename

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"


class Order(models.Model):
    """Представляет заказ."""
    idorder = models.AutoField(primary_key=True, verbose_name="ID Заказа")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="Комната")
    datestart = models.DateField(verbose_name="Дата начала")
    dateend = models.DateField(verbose_name="Дата окончания")
    sum = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    iscost = models.BooleanField(default=False, verbose_name="Учитывать Стоимость")
    client = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Клиент") # Связь с User

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderService(models.Model):
    """Промежуточная таблица для заказов и их услуг"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Услуга Заказа"
        verbose_name_plural = "Услуги Заказа"
        unique_together = ('order', 'service')
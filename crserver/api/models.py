from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from .manager import CustomUserManager


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractBaseUser, TimestampedModel):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email}"

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class CurrencyRate(TimestampedModel):
    currency_id = models.CharField(max_length=10)  # ID валюты
    num_code = models.CharField(max_length=3)  # код валюты
    char_code = models.CharField(max_length=5)  # Символьный код "AUD"
    nominal = models.PositiveIntegerField()  # Номинал валюты
    name = models.CharField(max_length=100)  # Название валюты
    value = models.DecimalField(max_digits=10, decimal_places=4)  # Значение котировки
    previous = models.DecimalField(max_digits=10, decimal_places=4)  # Предыдущее значение котировки
    date = models.DateField()  # Дата котировки

    def __str__(self):
        return f"{self.char_code} ({self.date})"

    class Meta:
        ordering = ['-id']


class UserCurrency(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ID на пользователя
    currency_id = models.CharField(max_length=10)  # ID котируемой валюты, "R01010"
    threshold = models.DecimalField(max_digits=10, decimal_places=4)  # Пз

    def __str__(self):
        return f"{self.user.email} отслеживает {self.currency_id} (Порог: {self.threshold})"

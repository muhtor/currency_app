from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.urls import reverse_lazy

from .models import User, CurrencyRate, UserCurrency

admin.site.unregister(Group)


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = "__all__"

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].help_text = ("<a href=\"%s\"><strong>Change the Password</strong></a>."
                                             ) % reverse_lazy('admin:auth_user_password_change',
                                                              args=[self.instance.id])

    def clean_password(self):
        return self.initial["password"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    filter_horizontal = ()
    list_display = ('id', 'email', 'is_staff', 'is_superuser',)
    list_filter = ('is_staff', 'is_superuser')
    search_fields = ('id', 'email')

    fieldsets = (
        (None, {
            'fields': (
                'email',
                'is_active',
                'is_staff',
                'is_superuser',
                'password',
            )
        }),
        ('Important dates', {'fields': ('last_login',)}),

    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'is_active',
                'is_staff',
                'is_superuser',
                'password1',
                'password2',
            )
        }),
        # ('Personal info', {'fields': ('groups',)}),
        # ('Permissions', {'fields': ('user_permissions',)}),
    )

    list_display_links = ('id', 'email')
    ordering = ('-id',)


@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
    list_display = ('id', 'currency_id', 'num_code', 'char_code', 'value', 'date')
    list_filter = ('date', )
    search_fields = ('char_code', 'name')


admin.site.register(UserCurrency)

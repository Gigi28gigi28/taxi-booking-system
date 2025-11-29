from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import Compte


# create user
class CompteCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    class Meta:
        model = Compte
        fields = ("email", "nom", "prenom", "role")

    def clean_password2(self):
        pw1 = self.cleaned_data.get("password1")
        pw2 = self.cleaned_data.get("password2")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Passwords do not match")
        return pw2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# update user 
class CompteChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Compte
        fields = ("email", "nom", "prenom", "role", "password",
                  "is_active", "is_staff", "is_superuser")


# admin user
class CompteAdmin(UserAdmin):
    add_form = CompteCreationForm
    form = CompteChangeForm
    model = Compte

    list_display = ("email", "nom", "prenom", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("nom", "prenom")}),
        ("Permissions",
         {"fields": ("role", "is_staff", "is_superuser", "is_active")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "nom", "prenom", "role", "password1", "password2"),
        }),
    )

    search_fields = ("email", "nom", "prenom")
    ordering = ("email",)
    filter_horizontal = ()


admin.site.register(Compte, CompteAdmin)

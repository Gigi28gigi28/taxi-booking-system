from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Compte
from django import forms

class CompteCreationForm(forms.ModelForm):
    class Meta:
        model = Compte
        fields = ('email','nom','prenom','role')

class CompteAdmin(UserAdmin):
    model = Compte
    add_form = CompteCreationForm
    list_display = ('email', 'nom', 'prenom', 'role', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'role')
    fieldsets = (
        (None, {'fields': ('email','password')}),
        ('Personal', {'fields': ('nom','prenom','role')}),
        ('Permissions', {'fields': ('is_staff','is_active','is_superuser','groups')}),
    )
    add_fieldsets = (
        (None, {
            'classes':('wide',),
            'fields': ('email','nom','prenom','role','password1','password2','is_staff','is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(Compte, CompteAdmin)

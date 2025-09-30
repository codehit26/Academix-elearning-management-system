from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Country, State, District

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_email_verified')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone', 'country', 'state', 'district',
                      'skype_id', 'whatsapp_number', 'is_email_verified')
        }),
    )

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'state')
    list_filter = ('state',)
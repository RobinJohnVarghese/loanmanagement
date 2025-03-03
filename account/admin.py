from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserAccount,OTP




@admin.register(UserAccount)
class CustomUserAdmin(UserAdmin):
    # Define the fields to display in the admin panel
    list_display = ('email','id', 'name', 'phone', 'description','is_active', 'is_staff')

    # Define the fields to filter by in the admin panel
    list_filter = ('is_active', 'is_staff')

    # Define the fieldsets for the add and change forms in the admin panel
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'phone', 'description',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff')}),
    )

    # Define the fieldsets for the add form in the admin panel
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','id', 'name','phone', 'description', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )

    # Set the ordering of objects in the admin panel
    ordering = ('is_staff','email',)


    # admin.site.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'otpCode', 'createdAt')
    list_display_links = ('id', 'user')

admin.site.register(OTP, OTPAdmin)
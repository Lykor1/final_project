from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(UserAdmin):
    model = User

    list_display = (
        'email',
        'first_name',
        'last_name',
        'role',
        'team'
    )
    search_fields = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'birthday')}),
        ('Work info', {'fields': ('role', 'team')}),
        ('Permission', {'fields': ('is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('created_at', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'first_name', 'last_name',
                'is_active'
            )
        }),
    )

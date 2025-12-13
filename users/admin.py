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
    ordering = ('email',)
    search_fields = ('email',)
    readonly_fields = ('created_at', 'last_login')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'birthday')}),
        ('Рабочая информация', {'fields': ('role', 'team')}),
        ('Права', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('created_at', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'first_name',
                'last_name',
                'is_active'
            )
        }),
    )

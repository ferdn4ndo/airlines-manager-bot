from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from api.models.user_model import CustomUser


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email',)


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    readonly_fields = ('id',)
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        'id',
        'email',
        'is_admin',
        'is_staff',
        'is_active',
        'registered_at',
        'last_activity_at',
    ]
    list_filter = [
        'id',
        'email',
        'is_admin',
        'is_staff',
        'is_active',
        'registered_at',
        'last_activity_at',
    ]
    fieldsets = [
        [
            None,
            {
                'fields': [
                    'email',
                ]
            }
        ],
        ['Permissions', {'fields': ['is_admin', 'is_staff', 'is_active']}],
    ]
    add_fieldsets = [
        [
            None,
            {
                'classes': ['wide'],
                'fields': ['email', 'password1', 'password2', 'is_admin', 'is_active']
            }
        ],
    ]
    search_fields = ['email']
    ordering = ['email']

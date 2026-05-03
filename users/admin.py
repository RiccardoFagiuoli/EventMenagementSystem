from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'date_created')
    list_filter = ('role', 'date_created')
    search_fields = ('user__username', 'user__email')
    fieldsets = (('User', {'fields': ('user',)}), ('Profile', {'fields': ('bio', 'profile_picture', 'phone_number', 'role')}))

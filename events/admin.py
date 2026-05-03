from django.contrib import admin
from .models import Event, EventRegistration, EventAttendance

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'start_date', 'status', 'location')
    list_filter = ('status', 'start_date', 'created_at')
    search_fields = ('title', 'description', 'location')
    fieldsets = (('Basic', {'fields': ('title', 'description', 'organizer')}), ('Details', {'fields': ('location', 'start_date', 'end_date', 'max_attendees')}), ('Media', {'fields': ('image',)}), ('Status', {'fields': ('status',)}))

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'status', 'registered_at')
    list_filter = ('status', 'registered_at')
    search_fields = ('user__username', 'event__title')
    readonly_fields = ('registered_at', 'updated_at')

@admin.register(EventAttendance)
class EventAttendanceAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'get_event', 'check_in_time')
    list_filter = ('check_in_time',)
    search_fields = ('registration__user__username', 'registration__event__title')
    readonly_fields = ('check_in_time',)
    def get_user(self, obj):
        return obj.registration.user
    get_user.short_description = 'User'
    def get_event(self, obj):
        return obj.registration.event
    get_event.short_description = 'Event'


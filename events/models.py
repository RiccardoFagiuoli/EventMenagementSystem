from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('published', 'Published'), ('ongoing', 'Ongoing'), ('completed', 'Completed'), ('cancelled', 'Cancelled')]
    title = models.CharField(max_length=200)
    description = models.TextField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    location = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    max_attendees = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-start_date']
        permissions = [('can_create_event', 'Can create events'), ('can_edit_own_events', 'Can edit own events'), ('can_delete_own_events', 'Can delete own events'), ('can_view_attendees', 'Can view attendees list')]
    def __str__(self):
        return self.title
    def is_full(self):
        if self.max_attendees is None:
            return False
        return self.eventregistration_set.filter(status='confirmed').count() >= self.max_attendees

class EventRegistration(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled'), ('attended', 'Attended')]
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('event', 'user')
        ordering = ['-registered_at']
    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.status})"

class EventAttendance(models.Model):
    registration = models.OneToOneField(EventRegistration, on_delete=models.CASCADE, related_name='attendance')
    check_in_time = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.registration.user.username} - {self.registration.event.title} (Attended)"

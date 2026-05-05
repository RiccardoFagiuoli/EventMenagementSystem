from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'start_date', 'end_date', 'max_attendees', 'image', 'status']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        n_attendees = cleaned_data.get('max_attendees')

        if n_attendees < 1:
            raise forms.ValidationError('Numero di partecipanti deve essere maggiore di 0')

        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError('La data e ora di inizio deve essere precedente alla data e ora di fine.')

        return cleaned_data

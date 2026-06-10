from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'start_date', 'end_date', 'max_attendees', 'image', 'status']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'max_attendees': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Aggiungi classe form-control ai campi testuali
        for field_name in ['title', 'description', 'location']:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

        # SOLO IN MODIFICA: popola i campi data con il formato corretto
        if self.instance and self.instance.pk:  # Evento esistente
            if self.instance.start_date:
                self.initial['start_date'] = self.instance.start_date.strftime('%Y-%m-%dT%H:%M')
            if self.instance.end_date:
                self.initial['end_date'] = self.instance.end_date.strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        n_attendees = cleaned_data.get('max_attendees')

        if n_attendees is not None and n_attendees < 0:
            raise forms.ValidationError(
                'Il numero di partecipanti deve essere maggiore di 0 o vuoto per posti illimitati')

        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError('La data e ora di inizio deve essere precedente alla data e ora di fine.')

        return cleaned_data

    # Validazione dimensione immagine (max 2 MB)
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 2 * 1024 * 1024:
                raise forms.ValidationError("L'immagine è troppo pesante (max 2MB).")
        return image

    def clean_start_date(self):
        """Converte la stringa del datetime-local in oggetto datetime"""
        start_date = self.cleaned_data.get('start_date')
        if start_date and isinstance(start_date, str):
            from datetime import datetime
            return datetime.fromisoformat(start_date)
        return start_date

    def clean_end_date(self):
        """Converte la stringa del datetime-local in oggetto datetime"""
        end_date = self.cleaned_data.get('end_date')
        if end_date and isinstance(end_date, str):
            from datetime import datetime
            return datetime.fromisoformat(end_date)
        return end_date
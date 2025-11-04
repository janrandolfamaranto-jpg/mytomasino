from django import forms
from .models import Ticket

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category']  
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your issue'}),
            'title': forms.TextInput(attrs={'placeholder': 'Ticket Title'}),
        }

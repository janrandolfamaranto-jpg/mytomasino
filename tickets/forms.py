from django import forms
from .models import Ticket

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category']

class TechnicalSupportForm(forms.ModelForm):
    ISSUE_CHOICES = [
        ('login', 'Login/Password Issue'),
        ('software', 'Software/System Error'),
        ('hardware', 'Device/Hardware Issue'),
        ('other', 'Other'),
    ]

    issue_type = forms.ChoiceField(choices=ISSUE_CHOICES, label="Issue Type")

    class Meta:
        model = Ticket
        fields = ['title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your issue'}),
            'title': forms.TextInput(attrs={'placeholder': 'Ticket Title'}),
        }
    
    def save(self, commit=True):
        ticket = super().save(commit=False)
        # Store issue_type in description or create a custom field
        issue_type = self.cleaned_data.get('issue_type')
        ticket.description = f"Issue Type: {dict(self.ISSUE_CHOICES)[issue_type]}\n\n{ticket.description}"
        if commit:
            ticket.save()
        return ticket

class AcademicSupportForm(forms.ModelForm):
    program_year = forms.CharField(
        max_length=50, 
        label="Program / Year Level",
        widget=forms.TextInput(attrs={'placeholder': 'Program / Year Level'})
    )
    
    INQUIRY_CHOICES = [
        ('enrollment','Enrollment / Registration'),
        ('grades','Grades / Transcript'),
        ('schedule','Schedule / Class Availability'),
        ('curriculum','Curriculum / Course Requirements'),
        ('other','Other')
    ]
    inquiry_type = forms.ChoiceField(choices=INQUIRY_CHOICES, label="Inquiry Type")
    
    question = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your question/issue'}), 
        label="Question / Issue"
    )

    class Meta:
        model = Ticket
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Ticket Title'}),
        }
    
    def save(self, commit=True):
        ticket = super().save(commit=False)
        program_year = self.cleaned_data.get('program_year')
        inquiry_type = self.cleaned_data.get('inquiry_type')
        question = self.cleaned_data.get('question')
        
        ticket.description = f"Program/Year: {program_year}\nInquiry Type: {dict(self.INQUIRY_CHOICES)[inquiry_type]}\n\n{question}"
        if commit:
            ticket.save()
        return ticket

class LostAndFoundForm(forms.ModelForm):
    DEPARTMENT_CHOICES = [
        ('jhs', 'JHS'),
        ('shs', 'SHS'),
        ('college', 'College'),
    ]
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, label="Department")
    
    item_description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe the item'}), 
        label="Item Description"
    )
    
    location = forms.CharField(
        max_length=100, 
        label="Location Last Seen / Found",
        widget=forms.TextInput(attrs={'placeholder': 'Location'})
    )
    
    date_time = forms.DateTimeField(
        label="Date / Time",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    
    photo = forms.FileField(required=False, label="Upload Photo (optional)")
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional notes'}), 
        required=False
    )

    class Meta:
        model = Ticket
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Item Name'}),
        }
    
    def save(self, commit=True):
        ticket = super().save(commit=False)
        department = self.cleaned_data.get('department')
        item_description = self.cleaned_data.get('item_description')
        location = self.cleaned_data.get('location')
        date_time = self.cleaned_data.get('date_time')
        notes = self.cleaned_data.get('notes', '')
        
        ticket.description = f"Department: {dict(self.DEPARTMENT_CHOICES)[department]}\n"
        ticket.description += f"Item: {item_description}\n"
        ticket.description += f"Location: {location}\n"
        ticket.description += f"Date/Time: {date_time.strftime('%Y-%m-%d %H:%M')}\n"
        if notes:
            ticket.description += f"Notes: {notes}"
        
        if commit:
            ticket.save()
        return ticket

class WelfareForm(forms.ModelForm):
    CONTACT_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('inperson', 'In-Person')
    ]
    contact_method = forms.ChoiceField(choices=CONTACT_CHOICES, label="Preferred Contact Method")
    
    REQUEST_CHOICES = [
        ('academic', 'Academic Stress / Guidance'),
        ('personal', 'Personal / Emotional Support'),
        ('mental', 'Mental Health Counselling'),
        ('peer', 'Peer / Conflict Mediation'),
        ('other', 'Other')
    ]
    request_type = forms.ChoiceField(choices=REQUEST_CHOICES, label="Request Type")
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Brief Description of Concern'}),
        label="Description"
    )
    
    preferred_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Preferred Meeting Date"
    )

    class Meta:
        model = Ticket
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Counseling Request Title'}),
        }
    
    def save(self, commit=True):
        ticket = super().save(commit=False)
        contact_method = self.cleaned_data.get('contact_method')
        request_type = self.cleaned_data.get('request_type')
        description = self.cleaned_data.get('description')
        preferred_date = self.cleaned_data.get('preferred_date')
        
        ticket.description = f"Contact Method: {dict(self.CONTACT_CHOICES)[contact_method]}\n"
        ticket.description += f"Request Type: {dict(self.REQUEST_CHOICES)[request_type]}\n"
        if preferred_date:
            ticket.description += f"Preferred Date: {preferred_date.strftime('%Y-%m-%d')}\n"
        ticket.description += f"\n{description}"
        
        if commit:
            ticket.save()
        return ticket

class FacilitiesForm(forms.ModelForm):
    ISSUE_CHOICES = [
        ('electrical', 'Electrical / Lighting'),
        ('plumbing', 'Plumbing / Water'),
        ('furniture', 'Furniture / Fixtures'),
        ('it', 'IT / AV Equipment'),
        ('safety', 'Safety / Security'),
        ('other', 'Other')
    ]
    
    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]
    
    location = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Location of the issue'}),
        label="Location"
    )
    
    issue_type = forms.ChoiceField(choices=ISSUE_CHOICES, label="Issue Type")
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the issue'}),
        label="Description"
    )
    
    photo = forms.FileField(required=False, label="Attach a Photo (optional)")
    
    urgency = forms.ChoiceField(choices=URGENCY_CHOICES, label="Urgency Level")

    class Meta:
        model = Ticket
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Issue Title'}),
        }
    
    def save(self, commit=True):
        ticket = super().save(commit=False)
        location = self.cleaned_data.get('location')
        issue_type = self.cleaned_data.get('issue_type')
        description = self.cleaned_data.get('description')
        urgency = self.cleaned_data.get('urgency')
        
        ticket.description = f"Location: {location}\n"
        ticket.description += f"Issue Type: {dict(self.ISSUE_CHOICES)[issue_type]}\n"
        ticket.description += f"Urgency: {dict(self.URGENCY_CHOICES)[urgency].upper()}\n\n"
        ticket.description += description
        
        if commit:
            ticket.save()
        return ticket
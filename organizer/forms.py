from django import forms
from . import models


class FAQForm(forms.ModelForm):
    question = forms.CharField(
        max_length=250,
        label= "Question:",
        required=True,
        widget=forms.TextInput(attrs={
            'class':'form-control',
            'placeholder': 'What is the name of your pet?',
        })
    )
    
    answer = forms.CharField(
        label="Answer:",
        required=True,
        widget=forms.Textarea(attrs={
            'class':'form-control',
            'placeholder': 'Lorem ipsum dolor...',
            'rows':4,
        })
    )
    
    class Meta:
        model = models.Faq
        fields = ['question', 'answer']
    
class AwardForm(forms.ModelForm):
    award_name = forms.CharField(
        max_length=150,
        required=True,
        label="Award Name:",
        widget=forms.TextInput(attrs={
            'class':'form-control',
            'placeholder': 'Spotlight Award',
        })
    )
    
    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(attrs={
            'class':'form-control',
            'placeholder':'Lorem ipsum dolor...',
            'rows':4,
        })
    )
    
    img = forms.FileField(
        required=True,
        label="Select award image:",
        widget=forms.ClearableFileInput(attrs={
            'class':'form-control',
            'accept':'image/*',
            'id':'id_award_img'
        })
    )
    
    class Meta:
        model = models.Awards
        fields = ['award_name', 'description', 'img']
    
class ProjectForm(forms.ModelForm):
    project_name = forms.CharField(
        max_length=150,
        required=True,
        label="Project Name:",
        widget=forms.TextInput(attrs={
            'class':'form-control',
            'placeholder': 'John & Doe Marriage',
        })
    )
    
    description = forms.CharField(
        label="Description:",
        widget=forms.Textarea(attrs={
            'class':'form-control',
            'placeholder':'Lorem ipsum dolor...',
            'rows':4,
        })
    )
    
    img = forms.FileField(
        required=True,
        label="Select project image:",
        widget=forms.ClearableFileInput(attrs={
            'class':'form-control',
            'accept':'image/*',
        })
    )
    
    class Meta:
        model = models.Project
        fields = ['project_name', 'description', 'img']
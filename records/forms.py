from django import forms

class EHRForm(forms.Form):
    name = forms.CharField(label='Name Of Medicial Record', max_length=256)
    data = forms.CharField(widget=forms.Textarea)

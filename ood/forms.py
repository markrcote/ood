from django import forms


class InstanceForm(forms.Form):
    port = forms.IntegerField(min_value=1)
    rcon_port = forms.IntegerField(min_value=1)
    rcon_password = forms.CharField(min_length=8)
    name = forms.CharField(min_length=1)
    region = forms.CharField(min_length=1)
    pkey = forms.CharField(min_length=1, widget=forms.Textarea)

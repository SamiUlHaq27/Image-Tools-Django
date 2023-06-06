from django import forms

class ImgForm(forms.Form):
    image = forms.ImageField()
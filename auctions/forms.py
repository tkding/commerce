from django import forms

from .models import Category

class ListingForm(forms.Form):
    title = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea)
    starting_bid = forms.DecimalField(max_digits=10, decimal_places=2)
    image_url = forms.URLField(required=False, empty_value=None)
    #category = forms.CharField(max_length=255, required=False, empty_value=None)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label="Select a categroy")
    
class BidForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    
class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
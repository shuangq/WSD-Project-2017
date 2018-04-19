from django import forms
from registration.forms import RegistrationForm
from shop.models import User
 
class SignupForm(RegistrationForm): 

    """Registration Form, extends django registration form to include more fields
    
    Fields:
        username : the username of the user
        first_name : first name of the user
        last_name : last name of the user
        email : email address, validated
        password1 : password, validated with restrictions
        password2 : password confirmation
        usergroup : group of the user: players of devs
    """
    
    CHOICES = (('players', 'Players',), ('devs', 'Developers')) 
    usergroup = forms.ChoiceField(widget=forms.Select, choices=CHOICES, required=True) 
    # first_name = forms.CharField(max_length=30, required=False, help_text='Optional.') 
    # last_name = forms.CharField(max_length=30, required=False, help_text='Optional.') 
 
    class Meta: 
        model = User 
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'usergroup') 
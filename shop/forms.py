from django import forms
from shop.models import Category
from shop.models import Game

class GameForm(forms.ModelForm):
    """Form for the creation and update of a game
    
    Fields:
    	category (set of strings): set of categories associated with the game
        description (string): a short description for the game
        difficulty (string): a string describing the difficulty
        game_name (string): the name of the game
        icon (image): the image of the game
        link (string): the link to the game, validated
        price (float): the price of the game
    """
    
    CHOICES = Category.objects.all().values_list('id', 'category')
    category = forms.MultipleChoiceField(choices=CHOICES, required=True)

    class Meta:
        model = Game
        fields = ('game_name', 'link', 'price', 'description', 'icon', 'difficulty', 'category')

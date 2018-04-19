import boto3
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

class Game(models.Model):

    """Game objects model
    
    Attributes:
        author (string): the author of the game, foreign key to User table
        description (string): a description for the game
        difficulty (string): a string describing the difficulty
        game_name (string): the name of the game
        icon (image): the image of the game
        link (string): the link to the game, validated
        price (float): the price of the game
    """
    
    def get_image_path(instance, filename):
        return os.path.join(settings.EXTERNAL_FILES,'game_icons', filename)

    game_name   = models.CharField(max_length=100,
                                   unique=True)
    author      = models.ForeignKey(User,
                                    on_delete=models.CASCADE,
                                    related_name="games")
    link        = models.URLField("url",
                                  blank=True)
    price       = models.FloatField(default=None,
                                    validators=[MinValueValidator(0)])
    description = models.TextField()
    icon        = models.ImageField(upload_to=os.path.join(settings.EXTERNAL_FILES,'game_icons'),
                                    blank=True,
                                    null=True,
                                    validators=[FileExtensionValidator(["jpg","jpeg","png","gif",])])
    difficulty  = models.CharField(max_length=20)

    def __str__(self):
        return 'Game: ' + self.game_name + ' by ' + self.author.username

    def getHighScore(self):
        """Returns the list of high scores for the 10 best users
        for the given game
        
        Returns:
            list: list of dict: each element is composed of
            username, position, highscore
        """
        rank_list = []
        try:
            scores_list = (Score.objects.all().filter(game=self.id)
                        .annotate(user_highscore=models.Max('score'))
                        .values_list('user__username', 'user_highscore')
                        .annotate(highscore=models.Max('score'))
                        .order_by('-highscore')
                        #.annotate(rank=Count('highscore', filters=Q(highscore__gt=highscore)))
                        .values_list('user__username', 'highscore')
                    )
            count = 1
            position = count
            for i, s in enumerate(scores_list):
                score = s[1]
                if i > 0 and score != scores_list[i - 1][1]:
                    position = count
                count = count + 1

                rank_list.append({
                    'username': s[0],
                    'position': position,
                    'highscore': s[1]
                })
            return rank_list
        except Exception as e:
            return None


    def getCategories(self):
        """Returns a Queryset of categories associated to the given game
        """
        return GamesCategory.objects.select_related('category').all().filter(game_id=self.id)

    def getUserHighScore(self, user_id):
        """Returns the top score for a user for the given game
        
        Args:
            user_id (integer): the id of the user
        
        Returns:
            Score: the best score achieved by the user
        """
        try:
            highscore = Score.objects.filter(user=user_id, game=self.id).order_by('-score').first()
            return highscore
        except:
            return None


    def getUserRank(self, user_id):
        """Returns the position of the user in the ranking for the given game
        
        Args:
            user_id (integer): the id of the user
        
        Returns:
            integer: the ranking of the user
        """
        highscore = self.getUserHighScore(user_id)

        if highscore:
            position = (Score.objects.all().filter(game=self.id)
                        .annotate(user_highscore=models.Max('score'))
                        .values_list('user__username', 'user_highscore')
                        .annotate(highscore=models.Max('score'))
                        .order_by('-highscore')
                        .filter(highscore__gt=highscore.score)
                        .count()
                    ) + 1
            return position
        else:
            return -1

    def getUserHistory(self, user_id):
        """Returns the last 10 scores for a user for the given game
        
        Args:
            user_id (integer): the id of the user
        
        Returns:
            Queryset: a list of Score objects with the 10 last scores of the user
        """
        try:
            history = Score.objects.filter(user=user_id, game=self.id).order_by('-date')[:10]
            return history
        except:
            return None

    def addIcon(self, icon):
        """Associates the icon to the Game object and uploads it to AWS S3
        
        Args:
            icon (image): the image of the game
        
        Raises:
            Exception: if the parameter file does not have a valid image extension
        """
        ext = os.path.splitext(str(icon))[1]
        if ext in [".jpg",".jpeg",".png",".gif",]:
            name = slugify(self.game_name) + str(timezone.now().timestamp()) + os.path.splitext(str(icon))[1]
            s3 = boto3.resource('s3')
            s3.Bucket('panda-shop').put_object(Key=f'external_files/game_icons/{name}', Body=icon)
            self.icon = name
        else:
            raise Exception(f'invalid extension: \"{ext}\"')


class State(models.Model):
    """State objects model
    
    Attributes:
        game (id): the id of the game, foreign key on Game object
        state (string): the saved state for th pair game-user
        user (id): the user who saved the state, foreign key on User object
    """
    
    user  = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              related_name="states")
    state = models.TextField()
    game  = models.ForeignKey(Game,
                              on_delete=models.CASCADE,
                              related_name="states")

    def __str__(self):
        return 'State: ' + self.user.username + ' in ' + self.game.game_name

    class Meta:
        unique_together = ('user', 'game',)


class Score(models.Model):
    """Score object
    
    Attributes:
        date (datetime): the date of the score
        game (id): the id of the game, foreign key on Game object
        score (float): the score for the game-user pair
        user (id): the user who saved the state, foreign key on User object
    """
    
    user  = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              related_name="scores")
    game  = models.ForeignKey(Game,
                              on_delete=models.CASCADE,
                              related_name="scores")
    score = models.FloatField(default=None)
    date  = models.DateTimeField()

    def __str__(self):
        return 'Score: ' + self.user.username + ' in ' + self.game.game_name


class Category(models.Model):
    """Category objects model
    
    Attributes:
        category (string): the category
    """
    
    category = models.CharField(max_length=50,
                                unique=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return 'Category: ' + self.category


class GamesCategory(models.Model):

    """Game-Category many-to-many relation
    
    Attributes:
        category (id): the id of the category object, foreign key on Category
        game (id): the id of the game object, foreign key on Game
    """
    
    game     = models.ForeignKey(Game,
                                 on_delete=models.CASCADE,
                                 related_name="gamesCategories")
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 related_name="gamesCategories")

    class Meta:
        verbose_name_plural = "game categories"
        unique_together = ('game', 'category',)

    def __str__(self):
        return 'Game Category: ' + self.game.game_name + ': ' + self.category.category


class Purchase(models.Model):

    """User purchase of a game
    
    Attributes:
        game (id): game purchased by a user, foreign key on Game
        purchase_date (datetime): date of the purchase
        purchase_user (id): id of the user, foreign key on User
    """
    
    purchase_user = models.ForeignKey(User,
                                      on_delete=models.CASCADE,
                                      related_name="purchases")
    game          = models.ForeignKey(Game,
                                      on_delete=models.CASCADE,
                                      related_name="purchases")
    purchase_date = models.DateField()

    def __str__(self):
        return 'Purchase: ' + self.game.game_name + ' by ' + self.purchase_user.username

    class Meta:
        unique_together = ('purchase_user', 'game',)

    def checkPurchase(game_id, user_id):
        """checks if the user has bought a game in the past
        
        Args:
            game_id (id): the id of the game
            user_id (id ): the id of the user
        
        Returns:
            Purchase of Bool: the purchase object if the user has purchased the game, False otherwise
        """
        try:
            return Purchase.objects.get(purchase_user=user_id, game=game_id)
        except:
            return False

    def countPurchases(dev_id):
        """Returns the number of purchases for each game developed by a given author
        
        Args:
            dev_id (id): the id of the game author
        
        Returns:
            list: list of dict with the name of the game and the number of sells
        
        Raises:
            Exception: Possible query exceptions
        """
        try:
            return (Purchase.objects.filter(game__author=dev_id)
                                    .select_related('game')
                                    .values('game__game_name')
                                    .annotate(sells=models.Count('game')))
        except:
            return None

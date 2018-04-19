import json
import requests

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import models
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from shop.models import Category, Game, GamesCategory, Purchase, Score, State



class GameModelTests(TestCase):
  #test type

  def setUp(self):
    call_command("loaddata", 'data.json',verbosity=0)

  def _test_field_type(self, model, modelname, fieldname, type):
    try:
      field = model._meta.get_field(fieldname)
      self.assertTrue(isinstance(field, type), "Testing the type of %s field in model %s"%(fieldname, modelname))
    except models.fields.FieldDoesNotExist:
      self.assertTrue(False, "Testing if field %s exists in model %s"%(fieldname, modelname))
    return field

  def test_game_name(self):
    game_name = self._test_field_type(Game, 'Game', 'game_name', models.CharField)
    self.assertEquals(game_name.max_length, 100, "Testing the max_length of title field")
    self.assertTrue(game_name.unique, "Testing if title is set to unique")

  def test_game_difficulty(self):
    game_difficulty = self._test_field_type(Game, 'Game', 'difficulty', models.CharField)
    self.assertEquals(game_difficulty.max_length, 20, "Testing the max_length of title field")

  def test_game_price(self):
    game_price = self._test_field_type(Game, 'Game', 'price', models.FloatField)
    self.assertEquals(game_price.default, None, "Testing that price has default value set to 0")

  def test_game_link(self):
    game_link = self._test_field_type(Game, 'Game', 'link', models.URLField)
    self.assertTrue(game_link.blank, "Testing that image_url can be blank")

  def test_game_icon(self):
    game_icon=self._test_field_type(Game, 'Game', 'icon', models.ImageField)
    self.assertTrue(game_icon.blank, "Testing that image_url can be blank")
    self.assertTrue(game_icon.null, "Testing that image_url can be blank")

  def test_game_description(self):
    self._test_field_type(Game, 'Game', 'description', models.TextField)

  def test_game_state(self):
    self._test_field_type(State, 'State', 'state', models.TextField)

  def test_game_score(self):
    game_score=self._test_field_type(Score, 'Score', 'score', models.FloatField)
    self.assertEquals(game_score.default, None, "Testing that price has default value set to 0")

  def test_game_date(self):
    self._test_field_type(Score, 'Score', 'date', models.DateField)

  def test_game_category(self):
    game_category = self._test_field_type(Category, 'Category', 'category', models.CharField)
    self.assertEquals(game_category.max_length, 50, "Testing the max_length of title field")

  def test_game_purchase(self):
    self._test_field_type(Purchase, 'Purchase', 'purchase_date', models.DateField)

  #test creating
  def testCreatingUser(self):
    testuser = User.objects.create(username="user1", email='user1@aa.com', password='12345678U')
    self.assertEqual(testuser.username, 'user1', "Getting a just created user")

  def testCreatingcategory(self):
    testcategory = Category.objects.create(category='sports_game')
    self.assertEqual(testcategory.category, 'sports_game', "Getting a just created category")

  def testCreatingscore(self):
    testscore = Score.objects.create(user_id=9,game_id=9,date=timezone.now(),score=89)
    self.assertEqual(testscore.score, 89, "Getting a just created score")

  def testCreatinggame(self):
    testgame = Game.objects.create(author_id=5,game_name='lalal',link='www.google.com',description='1990-04-09',price=89,difficulty='hard')
    self.assertEqual(testgame.price, 89, "Getting a just created score")

  def testCreatingstate(self):
    teststate = State.objects.create(user_id=8,state='lalal',game_id=89)
    self.assertEqual(teststate.state, 'lalal', "Getting a just state")

  def testCreatingpurchase(self):
    testpurchase = Purchase.objects.create(game_id=8,purchase_user_id=9,purchase_date=timezone.now())
    self.assertEqual(testpurchase.purchase_user_id, 9, "Getting a just purchase")

  def testCreatingGamesCategory(self):
    testGamesCategory = GamesCategory.objects.create(game_id=8,category_id=2)
    self.assertEqual(testGamesCategory.category_id, 2, "Getting a just purchase")

  #foreign key test
  def testgamecategoryThroughcategory(self):
    category1 = Category.objects.get(id=3)
    gamescategory1 = category1.gamesCategories.filter(category=3).first()
    self.assertEqual(gamescategory1.category_id, 3, "Getting a gamecategory from a category")

  # query test
  def testGetHighscore(self):
      game = Game.objects.get(id=4)
      highscore = game.getHighScore()[0]
      expectHighscore = {'username': 'marco', 'position': 1, 'highscore':80.0}
      self.assertEqual(highscore, expectHighscore, 'Getting the top highscore from a game')

      # get highscore of a game which has no highscore...
      game2 = Game.objects.get(id=2)
      highscore2 = game2.getHighScore()
      self.assertEqual(highscore2, [], 'Getting highscore from a game with no highscore')

  def testGetCategories(self):
      game = Game.objects.get(id=2)
      cat = set(map(lambda c: c.category.category, game.getCategories()))
      expectCat = set(['puzzle', 'point and click'])
      self.assertEqual(cat, expectCat, 'Getting categories of a game')


  def testGetUserHighScore(self):
      game = Game.objects.get(id=4)
      highscore = game.getUserHighScore(user_id=1).score
      expectHighscore = 80.0
      self.assertEqual(highscore, expectHighscore, 'Getting the highscore of a user in a game')

      # if user doesn't exist...
      highscore2 = game.getUserHighScore(user_id='panda')
      self.assertEqual(highscore2, None, 'Getting the highscore of an unexisting user in a game')

      # if user has never played the game...
      highscore3 = game.getUserHighScore(user_id=3)
      self.assertEqual(highscore3, None, 'Getting the highscore of a user who has never played the game')


  def testGetUserRank(self):
      game = Game.objects.get(id=4)
      rank = game.getUserRank(user_id=1)
      expectRank = 1
      self.assertEqual(rank, expectRank, 'Getting the rank of a user in a game')

      # if user doesn't exist...
      rank2 = game.getUserRank(user_id='panda')
      self.assertEqual(rank2, -1, 'Getting the rank of an unexisting user in a game')

      # if user has never played the game...
      rank3 = game.getUserRank(user_id=3)
      self.assertEqual(rank3, -1, 'Getting the rank of a user who has never played the game')


  def testGetUserHistory(self):
      game = Game.objects.get(id=4)
      history = game.getUserHistory(user_id=1)[0]
      self.assertEqual(history.score, 30.0, 'Getting the history of a user in a game')

      # if user doesn't exist...
      history2 = game.getUserHistory(user_id='panda')
      self.assertEqual(history2, None, 'Getting the history of an unexisting user in a game')

      # if user has never played the game...
      history3 = list(game.getUserHistory(user_id=3)) # the function will return an empty query set
      self.assertEqual(history3, [], 'Getting the history of a user who has never played the game')


  def testCheckPurchase(self):
      # puchased
      purchase = Purchase.checkPurchase(game_id=4, user_id=1)
      self.assertEqual(purchase.purchase_user.id, 1, 'Checking if a user has purchased a game')

      # not purchased
      purchase2 = Purchase.checkPurchase(game_id=4, user_id=3)
      self.assertEqual(purchase2, False, 'Checking if a user has purchased a game')

      # user doesn't exist
      purchase3 = Purchase.checkPurchase(game_id=4, user_id=222)
      self.assertEqual(purchase3, False, 'Checking if a user has purchased a game')

      # game doesn't exist
      purchase4 = Purchase.checkPurchase(game_id=222, user_id=1)
      self.assertEqual(purchase4, False, 'Checking if a user has purchased a game')

  def testCountPurchases(self):
      purchase = Purchase.countPurchases(dev_id=1)
      self.assertEqual(purchase[0]['sells'], 2, 'Getting the purchase number of a developer')
      # dev doesn't exist (return an empty queryset)
      purchase2 = Purchase.countPurchases(dev_id=2222)
      self.assertEqual(list(purchase2), [], 'Getting the purchase number of a developer')
      # invalid input
      purchase3 = Purchase.countPurchases(dev_id='panda')
      self.assertEqual(purchase3, None, 'Getting the purchase number of a developer')


class RestTests(TestCase):
  client_id     = 'FeN6EbF9HLq4rV9IWCRfHrzKqYHzSL2KSvxvKZez'
  client_secret = 'TC7vtcK1Ul4sKauhDr5SC33itdARrQuXFAUpsXSVOZu9JWVZ9mvGiq1j3mqPZpml0j6eDMtE2tQcy2JRaezTSjPsgSVWNfrDRWsh72fl31GlSzSM7syEDO9mDh0qwnR9'
  grant_type    = 'password'
  username      = 'marco'
  password      = 'spamspam'

  def setUp(self):
    call_command("loaddata", 'data.json',verbosity=0)
    self.url = 'http://localhost:8000'


  def testIndex(self):
    client = Client()
    r = client.get(reverse('index'))
    self.assertEqual(r.status_code, 200, "Getting index.html")


  def testLoginDev(self):
    payload = {
      'client_id'     : self.client_id,
      'client_secret' : self.client_secret,
      'grant_type'    : self.grant_type,
      'username'      : 'marco',
      'password'      : 'spamspam',
    }
    r = requests.post(self.url+reverse('token'), data=payload)
    self.assertEqual(r.status_code, 200, "Getting an access token")
    content = json.loads(r.content)
    self.assertTrue('access_token' in content, "Reading the access_token for developer")
    h = {
      'Authorization': 'Bearer '+ content['access_token']
    }
    r = requests.get(self.url+reverse('profile'), headers=h)
    self.assertEqual(r.status_code, 200, "Getting the profile page")
    c = json.loads(r.content)
    self.assertTrue('user' in c, "Reading the user")
    return h


  def testLoginUser(self):
    payload = {
      'client_id'     : self.client_id,
      'client_secret' : self.client_secret,
      'grant_type'    : self.grant_type,
      'username'      : 'normal',
      'password'      : 'qazwsxedc123',
    }
    r = requests.post(self.url+reverse('token'), data=payload)
    self.assertEqual(r.status_code, 200, "Getting an access token for player")
    content = json.loads(r.content)
    self.assertTrue('access_token' in content, "Reading the access_token")
    h = {
      'Authorization': 'Bearer '+ content['access_token']
    }
    r = requests.get(self.url+reverse('profile'), headers=h)
    self.assertEqual(r.status_code, 200, "Getting the profile page")
    c = json.loads(r.content)
    self.assertTrue('user' in c, "Reading the user")
    return h


  def testAuthentication(self):
    r = requests.get(self.url+reverse('profile'))
    self.assertEqual(r.status_code, 403, "Trying to get profile without being authenticated")

    r = requests.get(self.url+reverse('profile'),headers=self.testLoginDev())
    self.assertEqual(r.status_code, 200, "Loading profile with authenticated user")


  def testAuthorization(self):
    h = self.testLoginDev()

    othergame = Game.objects.filter(author=8).first().id
    r = requests.get(self.url+reverse('edit_game',kwargs={'game_id':othergame}), headers=h, allow_redirects=False)
    self.assertEqual(r.status_code, 302, "Unauthorized modification of a game")
    files = {'icon': ('spam.png', open('WSDProject/static/img/error.png', 'rb'), 'image/png', {'Expires': '0'})}

    form ={
      'game_name'   : 'some name',
      'author'      : 1,
      'url'         : 'http://miniclip.com/',
      'price'       : 12.0,
      'description' : 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Omnis deserunt, eligendi ipsa pariatur esse dolore modi sequi ex inventore aliquam, fugiat culpa nesciunt fuga quia voluptas cumque voluptate, impedit vel!',
      'difficulty'  : 'yeees',
      'category'    : 1,
      'category'    : 5,
      'icon'        : 'spam.png',
      }
    r = requests.post(self.url+reverse('new_game'),
                                       data=form,
                                       files=files)
    self.assertEqual(r.status_code, 401, "Unauthorized creation of a game")

    r = requests.put(self.url+reverse('new_game'),
                                       data=form,
                                       files=files,
                                       headers=h)
    self.assertEqual(r.status_code, 200, "Authorized creation of a game")

    game_name = json.loads(r.content)['game_name']
    _id = json.loads(r.content)['id']
    r = requests.delete(self.url+reverse('delete_game',kwargs={'game_id':_id}),
                                       data={'game_name': game_name},
                                       headers=h)
    self.assertEqual(r.status_code, 200, "Authorized deletion of a game")


  def testLogout(self):
    r = requests.get(self.url+reverse('auth_logout'),
                                       headers=self.testLoginDev(),
                                       allow_redirects=False)
    self.assertEqual(r.status_code, 200, "Logging out")

    r = requests.post(self.url+reverse('invalidate_sessions'),
                                       headers=self.testLoginDev(),
                                       data={'client_id': self.client_id},
                                       allow_redirects=False)
    self.assertEqual(r.status_code, 204, "Invalidating all sessions")


  def testEditGame(self):
  	othergame = Game.objects.filter(author=8).first().id
  	r = requests.get(self.url+reverse('edit_game',kwargs={'game_id':othergame}), headers=self.testLoginDev(), allow_redirects=False)
  	self.assertEqual(r.status_code, 302, "Unauthorized modification of a game")
  	files = {'icon': ('spam.png', open('WSDProject/static/img/error.png', 'rb'), 'image/png', {'Expires': '0'})}
  	form ={
	'game_name'   : 'some name',
	'author'      : 1,
	'url'         : 'http://miniclip.com/',
	'price'       : 12.0,
	'description' : 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Omnis deserunt, eligendi ipsa pariatur esse dolore modi sequi ex inventore aliquam, fugiat culpa nesciunt fuga quia voluptas cumque voluptate, impedit vel!',
	'difficulty'  : 'yeees',
	'category'    : 1,
	'category'    : 5,
	'icon'        : 'spam.png',
	}



def testPurchaseData(self):
	r = requests.get(self.url+reverse('purchase_data'),
                                   headers=self.testLoginDev(),
                                   allow_redirects=False)
	self.assertEqual(r.status_code, 200, "Loading purchase_data with authenticated user")
	content = json.loads(r.content)
	self.assertTrue('sell' in content[0], "correct sell information")
	r = requests.get(self.url+reverse('purchase_data'))
	self.assertEqual(r.status_code, 403, "Trying to get purchase_data without being authenticated")


def testGameCom(self):
	payload = {'game_id': '5', 'purchase_user': 'marco'}
	r = requests.get(self.url+reverse('gamemessage'), params=payload)
	self.assertEqual(r.status_code, 200, "successful access")
	content = json.loads(r.content)
	self.assertTrue('messageType' in content, "correct response information")
	self.assertTrue('info' in content, "correct response information")
	payload = {'game_id': '5', 'purchase_user': 'mar'}
	r = requests.get(self.url+reverse('gamemessage'), params=payload)
	self.assertEqual(r.status_code, 403, "fail to access")


def testGameInfo(self):
	r = requests.get(self.url+reverse('gameinfo'),
	                               headers=self.testLoginDev(),
	                               allow_redirects=False)

	self.assertEqual(r.status_code, 200, "Loading gameinfo with authenticated user")
	content = json.loads(r.content)
	self.assertTrue('game' in content, "correct data information")
	self.assertTrue('categories' in content, "correct data information")
	self.assertTrue('scores_list' in content, "correct data information")
	self.assertTrue('user_status' in content, "correct data information")
	self.assertTrue('bill' in content, "correct data information")
	r = requests.get(self.url+reverse('gameinfo'))
	self.assertEqual(r.status_code, 403, "Trying to get gameinfo without being authenticated")


def testGamesList(self):
	payload = {'category': '1'}
	r = requests.get(self.url+reverse('gameslist'), params=payload)
	self.assertEqual(r.status_code, 200, "successful access")
	content = json.loads(r.content)
	self.assertTrue('games' in content, "correct response information")
	self.assertTrue('pages' in content, "correct response information")
	self.assertTrue('this_page' in content, "correct response information")
	payload = {'category': '20'}
	self.assertEqual(r.status_code, 403, "fail to access")

	payload = {'page': '1'}
	r = requests.get(self.url+reverse('gameslist'), params=payload)
	self.assertEqual(r.status_code, 200, "successful access")
	content = json.loads(r.content)
	self.assertTrue('games' in content, "correct response information")
	self.assertTrue('pages' in content, "correct response information")
	self.assertTrue('this_page' in content, "correct response information")
	payload = {'page': '20'}
	self.assertEqual(r.status_code, 403, "fail to access")

	payload = {'game_names': 'game_names'}
	r = requests.get(self.url+reverse('gameslist'), params=payload)
	self.assertEqual(r.status_code, 200, "successful access")
	content = json.loads(r.content)
	self.assertTrue('games' in content, "correct response information")
	self.assertTrue('pages' in content, "correct response information")
	self.assertTrue('this_page' in content, "correct response information")
	payload = {'game_names': 'lala20'}
	self.assertEqual(r.status_code, 403, "fail to access")


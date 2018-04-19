import json
import os
import requests

from PIL import Image
from datetime import date, datetime
from hashlib import md5
from itertools import groupby
from math import ceil
from operator import itemgetter

from authentication.authentication import BearerAuthentication
from shop import forms
from shop.models import Category, Game, GamesCategory, Purchase, Score, State

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission, User
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db import transaction
from django.db.models import Model
from django.db.models.fields.files import FileField, ImageFieldFile
from django.db.models.query import QuerySet
from django.db.utils import IntegrityError
from django.forms.models import model_to_dict
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from rest_framework import generics
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import authentication_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response


def isPC(request):
    """Checks whether the request is originated by 
    a browser interaction or by an ajax call

    Args:
        request (HTTPRequest): the request to check

    Returns:
        Bool: True if the request accepts html format as response
    """
    return request.accepted_renderer.format == 'html'


class Encoder(json.JSONEncoder):
    """
    JSON Encoder for objects
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, ImageFieldFile):
            return str(obj)
        if (isinstance(obj, Group) or
                isinstance(obj, Permission)):
            return str(obj)
        if isinstance(obj, Model):
            return model_to_dict(obj)
        if isinstance(obj, QuerySet):
            return list(obj)
        else:
            return json.JSONEncoder.default(self, obj)


def rest(d):
    """transforms objects, including Model instances in dictionary form

    Args:
        d (object): the object to transform

    Returns:
        dict: the object serialized in dictionary form
    """
    return json.loads(json.dumps(d, cls=Encoder))


class Index(generics.RetrieveAPIView):
    """
    A view that returns a templated HTML representation of index.html
    """
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request):
        """
        index view
        """
        limit = 12

        context = {
            'game_names': Game.objects.all().values('game_name'),
            'categories': Category.objects.all(),
            'pages': list(range(1, ceil(Game.objects.count() / limit) + 1)),
            'this_page': 1,
            'message': request.GET.get('message', None)
        }
        return Response(context, template_name='index.html')


class UserDetail(generics.RetrieveAPIView):
    """
    A view that returns a templated HTML representation of a given user or a JSON representing the user data
    """
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        User page
        """
        games = list(map(lambda x: x.game, Purchase.objects.select_related(
            'game').all().filter(purchase_user=request.user.id)))
        dev_games = Game.objects.filter(author=request.user.id)

        if request.accepted_renderer.format == 'html':
            data = {'games': games}
            for g in dev_games:
                try:
                    i = games.index(g)
                    games[i].dev = True
                except:
                    pass
            for g in games:
                g.developer = Game.objects.filter(pk=g.id).select_related(
                    'author').first().author.username
                g.n_purchases = Purchase.objects.filter(game_id=g.id).count()
            return Response(data, template_name='user.html')
        else:
            data = {'user': request.user,
                    'games': games,
                    'dev_games': dev_games,
                    }
            return Response(rest(data))


class NewGame(generics.CreateAPIView):
    """
    A view that returns a templated HTML representation of the form for adding new games
    """
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)
    authentication_classes = (BearerAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        New game form
        """
        if isPC(request):
            return Response({'form': forms.GameForm, 'button_text': 'Publish', 'select_text': 'Category'}, template_name='game_form.html')
        else:
            return Response(status=404)

    def post(self, request):
        if isPC(request):
            return self.put(request)
        else:
            return Response(status=404)

    def put(self, request):
        """
        New game content processing
        """
        form = forms.GameForm(request.POST)
        if form.is_valid():
            game = form.save(commit=False)
            game.author_id = request.user.id
            try:
                game.addIcon(request.FILES['icon'])
            except:
                pass
            with transaction.atomic():
                game.save()
                Purchase(purchase_user=request.user,
                         game=game,
                         purchase_date=datetime.now()
                         ).save()
                for c in request.POST.getlist('category'):
                    GamesCategory(category_id=c, game=game).save()
            if isPC(request):
                return redirect('gameinfo', game_id=game.id)
            else:
                return Response(rest(game))
        else:
            if isPC(request):
                return Response({'form': form, 'button_text': 'Publish', 'select_text': 'Category'}, template_name='game_form.html')
            else:
                return Response(form.errors.as_json())


class EditGame(generics.UpdateAPIView):
    """
    A view that returns a templated HTML representation of the form for editing new games
    """
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)
    authentication_classes = (BearerAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, game_id):
        """
        Edit game form
        """
        try:
            game = Game.objects.get(pk=game_id)
            # Check authority
            if game.author.id is not request.user.id:
                message = 'Unauthorized request. What are you trying to do? Panda is not amused.'
                return redirect(f'/?message={message}')

            categories = list(
                game.getCategories().values_list('category', flat=True))
            form = forms.GameForm(instance=game, initial={
                                  'category': categories})

            if isPC(request):
                return Response({'form': form, 'button_text': 'Update', 'select_text': 'Category'}, template_name='game_form.html')
            else:
                return Response(status=404)

        except Exception as e:
            message = str(e)
            if isPC(request):
                return redirect(f'/?message={message}')
            else:
                return Response({'message': message}, status=403)

    def post(self, request, game_id):
        """
        Edit game content processing
        """
        try:
            game = Game.objects.get(pk=game_id)
            # Check authority
            if game.author.id is not request.user.id:
                message = 'Unauthorized request. What are you trying to do? Panda is not amused.'
                return redirect(f'/?message={message}')

            categories = list(
                game.getCategories().values_list('id', flat=True))
            # Pass instance to the modelform so that it updates the existing instance instead of saving a new one
            form = forms.GameForm(request.POST, instance=game, initial={
                                  'category': categories})
            if form.is_valid():
                new_game = form.save(commit=False)
                try:
                    game.addIcon(request.FILES['icon'])
                except:
                    pass
                with transaction.atomic():
                    new_game.save()
                    GamesCategory.objects.filter(game=game).delete()
                    for c in request.POST.getlist('category'):
                        GamesCategory(category_id=c, game=game).save()
                if isPC(request):
                    return redirect('gameinfo', game_id=game.id)
                else:
                    return Response(rest(new_game))

            else:
                if isPC(request):
                    return Response({'form': form, 'button_text': 'Update', 'select_text': 'Category'}, template_name='game_form.html')
                else:
                    return Response(form.errors.as_json())

        except Exception as e:
            message = str(e)
            if isPC(request):
                return redirect(f'/?message={message}')
            else:
                return Response({'message': message}, status=403)


class DeleteGame(generics.DestroyAPIView):
    """
    A view that returns a templated HTML representation of the form for deleting a game
    """
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)
    authentication_classes = (BearerAuthentication, SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, game_id):
        if isPC(request):
            return self.delete(request, game_id)
        else:
            return Response(status=404)

    def delete(self, request, game_id):
        """
        Delete game
        """
        try:
            game = Game.objects.get(pk=game_id)

            # Check authority
            if game.author.id is not request.user.id:
                message = 'Unauthorized request. What are you trying to do? Panda is not amused.'
                if isPC(request):
                    return redirect(f'/?message={message}')
                else:
                    return Response({'message': message}, status=403)

            # Check form parameter
            game_name = request.POST.get("game_name", "")
            if game_name != game.game_name:
                message = 'Game name does not match.'
                if isPC(request):
                    return redirect('gameinfo', game_id=game_id)
                else:
                    return Response({'message': message}, status=403)

            with transaction.atomic():
                game.delete()
                GamesCategory.objects.filter(game=game).delete()
            return redirect('profile')
            if isPC(request):
                return redirect('profile')
            else:
                return Response(rest(game), status=403)

        except Exception as e:
            message = str(e)
            if isPC(request):
                return redirect(f'/?message={message}')
            else:
                return Response({'message': message}, status=403)


class GameInfo(generics.RetrieveAPIView):
    """
    A view that returns a templated HTML representation of the game information
    """
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)
    authentication_classes = (BearerAuthentication, SessionAuthentication)

    def get(self, request, game_id):
        """
        Returns the info for a game, including info on the user that
        created the request and purchase link if the user did not
        purchase the game
        """
        try:
            game = Game.objects.get(pk=game_id)
            categories = game.getCategories()
            scores = game.getHighScore()

            # check if user has login & usergroup
            if_login = request.user.is_authenticated
            if_dev = if_login and request.user.id is game.author.id
            if_purchase = if_login and Purchase.checkPurchase(
                game_id, request.user.id)

            highscore = None
            rank = None
            history = None
            bill = None

            if if_purchase:
                highscore = game.getUserHighScore(request.user.id)
                rank = game.getUserRank(request.user.id)
                history = game.getUserHistory(request.user.id)
            elif if_login:
                try:
                    sid = "pandashop"
                    pid = str(game.id) + "!" + str(request.user.id)

                    secret_key = "583e35f04573f59158691b6e21f869dc"
                    checksumstr = "pid={}&sid={}&amount={}&token={}".format(
                        pid, sid, game.price, secret_key)
                    m = md5(checksumstr.encode("ascii"))

                    bill = {
                        'pid': pid,
                        'sid': sid,
                        'checksum': m.hexdigest(),
                    }

                except (TypeError, NameError) as e:
                    if isPC(request):
                        return Response({'message': str(e)}, template_name='gameinfo.html')
                    else:
                        return Response(rest({'message': str(e)}), status=403)

            user_status = {
                'if_dev': if_dev,
                'if_purchase': if_purchase,
                'record': {
                    'highscore': highscore,
                    'rank': rank,
                    'history': history
                }
            }

            data = {
                'game': game,
                'categories': categories,
                'scores_list': scores,
                'user_status': user_status,
                'bill': bill
            }

        except Game.DoesNotExist:
            data = None
        if isPC(request):
            return Response(data, template_name='gameinfo.html')
        else:
            data = {
                'game': game,
                'categories': categories,
                'scores_list': scores,
                'user_status': user_status,
            }
            print(data)
            return Response(rest(data))

        if isPC(request):
            return Response(data, template_name='gameinfo.html')
        else:
            data = {
                'game': game,
                'categories': categories,
                'scores_list': scores,
                'user_status': user_status,
            }
            return Response(rest(data))


class GamesList(generics.RetrieveAPIView):
    """
    A rest api that returns a list of games according to the category and name search
    """
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)

    def get(self, request):
        """
        Returns the list of games according to some parameters

        Parameters:
            category (string): the category to filter the games
            search (string): a string to use as search substring
            page (integer): the offset of the page for the query
        """
        try:
            query = GamesCategory.objects
            limit = 12

            # category filter
            category = request.GET.get('category', None)
            if category:
                query = query.filter(category=category)

            games_categories = query.select_related('game')
            games = set(map(lambda x: x.game, games_categories))

            # name search
            q = request.GET.get('search', None)
            if q:
                games = Game.objects.filter(game_name__icontains=q)

            # offset
            page = int(request.GET.get('page', 1))
            # page = page if page > 0 else 1

            games = list(map(lambda x: model_to_dict(x), games))

            for g in games:
                g['author'] = Game.objects.filter(pk=g['id']).select_related(
                    'author').first().author.username
                g['n_purchases'] = Purchase.objects.filter(
                    game_id=g['id']).count()

            data = {
                'games': games[(page - 1) * limit:page * limit],
                'pages': list(range(1, ceil(len(games) / limit) + 1)),
                'this_page': page,
            }
        except Exception as e:
            data = {'message': str(e)}

        return Response(rest(data))


class ResultPay(generics.RetrieveAPIView):
    """
    A rest api that purchase the game
    """
    renderer_classes = (TemplateHTMLRenderer,)
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Returns the view corresponding to the result of the payment
        """

        try:
            pid = request.GET['pid']
            game_id = int((pid.split('!'))[0])
            game = Game.objects.get(pk=game_id)

            ref = request.GET['ref']
            result = request.GET['result']
            secret_key = "583e35f04573f59158691b6e21f869dc"
            checksum = request.GET['checksum']

            checksumstr1 = "pid={}&ref={}&result={}&token={}".format(
                pid, ref, result, secret_key)
            m = md5(checksumstr1.encode("ascii"))
            checksum_check = m.hexdigest()

        except (TypeError, NameError):
            raise Http404("There are some errors, values are missing")

        if checksum == checksum_check:
            if result not in ["success", "cancel", "error"]:
                return HttpResponse(content="error")

            if result == "success":
                Purchase(purchase_user=request.user, game=game,
                         purchase_date=datetime.now()).save()
                return HttpResponseRedirect(reverse('gameinfo', args=(game_id,)))

            elif result == "cancel":
                return HttpResponseRedirect(reverse('gameinfo', args=(game_id,)))

            elif result == "error":
                return render(request, "error.html", {'game': game})

            else:
                return render(request, "error.html", {'game': game})

        else:
            return render(request, "data_no_match.html", {'game': game})


class PlayGame(generics.RetrieveAPIView):
    """
    A view that returns a templated HTML representation of the game playing page
    """
    renderer_classes = (TemplateHTMLRenderer,)
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, game_id):
        """
        View with the iframe for playing the game
        """
        if not Purchase.objects.filter(game_id=game_id, purchase_user=request.user):
            message = 'Unauthorized request. What are you trying to do? Panda is not amused.'
            return redirect(f'/?message={message}')
        else:
            return Response({'game': Game.objects.get(pk=game_id)}, template_name='game.html')


class GameCom(generics.GenericAPIView):
    """
    Endpoint for game communication (SAVE/SCORE/LOAD)
    """
    renderer_classes = (JSONRenderer,)
    authentication_classes = (SessionAuthentication, BearerAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, game_id):
        """
        Communication function between the game and the service

        messages:
            SAVE: saves the state of the game in the database, overwriting the previous one
            SCORE: saves a high score for a user
            LOAD_REQUEST: queries the database for a previously saved state
        """
        if not Purchase.objects.filter(game_id=game_id, purchase_user=request.user):
            message = 'Unauthorized request. What are you trying to do? Panda is not amused.'
            return redirect(f'/?message={message}')
        else:
            mtype = request.GET.get('messageType', None)
            try:
                game = Game.objects.get(pk=game_id)
            except ObjectDoesNotExist as e:
                response = {
                    'messageType': 'ERROR',
                    'info': str(e)
                }
                return Response(rest(response))
            if mtype:
                if mtype == 'SAVE':
                    state = json.loads(request.GET.get('gameState', None))
                    s = State(user=request.user, game=game, state=state)
                    try:
                        s.save()
                    except IntegrityError as e:
                        s = State.objects.get(user=request.user, game=game)
                        s.state = state
                        s.save()
                    response = {'info': 'State Saved'}
                if mtype == 'SCORE':
                    score = json.loads(request.GET.get('score', None))
                    Score(user=request.user, game=game,
                          score=score, date=timezone.now()).save()
                    response = {'info': 'Score Saved'}
                if mtype == 'LOAD_REQUEST':
                    try:
                        s = State.objects.filter(
                            user=request.user, game=game).last()
                        response = {
                            'messageType': 'LOAD',
                            'gameState': s.state
                        }
                    except Exception as e:
                        response = {
                            'messageType': 'ERROR',
                            'info': str(e)
                        }
            return Response(json.dumps(response))


class Share(generics.RetrieveAPIView):
    """
    A view that returns a templated HTML page for sharing highscore
    """
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request, score_id):
        """
        Simple view with the game highscore achieved by the user
        """
        try:
            score = Score.objects.select_related(
                'game', 'user').get(pk=score_id)

            data = {
                'username': score.user.username,
                'game': score.game,
                'score': score,
            }
        except Exception as e:
            # Otherwise, redirect to the home page
            message = str(e)
            return redirect(f'/?message={message}')

        return Response(data, template_name='share.html')


class PurchaseData(generics.RetrieveAPIView):
    """
    REST api that returns the sales data of a game for the developer
    """
    renderer_classes = (JSONRenderer,)
    authentication_classes = (SessionAuthentication, BearerAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Returns a list of sells for the user
        """
        if request.user.groups.get(name='devs'):
            dev_id = request.user.id
            sells = Purchase.countPurchases(dev_id)
            return Response(rest(list(sells)))
        else:
            message = 'Unauthorized request. What are you trying to do? Panda is not amused.'
            return Response({'message', message})

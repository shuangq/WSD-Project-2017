from . import views
from django.urls import re_path

urlpatterns = [
    # shop urls
    re_path(r'^$', views.Index.as_view(), name='index'),
    re_path(r'^game/(?P<game_id>\d+)/?$', views.GameInfo.as_view(), name='gameinfo'),
    re_path(r'^gameslist/?$', views.GamesList.as_view(), name='gameslist'),
    re_path(r'^play/(?P<game_id>\d+)/?$', views.PlayGame.as_view(), name='game'),
    re_path(r'^gamemessage/(?P<game_id>\d+)/?$', views.GameCom.as_view(), name='gamemessage'),
    re_path(r'^profile/?$', views.UserDetail.as_view(), name='profile'),
    re_path(r'^newgame/?$', views.NewGame.as_view(), name='new_game'),
    re_path(r'^editgame/(?P<game_id>\d+)/?$', views.EditGame.as_view(), name='edit_game'),
    re_path(r'^deletegame/(?P<game_id>\d+)/$', views.DeleteGame.as_view(), name='delete_game'),
    re_path(r'^purchasedata/?', views.PurchaseData.as_view(), name='purchase_data'),
    re_path(r'^share/(?P<score_id>\d+)/?$', views.Share.as_view(), name='share'),
    re_path(r'^resultpay/?$', views.ResultPay.as_view(), name='result_pay'),
]

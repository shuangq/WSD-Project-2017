from django.contrib import admin
from shop.models import *

# registers the models into the admin page
admin.site.register(Game)
admin.site.register(State)
admin.site.register(Score)
admin.site.register(Category)
admin.site.register(GamesCategory)
admin.site.register(Purchase)

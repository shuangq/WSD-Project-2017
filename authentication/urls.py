from authentication import views
from django.urls import include, re_path
from django.views.generic.base import RedirectView

urlpatterns = [
	# include external frameworks urls
    re_path(r'^auth/', include('rest_framework_social_oauth2.urls')),
    re_path(r'^', include('registration.backends.hmac.urls')),
    # custom registration page
    re_path(r'^register/$', views.Reg.as_view(), name='reg'),
    # profile page
    re_path(r'^profile', RedirectView.as_view(pattern_name='profile')),
    # pipeline view for social login (see authentication.pipeline.add_group)
    re_path(r'^askforgroup/(?P<backend>.+)', views.AskForGroup.as_view(), name='askforgroup'),
]

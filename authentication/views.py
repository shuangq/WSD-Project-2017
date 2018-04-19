from django.contrib.auth.models import Group
from django.db import transaction
from django.shortcuts import render

from authentication.forms import SignupForm
from registration.backends.hmac.views import RegistrationView

from django.shortcuts import redirect

from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response


class Reg(RegistrationView):

    """Custom registration view, uses SignupForm
    """
    
    def get(self, request):
        """Returns the form view to be filled in by the user
        """
        context={'form':SignupForm}
        return render(request, 'registration/registration_form.html', context=context)

    def post(self, request):
        """Reads the content of the filled in form and registers
        the user in the database if all the fields conform to a 
        valid user object, renders a new form with errors otherwise
        """
        form = SignupForm(request.POST)
        usergroup = request.POST.get('usergroup', 'players')

        if form.is_valid():
            group = Group.objects.get(name=usergroup)
            with transaction.atomic():
                new_user = self.register(form)
                group.user_set.add(new_user)
            return render(request, 'registration/registration_complete.html')
        else:
            return render(request, 'registration/registration_form.html', context={'form':form})

class AskForGroup(generics.GenericAPIView):
    """View used in the social authentication pipeline to associate
    a group to a user
    """
    
    renderer_classes = (TemplateHTMLRenderer,)
    def get(self, request, backend):
        return Response({}, template_name='askforgroup.html')

    def post(self, request, backend):
        request.session['group'] = request.POST.get('group','players')
        return redirect('social:complete', backend=backend)
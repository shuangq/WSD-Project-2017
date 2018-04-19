from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

class BearerAuthentication(TokenAuthentication):

    """Extends TokenAuthentication to work with oauth2 model
    
    Attributes:
        keyword (str): 'Bearer'
        model (Model): Access token model
    """
    
    keyword = 'Bearer'
    model   = None

    def get_model(self):
        """Returns the model used by the Token authorization
           This authentication method used oauth2_provider AccessToken model
        
        Returns:
            Model: AccessToken database model
        """
        if self.model is not None:
            return self.model
        from oauth2_provider.models import AccessToken
        return AccessToken

    def authenticate_credentials(self, key):
        """Authenticate the user through the access token provided 
        
        Args:
            key (str): Access token
        
        Returns:
            tuple: (user, token): user corresponding to the token and token
        
        Raises:
            exceptions.AuthenticationFailed: if the user is not authenticated
        """
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(token=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return (token.user, token)

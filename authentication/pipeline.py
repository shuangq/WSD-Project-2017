from django.contrib.auth.models import Group
from django.shortcuts import redirect
from social_core.pipeline.partial import partial

@partial
def add_group(strategy, user, is_new, backend, **kwargs):
    """Pipeline function user in the process of 
    registering a user through social network identification
    
    Args:
        **kwargs: all the parameters that the previous steps 
        of the pipeline created or pass through the next function
    
    Returns:
        **kwargs: pass through of the parameters to the next function
    """
    if is_new:
        if 'group' in kwargs['request'].session:
            group = Group.objects.get(name=strategy.session_get('group'))
            group.user_set.add(user)
            return(kwargs)
        else:
            return redirect('askforgroup', backend=backend.name)
    else:
        return(kwargs)
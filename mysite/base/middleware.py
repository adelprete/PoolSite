from django.shortcuts import redirect
from django.core.urlresolvers import reverse


class FinishProfile:
    """
        Middleware that checks if the user finished filling out their profile.
        If they go anywhere on the site they will be redirect tot he profile form.
    """
    def process_request(self,request):
        if not request.user.is_anonymous():
            if request.path != '/profile/' and request.path != '/accounts/logout/':
                if hasattr(request.user, "memberprofile"):
                    if request.user.memberprofile:
                        return
                else:
                    return redirect(reverse('add_profile'))

from django.shortcuts import redirect
from django.core.urlresolvers import reverse


class FinishProfile:
    def process_request(self,request):
        if not request.user.is_anonymous():
            if request.path != '/profile/' and request.path != '/accounts/logout/':
                if hasattr(request.user, "memberprofile"):
                    if request.user.memberprofile:
                        return
                else:
                    return redirect(reverse('add_profile'))

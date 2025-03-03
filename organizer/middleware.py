from django.shortcuts import redirect
from django.conf import settings
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin


class OrganizerOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/organizer/') and (not request.user.is_authenticated or not request.user.is_staff):
            if request.user.is_authenticated:
                messages.warning(request, "You don't have access to the requested page.")
                return redirect('user:dashboard')
            else:
                messages.info(request, "Please login to your account first.")
                return redirect('user:login')

        elif request.path.startswith('/user/') and (request.user.is_staff or request.user.is_superuser):
            messages.warning(request, "Sorry, you don't have access to the client side.")
            return redirect("organizer:dashboard")
        
        elif request.path.startswith('/message/') and (not request.user.is_authenticated):
            messages.warning(request, "you dont have access here.")
            return redirect("user:landingpage")

        return self.get_response(request)
    

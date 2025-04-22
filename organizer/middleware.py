from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.conf import settings
from django.contrib import messages
from chat.models import Room
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

        elif request.path.startswith('/user/') and (request.user.is_staff or request.user.is_superuser or not request.user.is_authenticated):
            messages.warning(request, "Sorry, you don't have access to the client side.")
            return redirect("organizer:dashboard")
        
        elif request.path.startswith('/message/') and (not request.user.is_authenticated):
            messages.warning(request, "you dont have access here.")
            return redirect("user:landingpage")
        
        elif request.path.startswith('/message/c/') :
            try:
                room_id = int(request.path.split("/")[3])
                room = Room.objects.get(id=room_id)
            except(IndexError, ValueError, Room.DoesNotExist):
                messages.warning(request, "Invalid or non-existent room.")
                return HttpResponseForbidden("Invalid or non-existent room.")
            
            if request.user != room.user1 and request.user != room.user2:
                messages.warning(request, "You don't have acces in that messages.")
                return redirect("chat:chat-user")
            

        return self.get_response(request)
    

import datetime
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Message, Room
from django.db.models import Q, Exists, OuterRef
from django.db.models import Max

# Create your views here.
def chat_box(request, room_id=None):
    user_rooms = Room.objects.filter(user1=request.user) | Room.objects.filter(user2=request.user)
    
    if request.user.is_staff:
        # user_rooms = user_rooms.annotate(
        #     has_messages=Exists(Message.objects.filter(room=OuterRef('pk')))
        # ).filter(has_messages=True)
        user_rooms = user_rooms.annotate(
            has_messages=Exists(Message.objects.filter(room=OuterRef('pk')))
        )
        
    user_last_messages = []

    for room in user_rooms:
        last_message = Message.objects.filter(room=room).order_by('-timestamp').first()
        
        # Determine the other user in the room
        other_user = room.user1 if room.user2 == request.user else room.user2

        user_last_messages.append({
            'room': room,
            'other_user': other_user,  # Store the other user
            'last_message': last_message.message if last_message else "No messages yet",
            'last_message_time': last_message.timestamp if last_message else None,
        })
        
    chats = None
    room = None
    if room_id:
        room = get_object_or_404(Room, id=room_id)
        chats = Message.objects.filter(room=room)
        print(chats)
        
    return render (request, 'chat/chat_box.html', {'user_last_messages': user_last_messages, 'chats' : chats, 'room_id':room_id, 'room':room})
from django.urls import path
from . import views

app_name = "chat"


urlpatterns = [
    # path('', views.chat, name="chat"),
   path('c/<str:room_name>/', views.chat_box, name='chat-user'),
]
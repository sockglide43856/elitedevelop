from django.urls import path
from . import views

urlpatterns = [
    path("", views.chatPage, name="chat-page"),
    path("send/", views.send_message, name="send-message"),
    path("get_messages/", views.get_messages, name="get-messages"),
    path("private/", views.private_redirect, name="private-redirect"), # Redirects to /home
    path("private/home/", views.PrivatePortalView.as_view(), name="private-portal"),
    path("private/create/", views.create_private_chat, name="private-create"),
    path("private/join/", views.join_private_chat, name="private-join"),

    path("private/<uuid:membership_id>/", views.private_chat_room, name="private-room"),

    path("private/<uuid:membership_id>/get/", views.get_private_messages, name="get-private-messages"),
    path("private/<uuid:membership_id>/send/", views.send_private_message, name="send-private-message"),

    path("private/<uuid:membership_id>/leave/", views.leave_or_delete_room, name="private-leave-delete"),

    path("private/<uuid:membership_id>/edit/", views.edit_private_message, name="private-edit-message"),
    path("private/<uuid:membership_id>/unsend/", views.unsend_private_message, name="private-unsend-message"),
    path('api/save-subscription/', views.save_push_subscription, name='save_subscription'),
    path("api/check-new-messages/", views.check_global_notifications, name="global-notifications-check"),
    path("api/destroy-web-push-subscription", views.destory_push_subscription, name="destory_push_subscription"),
    path('join/<str:code>/', views.quick_join_room, name='quick-join'),

    path('private/<uuid:membership_id>/typing/', views.update_typing_status, name='private-typing'),
    path('dm/', views.dm_inbox, name='dm_inbox'),

    # Shortcut to start/open a conversation with a specific user by ID
    path('dm/start/<int:user_id>/', views.start_dm, name='start_dm'),

    # The actual 1-on-1 chat room for a specific conversation
    path('dm/<int:conversation_id>/', views.dm_detail, name='dm_detail'),
]

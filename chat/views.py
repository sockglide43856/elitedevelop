import json
import traceback
from datetime import timedelta
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.db.models import Q
from django.core.cache import cache
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt

from elitedevelop.models import UserBlock, UserReport
from .models import (
    PrivateChatRoom,
    PrivateChatMembership,
    PrivateMessage,
    ChatMessage,
    DMConversation,
    DirectMessage,
    WebPushSubscription,
)
from .utils import send_push_to_user

User = get_user_model()



def get_blocked_user_ids(user):
    blocked_ids = UserBlock.objects.filter(blocker=user).values_list('blocked_id', flat=True)
    blocked_by_ids = UserBlock.objects.filter(blocked=user).values_list('blocker_id', flat=True)
    return set(blocked_ids).union(set(blocked_by_ids))


# ==========================================
# 1. USER PROFILE ACTIONS
# ==========================================

@login_required
def user_details(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    is_blocked = UserBlock.objects.filter(blocker=request.user, blocked=target_user).exists()

    return render(request, 'user_details.html', {
        'target_user': target_user,
        'is_blocked': is_blocked,
    })


@login_required
def toggle_block_user(request, user_id):
    if request.method == "POST":
        target_user = get_object_or_404(User, id=user_id)
        if target_user == request.user:
            messages.error(request, "You cannot block yourself.")
            return redirect('user_details', user_id=user_id)

        block_obj, created = UserBlock.objects.get_or_create(blocker=request.user, blocked=target_user)

        if created:
            messages.success(request, f"You have blocked @{target_user.username}.")
        else:
            block_obj.delete()
            messages.info(request, f"You have unblocked @{target_user.username}.")

    return redirect('user_details', user_id=user_id)


@login_required
def report_user(request, user_id):
    if request.method == "POST":
        target_user = get_object_or_404(User, id=user_id)
        if target_user == request.user:
            messages.error(request, "You cannot report yourself.")
            return redirect('user_details', user_id=user_id)

        reason = request.POST.get('reason')
        details = request.POST.get('details', '').strip()

        if reason:
            UserReport.objects.create(
                reporter=request.user,
                reported_user=target_user,
                reason=reason,
                details=details
            )
            messages.success(request, f"Thank you. Your report against @{target_user.username} has been submitted.")
        else:
            messages.error(request, "Please select a reason for reporting.")

    return redirect('user_details', user_id=user_id)


# ==========================================
# 2. DIRECT MESSAGES
# ==========================================

@login_required
def dm_inbox(request):
    excluded_ids = get_blocked_user_ids(request.user)

    conversations = DMConversation.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).exclude(
        user1_id__in=excluded_ids
    ).exclude(
        user2_id__in=excluded_ids
    ).order_by('-updated_at')

    for conv in conversations:
        conv.recipient = conv.user2 if conv.user1 == request.user else conv.user1

    excluded_ids.add(request.user.id)
    available_users = User.objects.exclude(id__in=excluded_ids)

    return render(request, 'dm_inbox.html', {
        'conversations': conversations,
        'available_users': available_users,
    })


@login_required
def start_dm(request, user_id):
    target_user = get_object_or_404(User, id=user_id)

    excluded_ids = get_blocked_user_ids(request.user)
    if target_user.id in excluded_ids:
        messages.error(request, "You cannot message this user.")
        return redirect('dm_inbox')

    conversation, _ = DMConversation.get_or_create_conversation(request.user, target_user)
    return redirect('dm_detail', conversation_id=conversation.id)


@login_required
def dm_detail(request, conversation_id):
    conversation = get_object_or_404(DMConversation, id=conversation_id)

    if request.user not in [conversation.user1, conversation.user2]:
        return redirect('dm_inbox')

    recipient = conversation.user2 if conversation.user1 == request.user else conversation.user1

    excluded_ids = get_blocked_user_ids(request.user)
    if recipient.id in excluded_ids:
        return redirect('dm_inbox')

    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        content = request.POST.get('content', '').strip()
        if content:
            DirectMessage.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            conversation.save()

            if recipient.id not in excluded_ids:
                send_push_to_user(
                    user=recipient,
                    title=f"New DM from @{request.user.username}",
                    message=f"@{request.user.username}: {content}",
                    target_url=f"/dm/{conversation.id}/"
                )

            return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': 'empty'}, status=400)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

        messages_data = [
            {
                'id': msg.id,
                'content': msg.content,
                'sender': msg.sender.username,
                'is_me': msg.sender == request.user,
                'timestamp': msg.timestamp.strftime("%H:%M")
            }
            for msg in conversation.messages.all()
        ]
        return JsonResponse({'messages': messages_data})

    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    return render(request, 'dm_detail.html', {
        'conversation': conversation,
        'chat_messages': conversation.messages.all(),
        'recipient': recipient,
    })


# ==========================================
# 3. NOTIFICATIONS
# ==========================================


def destory_push_subscription(request):
    if request.method == "POST":
        WebPushSubscription.objects.filter(user=request.user).delete()
        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "error"}, status=405)

@login_required
def check_global_notifications(request):
    excluded_ids = get_blocked_user_ids(request.user)

    user_memberships = PrivateChatMembership.objects.filter(user=request.user)
    room_ids = user_memberships.values_list('room_id', flat=True)

    unread_messages = PrivateMessage.objects.filter(
        room_id__in=room_ids
    ).exclude(
        author=request.user
    ).exclude(
        author_id__in=excluded_ids
    ).exclude(
        read_by=request.user
    ).select_related('room', 'author')

    results = []
    for msg in unread_messages:
        results.append({
            'id': msg.id,
            'room_name': msg.room.name,
            'username': msg.author.username,
            'message': "Sent an attachment" if msg.is_unsent else msg.message,
            'raw_timestamp': msg.timestamp.isoformat()
        })
    return JsonResponse({'unread_count': len(results), 'notifications': results})


# ==========================================
# 4. PRIVATE ROOMS & PUSH NOTIFICATION DISPATCH
# ==========================================

@login_required
def send_private_message(request, membership_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=400)

    membership = get_object_or_404(
        PrivateChatMembership,
        id=membership_id,
        user=request.user
    )

    try:
        data = json.loads(request.body)
        message_text = data.get('message', '').strip()

        if not message_text:
            return JsonResponse({'status': 'error'}, status=400)

        PrivateMessage.objects.create(
            room=membership.room,
            author=request.user,
            message=message_text
        )

        excluded_ids = get_blocked_user_ids(request.user)

        other_members = membership.room.users.exclude(
            id=request.user.id
        ).exclude(
            id__in=excluded_ids
        )

        for member in other_members:

            # Get THIS user's membership ID for the room.
            recipient_membership = PrivateChatMembership.objects.filter(
                room=membership.room,
                user=member
            ).first()

            if not recipient_membership:
                continue

            send_push_to_user(
                user=member,
                title=f"New message in {membership.room.name}",
                message=f"@{request.user.username}: {message_text}",
                target_url=f"/chat/private/{recipient_membership.id}/"
            )

        return JsonResponse({'status': 'ok'})

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'error': 'Invalid JSON'
        }, status=400)
@login_required
@csrf_exempt
def save_push_subscription(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            WebPushSubscription.objects.update_or_create(
                user=request.user,
                endpoint=data['endpoint'],
                defaults={'p256dh': data['keys']['p256dh'], 'auth': data['keys']['auth']}
            )
            return JsonResponse({'status': 'success', 'message': 'Subscription saved.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'invalid method'}, status=405)


@login_required
def private_redirect(request):
    return redirect('private-portal')


class PrivatePortalView(LoginRequiredMixin, TemplateView):
    template_name = 'private_portal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['memberships'] = PrivateChatMembership.objects.filter(
            user=self.request.user
        ).select_related('room')
        return context


@login_required
def create_private_chat(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        icon = request.POST.get('icon', '💬')

        if not name:
            messages.error(request, "Room name is required.")
            return redirect('private-portal')

        room = PrivateChatRoom.objects.create(name=name, icon=icon, owner=request.user)
        membership = PrivateChatMembership.objects.create(user=request.user, room=room)
        messages.success(request, f"Room '{name}' created! Invite Code: {room.invite_code}")
        return redirect('private-room', membership_id=membership.id)
    return redirect('private-portal')


@login_required
def join_private_chat(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        try:
            room = PrivateChatRoom.objects.get(invite_code=code)
            membership, created = PrivateChatMembership.objects.get_or_create(user=request.user, room=room)
            if created:
                messages.success(request, f"Joined '{room.name}' successfully.")
            else:
                messages.info(request, f"You are already a member of '{room.name}'.")
            return redirect('private-room', membership_id=membership.id)
        except PrivateChatRoom.DoesNotExist:
            messages.error(request, "Invalid invite code.")
            return redirect('private-portal')
    return redirect('private-portal')


def quick_join_room(request, code):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to join a private room.")
        return redirect('login')

    code = code.upper().strip()
    try:
        room = PrivateChatRoom.objects.get(invite_code=code)
        membership, created = PrivateChatMembership.objects.get_or_create(user=request.user, room=room)
        if created:
            messages.success(request, f"Successfully joined {room.name}!")
        return redirect('private-room', membership_id=membership.id)
    except PrivateChatRoom.DoesNotExist:
        messages.error(request, "Invalid invite code.")
        return redirect('private-portal')


@login_required
def private_chat_room(request, membership_id):
    membership = get_object_or_404(PrivateChatMembership, id=membership_id)
    if membership.user != request.user:
        return HttpResponseForbidden("You do not have access to this URL.")


    return render(request, 'private_room.html', {
        'room': membership.room,
        'membership': membership,
        'is_owner': (membership.room.owner == request.user),
        'members': membership.room.users.all(),
    })


@login_required
def update_typing_status(request, membership_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=400)

    membership = get_object_or_404(PrivateChatMembership, id=membership_id, user=request.user)
    cache.set(f"room_{membership.room_id}_user_{request.user.username}_typing", True, 3)
    return JsonResponse({'status': 'ok'})


@login_required
def get_private_messages(request, membership_id):
    membership = get_object_or_404(PrivateChatMembership, id=membership_id)
    if membership.user != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    room = membership.room
    now = timezone.now()

    cache.set(f"room_{room.id}_user_{request.user.username}_online_pulse", True, 6)
    cache.set(f"room_{room.id}_user_{request.user.username}_last_seen", now.isoformat(), 86400)

    members_status = {}
    for member in room.users.all():
        is_online = cache.get(f"room_{room.id}_user_{member.username}_online_pulse", False)
        last_seen_iso = cache.get(f"room_{room.id}_user_{member.username}_last_seen")
        is_typing = cache.get(f"room_{room.id}_user_{member.username}_typing", False)

        members_status[member.username] = {
            'is_online': is_online,
            'is_typing': is_typing if member.username != request.user.username else False,
            'last_seen_raw': last_seen_iso
        }

    excluded_ids = get_blocked_user_ids(request.user)
    messages_queryset = PrivateMessage.objects.filter(room=room).exclude(author_id__in=excluded_ids).order_by('timestamp').select_related('author').prefetch_related('read_by')

    unread_incoming_messages = messages_queryset.exclude(author=request.user).exclude(read_by=request.user)
    if unread_incoming_messages.exists():
        PrivateMessage.read_by.through.objects.bulk_create([
            PrivateMessage.read_by.through(privatemessage_id=msg.id, user_id=request.user.id)
            for msg in unread_incoming_messages
        ], ignore_conflicts=True)

        messages_queryset = PrivateMessage.objects.filter(room=room).exclude(author_id__in=excluded_ids).order_by('timestamp').select_related('author').prefetch_related('read_by')

    total_other_members = max(0, room.users.count() - 1)

    messages_data = [
        {
            'id': msg.id,
            'username': msg.author.username,
            'message': getattr(msg, 'get_decrypted_message', msg.message),
            'raw_timestamp': msg.timestamp.isoformat(),
            'is_edited': msg.is_edited,
            'is_unsent': msg.is_unsent,
            'subtext': "READ BY EVERYONE" if len(msg.read_by.all()) == total_other_members else f"READ BY {len(msg.read_by.all())} OUT OF {total_other_members}"
        }
        for msg in messages_queryset
    ]

    return JsonResponse({
        'messages': messages_data,
        'members_status': members_status
    })


@login_required
def edit_private_message(request, membership_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=400)

    membership = get_object_or_404(PrivateChatMembership, id=membership_id, user=request.user)
    try:
        data = json.loads(request.body)
        msg = get_object_or_404(PrivateMessage, id=data.get('message_id'), author=request.user, room=membership.room)

        if timezone.now() - msg.timestamp > timedelta(seconds=60) or msg.is_unsent:
            return JsonResponse({'error': 'Cannot edit message'}, status=400)

        new_text = data.get('message', '').strip()
        if new_text:
            msg.message = new_text
            msg.is_edited = True
            msg.save()
            return JsonResponse({'status': 'ok'})
    except Exception:
        pass
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def unsend_private_message(request, membership_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=400)

    membership = get_object_or_404(PrivateChatMembership, id=membership_id, user=request.user)
    try:
        data = json.loads(request.body)
        msg = get_object_or_404(PrivateMessage, id=data.get('message_id'), author=request.user, room=membership.room)

        if timezone.now() - msg.timestamp > timedelta(seconds=60):
            return JsonResponse({'error': 'Time limit exceeded'}, status=400)

        msg.is_unsent = True
        msg.save()
        return JsonResponse({'status': 'ok'})
    except Exception:
        pass
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def leave_or_delete_room(request, membership_id):
    if request.method != 'POST':
        return HttpResponseForbidden()

    membership = get_object_or_404(PrivateChatMembership, id=membership_id, user=request.user)
    room = membership.room
    room_name = room.name

    if room.owner == request.user:
        room.delete()
        messages.success(request, f"Chat room '{room_name}' has been deleted.")
    else:
        membership.delete()
        messages.success(request, f"You have left '{room_name}'.")
    return redirect('private-portal')


# ==========================================
# 5. PUBLIC CHAT
# ==========================================

def chatPage(request):
    return render(request, "index.html")


@login_required
def send_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message_text = data.get('message', '')
            if message_text.strip():
                ChatMessage.objects.create(user=request.user, message=message_text)
                return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def get_messages(request):
    messages_query = ChatMessage.objects.all().select_related('user')
    messages_list = [{'username': m.user.username, 'message': m.message} for m in messages_query]
    return JsonResponse({'messages': messages_list})

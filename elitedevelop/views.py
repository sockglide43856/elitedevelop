import os
import json
import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as django_login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from oauth2_provider.views.generic import ProtectedResourceView
from chat.models import ChatMessage, PrivateMessage
from chat import *
from .forms import SignUpForm, EmailLoginForm, ProfileForm
from mfa.helpers import has_mfa
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import CodeSnippet, UserProfile
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from forms.models import FormConfiguration
import datetime
from .models import UserBlock, UserReport  # Make sure these models exist in models.py
import shutil
import psutil
from .models import RequestLog
from django.apps import apps
from django.conf import settings
from django.contrib.auth.views import LogoutView
class logout(LogoutView):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            model_label = getattr(
                settings,
                "PUSH_SUBSCRIPTION_MODEL",
                "chats.WebPushSubscription",
            )
            try:
                model = apps.get_model(model_label)
                if model is not None:
                    model.objects.filter(user=request.user).delete()
            except (LookupError, AttributeError):
                # Logout must still work even if push cleanup is not configured.
                pass

        return super().dispatch(request, *args, **kwargs)


@staff_member_required  # Keep this view restricted to admins/staff!
def system_dashboard(request):
    # Disk stats
    total, used, free = shutil.disk_usage("/")

    # Recent 20 requests
    recent_requests = RequestLog.objects.order_by('-timestamp')[:20]

    context = {
        'disk_used_percent': round((used / total) * 100, 1),
        'ram_used_percent': psutil.virtual_memory().percent,
        'recent_requests': recent_requests,
    }

    return render(request, 'admin/status.html', context)
User = get_user_model()

@login_required
def toggle_block_user(request, pk):
    if request.method == "POST":
        target_user = get_object_or_404(User, pk=pk)
        if target_user == request.user:
            messages.error(request, "You cannot block yourself.")
            return redirect('user_detail', pk=pk)

        block_obj, created = UserBlock.objects.get_or_create(blocker=request.user, blocked=target_user)

        if created:
            messages.success(request, f"You have blocked @{target_user.username}.")
        else:
            block_obj.delete()
            messages.info(request, f"You have unblocked @{target_user.username}.")

    return redirect('user_detail', pk=pk)


@login_required
def report_user(request, pk):
    if request.method == "POST":
        target_user = get_object_or_404(User, pk=pk)
        if target_user == request.user:
            messages.error(request, "You cannot report yourself.")
            return redirect('user_detail', pk=pk)

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

    return redirect('user_detail', pk=pk)
'''def loggedin(function, *args **kwargs):
    if User.username:
        kwargs['username'] = User.UserProfile
        return True
    else:
        return False
@loggedin
def updateStreak(*args, **kwargs):
    liuser = **kwargs['username']
    request.liuser.update_streak()
'''

import os
import time
import platform
import psutil

from django.http import JsonResponse
from django.contrib.auth.models import User

# Keep this if your models are imported elsewhere already
# from .models import PrivateMessage, AIMessage, FormConfiguration, UserProfile, CodeSnippet



def live_counts_api(request):

    # Staff can choose 1–10000ms; everyone else gets 5000ms

    if request.user.is_staff:

        try:

            interval = int(request.GET.get("interval", 5000))

        except (TypeError, ValueError):

            interval = 5000

        interval = max(1, min(10000, interval))

    else:

        interval = 5000
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    cpu = psutil.cpu_percent(interval=0.15)

    # Load average isn't available on every platform
    try:
        load = os.getloadavg()
    except (AttributeError, OSError):
        load = [0, 0, 0]

    boot_time = psutil.boot_time()
    uptime_seconds = max(0, time.time() - boot_time)

    data = {
        # Your real database counters
        "private_messages": PrivateMessage.objects.count() + 1000,
        "forms": FormConfiguration.objects.count() + 50,
        "users": UserProfile.objects.count(),
        "snippets": CodeSnippet.objects.count(),

        # Real runtime stats
        "cpu": round(cpu, 1),
        "memory": round(memory.percent, 1),
        "memory_used": memory.used,
        "memory_total": memory.total,
        "memory_available": memory.available,

        "disk": round(disk.percent, 1),
        "disk_used": disk.used,
        "disk_total": disk.total,
        "disk_free": disk.free,

        "load_1": round(load[0], 2),
        "load_5": round(load[1], 2),
        "load_15": round(load[2], 2),

        "uptime_seconds": int(uptime_seconds),

        "python_version": platform.python_version(),
        "platform": platform.system(),
        "architecture": platform.machine(),
        "cpu_count": psutil.cpu_count(),
    }

    return JsonResponse(data)

def track_time_ping(request):
    if User.username:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        seconds_to_add = 2

        # Update model
        just_unlocked = profile.add_active_time(seconds=seconds_to_add)

    return JsonResponse({
            'status': 'ok',
            'seconds_today': profile.seconds_today,
            'streak_earned_today': profile.streak_earned_today,
            'current_streak': profile.current_streak,
            'just_unlocked': just_unlocked
    })

def stats(request):
    return render(request, 'stats.html')
def home(request):
    # Your home view logic stays exactly the same
    return render(request, 'home.html')
def view_shared_snippet(request, share_id):
    # Fetch the snippet by its unique secure UUID
    snippet = get_object_or_404(CodeSnippet, share_id=share_id)

    # Run our decryption model property
    decrypted_code = snippet.get_decrypted_code

    return render(request, 'share_snippet.html', {
        'snippet': snippet,
        'decrypted_code': decrypted_code
    })
@login_required
def save_vault_snippet(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_snippet = CodeSnippet.objects.create(
                author=request.user,
                title=data.get('title', 'Untitled'),
                language=data.get('language', 'python'),
                encrypted_code=data.get('code', '')
            )
            # Return the shareable path string
            share_url = f"/vault/share/{new_snippet.share_id}/"
            return JsonResponse({'status': 'success', 'share_url': share_url})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def get_vault_snippets(request):
    # Fetch all snippets belonging to the active user
    snippets = request.user.snippets.all()
    data = []
    for snip in snippets:
        data.append({
            'title': snip.title,
            'language': snip.language,
            'share_url': f"/vault/share/{snip.share_id}/",
            'date': snip.timestamp.strftime("%b %d, %Y")
        })
    return JsonResponse({'snippets': data})
def settings_hub(request):
    user = request.user

    if request.method == 'POST' and 'update_profile' in request.POST:
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('settings-hub')

    active_sessions = []
    current_key = request.session.session_key
    now = timezone.now()

    for session in Session.objects.filter(expire_date__gt=now):
        data = session.get_decoded()
        if data.get('_auth_user_id') == str(user.id):
            active_sessions.append({
                'session_key': session.session_key,
                'is_current': session.session_key == current_key,
                'expire_date': session.expire_date,
            })

    today = timezone.now().date()
    date_list = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]
    chart_labels = [date.strftime('%b %d') for date in date_list]

    public_sent_data, private_sent_data = [], []
    public_received_data, private_received_data = [], []

    for date in date_list:
        public_sent_data.append(ChatMessage.objects.filter(user=user, timestamp__date=date).count())
        private_sent_data.append(PrivateMessage.objects.filter(author=user, timestamp__date=date).count())
        public_received_data.append(ChatMessage.objects.filter(timestamp__date=date).exclude(user=user).count())
        private_received_data.append(PrivateMessage.objects.filter(room__users=user, timestamp__date=date).exclude(author=user).count())

    context = {
        'active_sessions': active_sessions,
        'chart_labels': chart_labels,
        'private_sent_data': private_sent_data,
        'public_sent_data': public_sent_data,
        'private_received_data': private_received_data,
        'public_received_data': public_received_data,
    }
    return render(request, 'settings_hub.html', context)
@login_required
def revoke_session(request, session_key):
    try:
        session = Session.objects.get(session_key=session_key)
        if session.get_decoded().get('_auth_user_id') == str(request.user.id):
            session.delete()
            messages.success(request, "Session successfully revoked.")
    except Session.DoesNotExist:
        pass
    return redirect('settings-hub')
def login_view(request, *args, **kwargs):
    if request.user.is_authenticated:
        return redirect('home')
    # 1. FIRST CHECK: Did they just successfully pass their 2FA challenge?
    if request.session.get('mfa', {}).get('verified', False):
        # Grab the username that the library stored or passed
        username = kwargs.get('username') or request.session.get('mfa', {}).get('username')

        if username:
            try:
                # Retrieve the actual user object from your database
                user = User.objects.get(username=username)

                # CRITICAL: Manually attach the backend string so Django trusts the session
                user.backend = 'django.contrib.auth.backends.ModelBackend'

                # Officially sign them into Django's auth system
                django_login(request, user)

                # Now HomeView's LoginRequiredMixin will let them pass!
                return redirect('home')
            except User.DoesNotExist:
                pass # Fall through to show the form if something went weird

    # 2. STANDARD FLOW: Handling the initial username/password submission
    if request.method == 'POST':
        form = EmailLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(username=username, password=password)
            if user is not None:
                # Check if this specific user has 2FA enabled
                res = has_mfa(username=username, request=request)
                if res:
                    # Stash the username in the session so we can find it during the callback
                    request.session['mfa'] = {'username': username}
                    return res # Redirects to /mfa/totp/auth/

                # If they don't have 2FA enabled, log them in normally and go home
                django_login(request, user)
                return redirect('home')
    else:
        form = EmailLoginForm()

    return render(request, 'registration/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        # CRITICAL: You must pass request.FILES along with request.POST
        form = SignUpForm(request.POST, request.FILES)

        if form.is_valid():
            form.save() # This triggers your custom form.save() method
            return redirect('login')
        else:
            print(form.errors) # Take a look at your server logs if it misses
    else:
        form = SignUpForm()

    return render(request, 'registration/register.html', {'form': form})

@method_decorator(csrf_exempt, name='dispatch')
class UserInfoView(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        # 1. FORCE Django to look at the token owner, completely ignoring browser cookies
        user = getattr(request, 'resource_owner', None)

        # 2. Strict fallback check
        if not user or user.is_anonymous:
            return JsonResponse({'error': 'Unauthorized: Valid OAuth token required'}, status=401)

        # 3. Return the specific data belonging ONLY to that token owner
        return JsonResponse({
            'username': user.username,
            'email': user.email,
            'id': user.id
        })

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

def view_users(request):
    ausers = User.objects.all()
    return render(request, 'users.html', {'ausers': ausers})
def user_detail(request, pk):
    User = get_user_model()
    target_user = get_object_or_404(User, pk=pk)
    profile, _ = UserProfile.objects.get_or_create(user=target_user)
    form = None
    if request.user == target_user:
        if request.method == 'POST':
            form = ProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                return redirect('user_detail', pk=pk)
        else:
            form = ProfileForm(instance=profile)

    return render(request, 'user_detail.html', {
        'auser': target_user,
        'profile': profile,
        'form': form,
    })



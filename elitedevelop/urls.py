from django.contrib import admin
from django.urls import path, include
from elitedevelop.views import HomeView, UserInfoView, register, login_view
from . import views
from machina import urls as machina_urls
from django.views.generic import RedirectView, TemplateView
from django.templatetags.static import static
from django.contrib.auth import views as auth_views

# UNUSED URLS #
#path('g/', include('gaming.urls')),
#path('gaming/', include('gaming.urls')),
###############

urlpatterns = [
    path('stats/', views.stats, name='stats'),
    path('legal/', TemplateView.as_view(template_name="legal.html"), name='legal'),
    path('chat/', include('chat.urls')),
    path('chats/', include('chat.urls')),
    path('forums/', include(machina_urls)),
    path('mfa/', include('mfa.urls')),
    path('admin/', admin.site.urls),
    path('admindash/', views.system_dashboard, name='dashboard'),
    path('settings/', views.settings_hub, name='settings-hub'),
    path('settings/revoke/<str:session_key>/', views.revoke_session, name='revoke-session'),
    path('accounts/password_reset/',auth_views.PasswordResetView.as_view(html_email_template_name='registration/password_reset_email.html',subject_template_name='registration/password_reset_subject.txt'),name='password_reset'),
    path('accounts/login/', login_view, name='login'),
    path('accounts/register/', register, name='register'),
    path('accounts/logout/', views.logout.as_view(), name="logout"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('allauth.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('qr/', include('qr_generator.urls')),
    path('py/', TemplateView.as_view(template_name="pyexec.html"), name='py'),
    path("ai/", include("ai.urls")),
    path('forms/', include('forms.urls')),
    path('eliteos/', include('eliteos.urls')),
    path('api/vault/save/', views.save_vault_snippet, name='api-vault-save'),
    path('api/vault/list/', views.get_vault_snippets, name='api-vault-list'),
    path('api/user-info/', UserInfoView.as_view(), name='user-info'),
    path('api/track-time/', views.track_time_ping, name='track_time_ping'),
    path('api/live-counts/', views.live_counts_api, name='live-counts-api'),
    path('vault/share/<uuid:share_id>/', views.view_shared_snippet, name='view-shared-snippet'),
    path('users/', views.view_users, name='view_users'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('user/<int:pk>/block/', views.toggle_block_user, name='toggle_block_user'),
    path('user/<int:pk>/report/', views.report_user, name='report_user'),
    path("proxy/", include("proxy.urls")),
    path('', views.home, name='home'),
]
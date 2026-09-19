from django.urls import path
from .views import formHome, create_form_view, serve_dynamic_form, view_responses, user_dashboard

urlpatterns = [
    path('', formHome, name='fhome'),
    path('dashboard/', user_dashboard, name='fdashboard'),
    path('build/', create_form_view, name='build_form'),
    path('<str:code>/', serve_dynamic_form, name='serve_form'),

    # Dynamic route demanding the exact custom code AND the 5-character HEX string token
    path('<str:code>/responses/<str:secret_token>/', view_responses, name='view_responses'),
]
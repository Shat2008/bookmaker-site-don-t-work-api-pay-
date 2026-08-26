from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('sport/<int:sport_id>/', views.sport_detail, name='sport_detail'),
    path('live/', views.live_matches, name='live_matches'),
    path('support/', views.support, name='support'),
    path('rules/', views.rules, name='rules'),  # ← добавляем этот маршрут
]
from django.urls import path, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = "api"

urlpatterns = (
    path('user/register/', views.UserCreateAPIView.as_view(), name='register'),

    path('user/login/', TokenObtainPairView.as_view(), name="token_create"),
    path('login/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('currency/user_currency/', views.UserCurrencyAddView.as_view(), name="user_currency"),
    path('rates/', views.CurrencyRateListView.as_view(), name='currency_rates'),
    path('currency/<int:id>/analytics/', views.AnalyticCurrencyRateListView.as_view(), name='currency_analytics'),
)

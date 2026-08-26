from django.urls import path
from . import views
from . import fondy_integration

app_name = 'payments'

urlpatterns = [
    path('deposit/', views.deposit, name='deposit'),
    path('stripe-deposit/', views.stripe_deposit, name='stripe_deposit'),
    path('stripe-payment-confirm/', views.stripe_payment_confirm, name='stripe_payment_confirm'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('transactions/', views.transaction_history, name='transactions'),
    path('callback/bank/', views.bank_callback, name='bank_callback'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('fondy/', fondy_integration.fondy_deposit, name='fondy_deposit'),
    path('webhook/fondy/', fondy_integration.fondy_webhook, name='fondy_webhook'),
    path('success/', views.payment_success, name='payment_success'),
    path('fail/', views.payment_fail, name='payment_fail'),
]
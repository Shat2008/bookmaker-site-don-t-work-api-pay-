from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Transaction
from .forms import DepositForm, WithdrawalForm, StripeDepositForm
from .stripe_service import StripePaymentService, convert_to_cents, convert_from_cents
from .integrations import BankIntegration
import json
import stripe

@login_required
def stripe_deposit(request):
    """Пополнение счета через Stripe"""
    if request.method == 'POST':
        form = StripeDepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            email = form.cleaned_data.get('email') or request.user.email
            
            # Создание Payment Intent
            stripe_service = StripePaymentService()
            amount_cents = convert_to_cents(amount)
            
            intent = stripe_service.create_payment_intent(
                user=request.user,
                amount=amount_cents,
                currency='usd',
                description=f"Deposit of ${amount} for {request.user.username}"
            )
            
            if intent:
                # Создание транзакции в БД
                transaction = Transaction.objects.create(
                    user=request.user,
                    transaction_type='deposit',
                    amount=amount,
                    payment_method='stripe',
                    stripe_payment_intent_id=intent.id,
                    description=f"Stripe payment: ${amount}",
                    status='pending',
                )
                
                context = {
                    'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
                    'client_secret': intent.client_secret,
                    'amount': amount,
                    'transaction_id': transaction.id,
                    'amount_cents': amount_cents,
                }
                return render(request, 'payments/stripe_payment.html', context)
            else:
                messages.error(request, 'Ошибка при создании платежа. Попробуйте позже.')
    else:
        form = StripeDepositForm()
    
    context = {
        'form': form,
        'title': 'Пополнение через Stripe',
    }
    return render(request, 'payments/stripe_deposit.html', context)

@login_required
def stripe_payment_confirm(request):
    """Подтверждение платежа Stripe"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_intent_id = data.get('payment_intent_id')
            
            if not payment_intent_id:
                return JsonResponse({'status': 'error', 'message': 'Payment intent ID required'}, status=400)
            
            # Получение статуса платежа
            stripe_service = StripePaymentService()
            intent_status = stripe_service.get_payment_intent_status(payment_intent_id)
            
            if intent_status and intent_status['status'] == 'succeeded':
                # Обновление транзакции
                try:
                    transaction = Transaction.objects.get(stripe_payment_intent_id=payment_intent_id)
                    transaction.complete({'stripe_status': 'succeeded'})
                    
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Payment successful',
                        'transaction_id': transaction.id
                    })
                except Transaction.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Transaction not found'}, status=404)
            else:
                return JsonResponse({'status': 'error', 'message': 'Payment not confirmed'}, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@login_required
def deposit(request):
    """Пополнение счета"""
    if request.method == 'POST':
        form = DepositForm(request.POST, user=request.user)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            
            if payment_method == 'stripe':
                return redirect('payments:stripe_deposit')
            
            # Создание транзакции
            transaction = Transaction.objects.create(
                user=request.user,
                transaction_type='deposit',
                amount=form.cleaned_data['amount'],
                payment_method=payment_method,
                payment_details={
                    'card_number': form.cleaned_data.get('card_number', ''),
                    'phone': form.cleaned_data.get('phone', ''),
                    'wallet': form.cleaned_data.get('wallet', ''),
                },
                description=f"Пополнение через {payment_method}",
            )
            
            # Интеграция с банком (в реальном проекте здесь будет вызов API)
            bank = BankIntegration()
            bank_response = bank.create_payment(
                user_id=request.user.id,
                amount=float(form.cleaned_data['amount']),
                description=f"Пополнение счета VIP BET"
            )
            
            if bank_response and bank_response.get('success'):
                transaction.external_id = bank_response.get('payment_id', '')
                transaction.bank_response = bank_response
                transaction.save()
                
                messages.success(request, 'Платеж создан. Перенаправляем на страницу оплаты...')
                # Здесь обычно происходит редирект на страницу банка
                return render(request, 'payments/payment_redirect.html', {
                    'payment_url': bank_response.get('payment_url'),
                    'transaction': transaction,
                })
            else:
                transaction.fail(bank_response.get('error', 'Ошибка банка'))
                messages.error(request, 'Ошибка при создании платежа. Попробуйте еще раз.')
    else:
        form = DepositForm(user=request.user)
    
    context = {
        'form': form,
        'min_deposit': 100,
        'max_deposit': 100000,
        'title': 'Пополнение счета',
    }
    return render(request, 'payments/deposit.html', context)

@login_required
def withdraw(request):
    """Вывод средств"""
    if request.method == 'POST':
        form = WithdrawalForm(request.POST, user=request.user)
        if form.is_valid():
            # Создание транзакции на вывод
            transaction = Transaction.objects.create(
                user=request.user,
                transaction_type='withdrawal',
                amount=form.cleaned_data['amount'],
                payment_method=form.cleaned_data['payment_method'],
                payment_details={
                    'card_number': form.cleaned_data.get('card_number', ''),
                    'phone': form.cleaned_data.get('phone', ''),
                    'wallet': form.cleaned_data.get('wallet', ''),
                },
                description=f"Вывод средств через {form.cleaned_data['payment_method']}",
            )
            
            # Проверка минимальной суммы вывода
            if form.cleaned_data['amount'] < 100:
                messages.error(request, 'Минимальная сумма вывода - 100 ₽')
                return redirect('payments:withdraw')
            
            # Проверка максимальной суммы вывода
            if form.cleaned_data['amount'] > 50000:
                messages.error(request, 'Максимальная сумма вывода за раз - 50,000 ₽')
                return redirect('payments:withdraw')
            
            messages.success(request, 'Заявка на вывод принята. Средства будут переведены в течение 24 часов.')
            return redirect('payments:transactions')
    else:
        form = WithdrawalForm(user=request.user)
    
    context = {
        'form': form,
        'min_withdrawal': 100,
        'max_withdrawal': 50000,
        'title': 'Вывод средств',
    }
    return render(request, 'payments/withdraw.html', context)

@login_required
def transaction_history(request):
    """История транзакций"""
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    
    # Фильтрация
    transaction_type = request.GET.get('type')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    context = {
        'transactions': transactions,
        'total_deposits': sum(t.amount for t in transactions.filter(transaction_type='deposit', status='completed')),
        'total_withdrawals': sum(t.amount for t in transactions.filter(transaction_type='withdrawal', status='completed')),
        'total_wins': sum(t.amount for t in transactions.filter(transaction_type='win', status='completed')),
        'title': 'История транзакций',
    }
    return render(request, 'payments/transactions.html', context)

@csrf_exempt
def stripe_webhook(request):
    """Webhook для обработки событий Stripe"""
    if request.method == 'POST':
        try:
            payload = request.body
            sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
            
            stripe_service = StripePaymentService()
            event = stripe_service.verify_webhook_signature(payload, sig_header)
            
            if not event:
                return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=400)
            
            # Обработка разных типов событий
            if event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                
                try:
                    transaction = Transaction.objects.get(stripe_payment_intent_id=payment_intent['id'])
                    transaction.complete({'stripe_charge_id': payment_intent.get('charges', {}).get('data', [{}])[0].get('id', '')})
                    return JsonResponse({'status': 'success'})
                except Transaction.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Transaction not found'}, status=404)
            
            elif event['type'] == 'payment_intent.payment_failed':
                payment_intent = event['data']['object']
                
                try:
                    transaction = Transaction.objects.get(stripe_payment_intent_id=payment_intent['id'])
                    transaction.fail(payment_intent.get('last_payment_error', {}).get('message', 'Payment failed'))
                    return JsonResponse({'status': 'success'})
                except Transaction.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Transaction not found'}, status=404)
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            print(f"Webhook error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def bank_callback(request):
    """Callback от банковской системы"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            signature = request.headers.get('X-Signature', '')
            
            bank = BankIntegration()
            
            # Проверка подписи
            if not bank.verify_webhook(request.body.decode(), signature):
                return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=400)
            
            payment_id = data.get('payment_id')
            status = data.get('status')
            amount = data.get('amount')
            
            # Поиск транзакции
            try:
                transaction = Transaction.objects.get(external_id=payment_id)
                
                if status == 'success':
                    transaction.complete(data)
                    # Уведомление пользователя (можно реализовать через WebSocket или email)
                    return JsonResponse({'status': 'success'})
                else:
                    transaction.fail(data.get('error', 'Payment failed'))
                    return JsonResponse({'status': 'error', 'message': 'Payment failed'})
                    
            except Transaction.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Transaction not found'}, status=404)
                
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@login_required
def payment_success(request):
    """Успешная оплата"""
    payment_id = request.GET.get('payment_id')
    
    context = {
        'payment_id': payment_id,
        'title': 'Оплата успешна',
    }
    return render(request, 'payments/success.html', context)

@login_required
def payment_fail(request):
    """Неудачная оплата"""
    error = request.GET.get('error', 'Неизвестная ошибка')
    
    context = {
        'error': error,
        'title': 'Ошибка оплаты',
    }
    return render(request, 'payments/fail.html', context)
# Stripe API - Примеры использования

## 📚 Работа с StripePaymentService

### Инициализация

```python
from payments.stripe_service import StripePaymentService, convert_to_cents

service = StripePaymentService()
```

## 💳 Создание платежа

### Базовый Payment Intent

```python
# Создать платеж на $100
intent = service.create_payment_intent(
    user=request.user,
    amount=convert_to_cents(100),  # 10000 центов
    currency='usd',
    description='Payout for order #123'
)

# Вернет объект с:
# - intent.id (pi_...)
# - intent.client_secret
# - intent.status
# - intent.amount
```

### С метаданными

```python
# Создать платеж с доп. информацией
intent = service.create_payment_intent(
    user=request.user,
    amount=convert_to_cents(50),
    currency='usd',
    description='Weekly subscription renewal'
)

# Метаданные автоматически добавляются:
# metadata = {
#     'user_id': 123,
#     'username': 'john_doe',
#     'transaction_type': 'deposit'
# }
```

## 👤 Управление клиентами

### Создать или получить клиента

```python
# Автоматически создается в create_payment_intent
customer = service.create_customer(user=request.user)

# Вернет объект customer с:
# - customer.id (cus_...)
# - customer.email
# - customer.name
```

### Сохранить карту

```python
# Создать Setup Intent для сохранения карты
setup_intent = service.create_setup_intent(user=request.user)

# Вернет:
# - setup_intent.id (seti_...)
# - setup_intent.client_secret
```

### Получить сохраненные карты

```python
# Получить все способы оплаты клиента
payment_methods = service.list_payment_methods(customer_id='cus_...')

# Вернет список методов:
for pm in payment_methods:
    print(f"{pm.card.brand} {pm.card.last4}")
    # Вывод: visa 4242
```

## ✅ Проверка статуса

### Получить статус платежа

```python
# Проверить, завершен ли платеж
status_info = service.get_payment_intent_status('pi_...')

# Вернет:
# {
#     'status': 'succeeded',  # или 'processing', 'requires_action'
#     'client_secret': 'pi_...secret',
#     'amount': 5000,
#     'currency': 'usd'
# }

if status_info['status'] == 'succeeded':
    print("Платеж успешен!")
elif status_info['status'] == 'requires_action':
    print("Требуется 3D Secure")
```

### Подтвердить платеж

```python
# Получить полный объект платежа
intent = service.confirm_payment_intent('pi_...')

print(intent.status)
print(intent.amount)
print(intent.charges)
```

## 🔄 Возвраты

### Вернуть платеж

```python
# Полный возврат
refund = service.refund_payment(charge_id='ch_...')

# Частичный возврат ($10)
refund = service.refund_payment(
    charge_id='ch_...',
    amount=convert_to_cents(10)
)

# Проверить статус возврата
if refund.status == 'succeeded':
    print("Возврат обработан")
```

## 🔐 Webhook обработка

### Проверить подпись webhook

```python
# В Django view
payload = request.body
sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

event = service.verify_webhook_signature(payload, sig_header)

if event:
    print(f"Event type: {event['type']}")
    print(f"Event ID: {event['id']}")
else:
    print("Invalid webhook signature!")
```

### Обработка событий

```python
event = service.verify_webhook_signature(payload, sig_header)

if event['type'] == 'payment_intent.succeeded':
    payment_intent = event['data']['object']
    print(f"Payment {payment_intent['id']} succeeded!")
    # Обновить БД, отправить email и т.д.

elif event['type'] == 'payment_intent.payment_failed':
    payment_intent = event['data']['object']
    error = payment_intent['last_payment_error']
    print(f"Payment failed: {error['message']}")
    # Уведомить пользователя об ошибке
```

## 🌍 Работа с валютами

### Преобразование валют

```python
from payments.stripe_service import convert_to_cents, convert_from_cents

# Доллары → Центы
cents = convert_to_cents(100)  # 10000

# Центы → Доллары
dollars = convert_from_cents(10000)  # 100.0
```

### Поддерживаемые валюты

```python
# Stripe поддерживает 135+ валют
currencies = [
    'usd',      # US Dollar
    'eur',      # Euro
    'gbp',      # British Pound
    'jpy',      # Japanese Yen
    'cad',      # Canadian Dollar
    'aud',      # Australian Dollar
    'rub',      # Russian Ruble
    'cny',      # Chinese Yuan
    'inr',      # Indian Rupee
    # ... и многие другие
]

# Использование в коде
intent = service.create_payment_intent(
    user=request.user,
    amount=convert_to_cents(100),
    currency='eur'  # Евро
)
```

## 🎯 Практические примеры

### Пример 1: Пополнение счета

```python
def deposit_view(request):
    amount = 50.00  # USD
    
    # Создать платеж
    intent = service.create_payment_intent(
        user=request.user,
        amount=convert_to_cents(amount),
        currency='usd',
        description=f'Deposit for {request.user.username}'
    )
    
    # Сохранить в БД
    transaction = Transaction.objects.create(
        user=request.user,
        transaction_type='deposit',
        amount=amount,
        payment_method='stripe',
        stripe_payment_intent_id=intent.id,
        status='pending'
    )
    
    # Отправить на фронт
    return JsonResponse({
        'client_secret': intent.client_secret,
        'amount': amount
    })
```

### Пример 2: Проверка платежа

```python
def check_payment(request):
    payment_intent_id = request.GET.get('payment_intent_id')
    
    # Получить статус
    status_info = service.get_payment_intent_status(payment_intent_id)
    
    if status_info['status'] == 'succeeded':
        # Обновить транзакцию
        transaction = Transaction.objects.get(
            stripe_payment_intent_id=payment_intent_id
        )
        transaction.complete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Payment completed'
        })
    else:
        return JsonResponse({
            'status': 'pending',
            'message': f'Payment status: {status_info["status"]}'
        })
```

### Пример 3: Обработка webhook

```python
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    event = service.verify_webhook_signature(payload, sig_header)
    
    if not event:
        return JsonResponse({'status': 'error'}, status=400)
    
    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        transaction = Transaction.objects.get(
            stripe_payment_intent_id=intent['id']
        )
        
        # Завершить транзакцию
        transaction.complete({
            'stripe_charge_id': intent['charges']['data'][0]['id']
        })
        
        # Отправить уведомление пользователю
        send_payment_receipt_email(transaction.user)
        
        return JsonResponse({'status': 'success'})
    
    elif event['type'] == 'payment_intent.payment_failed':
        intent = event['data']['object']
        transaction = Transaction.objects.get(
            stripe_payment_intent_id=intent['id']
        )
        
        # Отметить как неудачную
        transaction.fail(
            intent['last_payment_error']['message']
        )
        
        # Отправить уведомление об ошибке
        send_payment_failure_email(transaction.user)
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'success'})
```

### Пример 4: Возврат платежа

```python
def refund_payment_view(request, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    
    if not transaction.stripe_charge_id:
        return JsonResponse({'error': 'No Stripe charge ID'}, status=400)
    
    # Выполнить возврат
    refund = service.refund_payment(
        charge_id=transaction.stripe_charge_id,
        amount=convert_to_cents(transaction.amount)
    )
    
    if refund:
        # Обновить статус
        transaction.status = 'refunded'
        transaction.save()
        
        # Вернуть деньги пользователю
        request.user.balance += transaction.amount
        request.user.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Refund processed'
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Refund failed'
        }, status=400)
```

## 🐛 Обработка ошибок

```python
import stripe

try:
    intent = service.create_payment_intent(
        user=request.user,
        amount=convert_to_cents(100),
        currency='usd'
    )
except stripe.error.CardError as e:
    # Ошибка карты
    print(f"Card declined: {e.user_message}")
    
except stripe.error.RateLimitError:
    # Слишком много запросов
    print("Too many requests to Stripe API")
    
except stripe.error.InvalidRequestError:
    # Неверный параметр
    print("Invalid parameters")
    
except stripe.error.APIConnectionError:
    # Нет соединения со Stripe
    print("Connection error")
    
except stripe.error.StripeError as e:
    # Общая ошибка Stripe
    print(f"Stripe error: {e}")
```

## 📊 Отладка

### Логирование

```python
import logging

logger = logging.getLogger(__name__)

try:
    intent = service.create_payment_intent(
        user=request.user,
        amount=convert_to_cents(100),
        currency='usd'
    )
    logger.info(f"Payment intent created: {intent.id}")
except Exception as e:
    logger.error(f"Payment intent creation failed: {str(e)}")
```

### Тестирование в интерпретаторе

```python
python manage.py shell

from payments.stripe_service import StripePaymentService
from django.contrib.auth import get_user_model

service = StripePaymentService()
User = get_user_model()
user = User.objects.first()

# Создать платеж
intent = service.create_payment_intent(
    user=user,
    amount=5000,
    currency='usd'
)

print(f"Intent ID: {intent.id}")
print(f"Status: {intent.status}")
print(f"Client Secret: {intent.client_secret}")
```

## 🔗 Полезные ссылки

- [Stripe API Reference](https://stripe.com/docs/api)
- [Payment Intent API](https://stripe.com/docs/api/payment_intents)
- [Error Types](https://stripe.com/docs/api/errors)
- [Testing](https://stripe.com/docs/testing)
- [Webhooks](https://stripe.com/docs/webhooks)

---

**Готово к использованию!** Используйте эти примеры как отправную точку для вашего приложения.

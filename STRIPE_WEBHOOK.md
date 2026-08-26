# Stripe Webhook Configuration

## 🔔 Что такое Webhook?

Webhook - это механизм, при котором Stripe отправляет уведомления о событиях (платеж успешен, платеж отклонен и т.д.) на ваш сервер.

## 🌐 Локальное тестирование (Development)

### Использование Stripe CLI

Stripe CLI позволяет перенаправить события Stripe на локальный сервер без интернета.

#### 1. Установить Stripe CLI

**macOS:**
```bash
brew install stripe/stripe-cli/stripe
```

**Windows (Chocolatey):**
```bash
choco install stripe-cli
```

**Linux:**
```bash
# Debian/Ubuntu
sudo apt-get install stripe-cli

# Other
curl https://raw.githubusercontent.com/stripe/stripe-cli/master/install.sh | bash
```

#### 2. Авторизация

```bash
stripe login
```

Следуйте инструкциям в браузере для авторизации.

#### 3. Проверить webhook

```bash
stripe listen --forward-to localhost:8000/payments/webhook/stripe/
```

Вы получите строку типа:
```
> Ready! Your webhook signing secret is: whsec_test_1234567890...
```

#### 4. Скопировать webhook secret

Скопируйте строку, начинающуюся с `whsec_`, в .env:

```env
STRIPE_WEBHOOK_SECRET=whsec_test_1234567890...
```

#### 5. Запустить сервер

В другом терминале:
```bash
python manage.py runserver
```

## 🚀 Production Webhook (Live)

### 1. Развернуть приложение

Убедитесь, что приложение доступно из интернета (например, на Heroku, DigitalOcean, AWS и т.д.)

### 2. Настроить webhook в Stripe Dashboard

1. Перейти: https://dashboard.stripe.com/webhooks
2. Нажать "Add endpoint"
3. Ввести URL: `https://yourapp.com/payments/webhook/stripe/`
4. Выбрать события для отслеживания:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
5. Нажать "Create endpoint"
6. Скопировать "Signing secret"

### 3. Обновить .env на сервере

```env
STRIPE_WEBHOOK_SECRET=whsec_live_...
```

## 📋 Поддерживаемые события

Текущая реализация обрабатывает:

```python
# payment_intent.succeeded
# Платеж успешно обработан
Event: {
    type: "payment_intent.succeeded",
    data: {
        object: {
            id: "pi_...",
            status: "succeeded",
            amount: 5000,  # в центах
            currency: "usd",
            metadata: {
                user_id: 123,
                username: "john_doe"
            }
        }
    }
}

# payment_intent.payment_failed
# Платеж отклонен
Event: {
    type: "payment_intent.payment_failed",
    data: {
        object: {
            id: "pi_...",
            status: "requires_action",
            last_payment_error: {
                message: "Your card was declined"
            }
        }
    }
}
```

## 🔧 Тестирование webhook локально

### Способ 1: Stripe CLI (Рекомендуется)

```bash
# Терминал 1
stripe listen --forward-to localhost:8000/payments/webhook/stripe/

# Терминал 2
python manage.py runserver

# Терминал 3
stripe trigger payment_intent.succeeded
```

### Способ 2: ngrok (Альтернативный способ)

#### Установка ngrok

```bash
# Скачать с https://ngrok.com/download
# или через package manager

# macOS
brew install ngrok

# Linux
snap install ngrok
```

#### Использование

```bash
# Терминал 1
ngrok http 8000

# Скопируйте URL вида https://xxxxx.ngrok.io
# Используйте в Stripe Dashboard:
# https://xxxxx.ngrok.io/payments/webhook/stripe/

# Терминал 2
python manage.py runserver
```

## 🐛 Отладка webhook

### Просмотр логов

**Stripe Dashboard:**
1. https://dashboard.stripe.com/webhooks
2. Нажмите на endpoint
3. Посмотрите "Events"

**Django:**
```python
# В settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'stripe_webhook.log',
        },
    },
    'loggers': {
        'stripe': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Примеры тестовых команд Stripe CLI

```bash
# Успешный платеж
stripe trigger payment_intent.succeeded

# Отклоненный платеж
stripe trigger payment_intent.payment_failed

# Получить все события
stripe events list

# Просмотреть определенное событие
stripe events retrieve <event_id>
```

## 📊 Структура webhook в коде

```python
# payments/views.py

@csrf_exempt
def stripe_webhook(request):
    """Обработка webhook от Stripe"""
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    # Проверка подписи
    stripe_service = StripePaymentService()
    event = stripe_service.verify_webhook_signature(payload, sig_header)
    
    if not event:
        return JsonResponse({'status': 'error'}, status=400)
    
    # Обработка events
    if event['type'] == 'payment_intent.succeeded':
        # Обновляем транзакцию
        payment_intent = event['data']['object']
        transaction = Transaction.objects.get(
            stripe_payment_intent_id=payment_intent['id']
        )
        transaction.complete()
    
    elif event['type'] == 'payment_intent.payment_failed':
        # Отмечаем как неудачную
        payment_intent = event['data']['object']
        transaction = Transaction.objects.get(
            stripe_payment_intent_id=payment_intent['id']
        )
        transaction.fail(payment_intent['last_payment_error']['message'])
    
    return JsonResponse({'status': 'success'})
```

## 🛡️ Безопасность webhook

### Проверка подписи (важно!)

Всегда проверяйте подпись события:

```python
def stripe_webhook(request):
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        # Подпись недействительна
        return JsonResponse({'status': 'error'}, status=400)
```

### Идемпотентность

Webhook может быть отправлен несколько раз. Используйте ID события для предотвращения дублирования:

```python
# В моделях
class WebhookEvent(models.Model):
    stripe_event_id = models.CharField(unique=True, max_length=255)
    processed = models.BooleanField(default=False)
    
# В webhook обработчике
webhook_event, created = WebhookEvent.objects.get_or_create(
    stripe_event_id=event['id']
)

if not webhook_event.processed:
    # Обработка события
    webhook_event.processed = True
    webhook_event.save()
```

## 📝 Возможные события для обработки

```python
# Платежные события
'payment_intent.succeeded'          # Платеж успешен
'payment_intent.payment_failed'     # Платеж отклонен
'payment_intent.canceled'            # Платеж отменен
'payment_intent.requires_action'     # Требуется 3D Secure

# Возвраты
'charge.refunded'                    # Платеж возвращен
'charge.dispute.created'             # Спор по платежу

# Подписки (если используются)
'customer.subscription.created'      # Подписка создана
'customer.subscription.updated'      # Подписка обновлена
'customer.subscription.deleted'      # Подписка отменена
```

## ✅ Чеклист webhook

- [ ] Stripe CLI установлен и авторизован
- [ ] Webhook URL тестируется локально с Stripe CLI
- [ ] STRIPE_WEBHOOK_SECRET установлен в .env
- [ ] Webhook endpoint регулярно проверяет логи
- [ ] Все события логируются для отладки
- [ ] Production webhook настроен в Stripe Dashboard
- [ ] Подпись события всегда проверяется
- [ ] Обработка событий идемпотентна
- [ ] Есть fallback для失败ных доставок событий

## 📞 Помощь

- [Stripe Webhooks Docs](https://stripe.com/docs/webhooks)
- [Stripe CLI Docs](https://stripe.com/docs/stripe-cli)
- [Webhook Events](https://stripe.com/docs/api/events)

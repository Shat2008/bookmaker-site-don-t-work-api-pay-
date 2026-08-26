# Stripe Integration Guide

## 🎯 Обзор

Приложение полностью интегрировано с Stripe для обработки международных платежей через кредитные карты.

## 📦 Установка

### 1. Установить пакеты
```bash
pip install -r requirements.txt
```

### 2. Получить ключи Stripe

1. Перейти на https://dashboard.stripe.com/apikeys
2. Скопировать:
   - **Publishable key** (начинается с `pk_test_`)
   - **Secret key** (начинается с `sk_test_`)
3. Скопировать **Webhook signing secret** для вебхуков

### 3. Конфигурация .env файла

```env
# Stripe Test Keys
STRIPE_PUBLIC_KEY=pk_test_your_key_here
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

### 4. Применить миграции

```bash
python manage.py migrate payments
```

## 🧪 Тестирование

### Тестовые карты Stripe

Используйте эти карты в тестовом режиме:

| Номер | Дата | CVC | Результат |
|-------|------|-----|-----------|
| 4242 4242 4242 4242 | Любая будущая дата | Любые 3 цифры | ✅ Успех |
| 4000 0000 0000 0002 | Любая будущая дата | Любые 3 цифры | ❌ Отклонение |
| 4000 0000 0000 9995 | Любая будущая дата | Любые 3 цифры | 🔐 Требует 3D Secure |

### Тестовый процесс

1. **Перейти на страницу пополнения**: `http://localhost:8000/payments/deposit/`
2. **Выбрать Stripe**: Выбрать опцию "💳 Stripe (Карта)"
3. **Ввести сумму и перейти к платежу**
4. **Использовать тестовую карту**: `4242 4242 4242 4242`
5. **Заполнить детали**:
   - Дата: Любая будущая (напр. 12/25)
   - CVC: Любые 3 цифры (напр. 123)
6. **Нажать "Оплатить"**

## 🔐 Безопасность

- ✅ **PCI Compliant**: Stripe Elements обеспечивает безопасность данных карт
- ✅ **No card data stored**: Номера карт не сохраняются в БД
- ✅ **HTTPS required**: Используется только на защищённых соединениях
- ✅ **Webhook verification**: Все события проверяются по подписи

## 📋 Структура

### Файлы интеграции:
- `payments/stripe_service.py` - Основной сервис для работы со Stripe
- `payments/views.py` - Представления для обработки платежей
- `payments/forms.py` - Формы для ввода данных платежа
- `payments/models.py` - Модель Transaction с полями Stripe
- `templates/payments/stripe_*.html` - Шаблоны для платежей

### URL маршруты:
- `POST /payments/deposit/` - Выбор способа пополнения
- `POST /payments/stripe-deposit/` - Форма ввода суммы Stripe
- `POST /payments/stripe-payment-confirm/` - Подтверждение платежа
- `POST /payments/webhook/stripe/` - Webhook для событий Stripe

## 🔄 Процесс платежа

```
1. User выбирает Stripe → /payments/stripe-deposit/
2. Form отправляется → views.stripe_deposit()
3. Создается Payment Intent в Stripe
4. Отображается Stripe Elements форма
5. User вводит карту и нажимает "Оплатить"
6. confirmCardPayment() отправляет на Stripe
7. На успех → /payments/stripe-payment-confirm/
8. Webhook подтверждает платеж
9. Транзакция завершена → баланс обновлен
```

## 💰 Преобразование валют

Stripe работает в центах (USD). Функции для преобразования:

```python
from payments.stripe_service import convert_to_cents, convert_from_cents

# 100 USD → 10000 центов
cents = convert_to_cents(100)  # 10000

# 10000 центов → 100 USD
dollars = convert_from_cents(10000)  # 100.0
```

## 🔧 Администрирование

В Django админке можно:
1. Просмотреть все транзакции
2. Отфильтровать по статусу
3. Посмотреть ID платежа в Stripe
4. Видеть статус платежа

```
/admin/payments/transaction/
```

## 📚 Документация

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Payment Intents](https://stripe.com/docs/payments/payment-intents)
- [Stripe Elements](https://stripe.com/docs/stripe-js/elements/payment-request-button)
- [Stripe Webhooks](https://stripe.com/docs/webhooks)

## 🚀 Production Development

Для production:

1. **Использовать live ключи** (начинаются с `pk_live_` и `sk_live_`)
2. **Настроить webhook** в https://dashboard.stripe.com/webhooks
3. **Включить HTTPS** - обязательно
4. **Установить SECRET_KEY** - используйте крепкий случайный ключ
5. **Отключить DEBUG** - `DEBUG=False` в production
6. **Использовать PostgreSQL** вместо SQLite
7. **Настроить ALLOWED_HOSTS** правильно

## 🐛 Troubleshooting

### Ошибка: "Invalid API Key"
- Проверьте, что STRIPE_SECRET_KEY установлен в .env
- Убедитесь, что ключи скопированы полностью без пробелов

### Ошибка: "Invalid webhook signature"
- Проверьте STRIPE_WEBHOOK_SECRET
- Убедитесь, что вебхук настроен на правильный URL

### Платеж создается, но не завершается
- Проверьте логи вебхука в Stripe Dashboard
- Убедитесь, что webhook доступен из интернета (используйте ngrok для тестирования)

## 📞 Поддержка

Для вопросов о Stripe - посетите https://support.stripe.com

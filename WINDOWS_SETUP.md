# 🚀 Запуск на Windows - Пошаговая инструкция

Полная инструкция для запуска приложения с Stripe интеграцией на Windows.

## 📋 Требования

- **Python** 3.8+ (https://www.python.org/downloads/)
- **pip** (идет с Python)
- **Git** (опционально, https://git-scm.com/)
- Интернет соединение

## ⚡ Быстрый старт (5 минут)

### Шаг 1: Откройте PowerShell

```powershell
# Нажмите Win + R, введите:
powershell

# Или откройте VS Code Terminal
```

### Шаг 2: Перейдите в папку проекта

```powershell
cd "C:\Users\lowke\OneDrive\Desktop\applications"

# Или просто:
cd ~/Desktop/applications
```

### Шаг 3: Создайте виртуальное окружение (важно!)

```powershell
python -m venv venv

# Активируйте окружение
.\venv\Scripts\Activate.ps1
```

Если ошибка `cannot be loaded because running scripts is disabled`:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Шаг 4: Установите пакеты

```powershell
pip install -r requirements.txt
```

Это займет 2-3 минуты...

### Шаг 5: Получите Stripe ключи

1. Откройте: https://dashboard.stripe.com/apikeys
2. Переключитесь на **Test Mode** (слева внизу)
3. Скопируйте:
   - **Publishable key** (начинается с pk_test_)
   - **Secret key** (начинается с sk_test_)

### Шаг 6: Создайте .env файл

```powershell
# Создайте файл .env
New-Item -Path .env -ItemType File

# Или откройте в блокноте:
notepad .env
```

Содержимое .env:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

STRIPE_PUBLIC_KEY=pk_test_your_key_here
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_test_secret_here

BANK_API_URL=https://api.bank.example
BANK_API_KEY=your_bank_api_key

SITE_URL=http://localhost:8000
```

### Шаг 7: Примените миграции

```powershell
python manage.py migrate
```

### Шаг 8: Запустите сервер

```powershell
python manage.py runserver
```

Вы должны увидеть:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Шаг 9: Откройте браузер

```
http://localhost:8000
```

## 🧪 Протестируйте платеж

### 1. Зарегистрируйтесь

```
URL: http://localhost:8000/users/register/
Username: testuser
Email: test@example.com
Password: TestPassword123!
```

### 2. Пополните счет

```
URL: http://localhost:8000/payments/deposit/
Способ: Stripe
Сумма: 50 USD
```

### 3. Используйте тестовую карту

```
Номер:   4242 4242 4242 4242
Дата:    12/25
CVC:     123
Имя:     Test User
```

### 4. Подтвердите платеж

Нажмите кнопку "Оплатить $50"

**Результат:** ✅ Платеж должен быть успешным!

## 🔔 Настройка Webhook (опционально для локального тестирования)

### Вариант 1: Stripe CLI (рекомендуется)

```powershell
# 1. Скачайте Stripe CLI
# https://github.com/stripe/stripe-cli/releases

# Или через Chocolatey:
choco install stripe-cli

# 2. Авторизуйтесь
stripe login

# 3. Слушайте webhook (в отдельном PowerShell)
stripe listen --forward-to localhost:8000/payments/webhook/stripe/

# 4. Скопируйте webhook secret
# whsec_test_1234567890...

# 5. Добавьте в .env
# STRIPE_WEBHOOK_SECRET=whsec_test_...
```

### Вариант 2: ngrok

```powershell
# 1. Установите ngrok
choco install ngrok

# 2. Запустите ngrok (в отдельном PowerShell)
ngrok http 8000

# 3. Скопируйте URL вида:
# https://xxxxx.ngrok.io

# 4. Добавьте в Stripe Dashboard:
# https://dashboard.stripe.com/webhooks
# Endpoint: https://xxxxx.ngrok.io/payments/webhook/stripe/
```

## 🆘 Решение проблем

### Проблема: "Python не найден"

```powershell
# Проверьте установку
python --version

# Если не работает, добавьте Python в PATH:
# 1. Установите Python заново
# 2. Отметьте "Add Python to PATH"
# 3. Перезагрузитесь
```

### Проблема: "Permission denied" при активации venv

```powershell
# Выполните в PowerShell как администратор:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Или используйте cmd вместо PowerShell
cmd
.\venv\Scripts\activate.bat
```

### Проблема: "Module not found"

```powershell
# Убедитесь, что окружение активировано:
.\venv\Scripts\Activate.ps1

# Переустановите пакеты:
pip install -r requirements.txt
```

### Проблема: "Invalid API Key"

```powershell
# Проверьте .env файл:
notepad .env

# Убедитесь, что:
# 1. STRIPE_PUBLIC_KEY скопирован полностью
# 2. STRIPE_SECRET_KEY скопирован полностью
# 3. Нет пробелов в начале/конце
# 4. Используете тестовые ключи (pk_test_, sk_test_)
```

### Проблема: Порт 8000 уже занят

```powershell
# Используйте другой порт:
python manage.py runserver 8001

# Или закройте процесс на порту 8000:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Проблема: "No module named 'stripe'"

```powershell
# Убедитесь, что окружение активировано:
.\venv\Scripts\Activate.ps1

# Переустановите stripe:
pip install stripe
```

## 📁 Структура папок

```
C:\Users\lowke\Desktop\applications\
│
├── venv/                    ← Виртуальное окружение
│   └── Scripts/
│       ├── python.exe
│       └── activate.ps1
│
├── payments/                ← Приложение платежей
│   ├── stripe_service.py
│   ├── views.py
│   ├── forms.py
│   ├── models.py
│   └── ...
│
├── templates/               ← HTML шаблоны
│   └── payments/
│       ├── stripe_payment.html
│       └── stripe_deposit.html
│
├── .env                     ← Ключи Stripe
├── manage.py                ← Django управление
├── requirements.txt         ← Пакеты
└── db.sqlite3              ← База данных
```

## 🛠️ Полезные команды

```powershell
# Активировать окружение
.\venv\Scripts\Activate.ps1

# Деактивировать окружение
deactivate

# Установить/обновить пакеты
pip install -r requirements.txt

# Запустить сервер
python manage.py runserver

# Запустить на другом порту
python manage.py runserver 8001

# Миграции
python manage.py migrate
python manage.py makemigrations
python manage.py showmigrations

# Django shell (для тестирования)
python manage.py shell

# Создать суперпользователя (админка)
python manage.py createsuperuser

# Очистить БД (осторожно!)
python manage.py flush

# Собрать static файлы
python manage.py collectstatic
```

## 📊 Ссылки для быстрого доступа

```
Django админка:        http://localhost:8000/admin/
Главная страница:      http://localhost:8000/
Пополнение:           http://localhost:8000/payments/deposit/
История платежей:     http://localhost:8000/payments/transactions/
Регистрация:          http://localhost:8000/users/register/
Вход:                 http://localhost:8000/users/login/

Stripe Dashboard:     https://dashboard.stripe.com/apikeys
Stripe Events:        https://dashboard.stripe.com/events
```

## 🎯 Первый платеж - Полная инструкция

### 1. Запустите сервер
```powershell
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

### 2. Откройте браузер
```
http://localhost:8000/users/register/
```

### 3. Создайте аккаунт
- Username: `testuser`
- Email: `test@gmail.com`
- Password: `TestPass123!`

### 4. Войдите в аккаунт

### 5. Перейдите на пополнение
```
http://localhost:8000/payments/deposit/
```

### 6. Заполните форму
- Способ оплаты: Stripe
- Сумма: 50 USD

### 7. Введите тестовую карту
- Номер: `4242 4242 4242 4242`
- Дата: `12/25`
- CVC: `123`

### 8. Нажмите "Оплатить"

### 9. Проверьте результат
- Баланс должен увеличиться на 50 USD ✅
- Транзакция должна быть в истории

## 🔒 Безопасность на локальном ПК

```powershell
# Никогда не коммитьте .env в Git:
echo ".env" >> .gitignore

# Не передавайте .env другим людям
# Не публикуйте ключи в интернете

# Используйте только тестовые ключи (pk_test_, sk_test_)
```

## 🚀 Переход на Production

Когда будете готовы к production:

1. **Получите live ключи** (pk_live_, sk_live_)
2. **Обновите .env** с live ключами
3. **Измените DEBUG** на False
4. **Включите HTTPS**
5. **Используйте PostgreSQL** вместо SQLite
6. **Разверните** на хостинге (Heroku, DigitalOcean и т.д.)

## 📞 Если что-то не работает

1. **Проверьте логи** - смотрите вывод в PowerShell
2. **Прочитайте документацию** - смотрите файлы STRIPE_*.md
3. **Тестовые ключи** - используйте pk_test_, sk_test_
4. **Stripe Support** - https://support.stripe.com

## ✅ Готово!

Ваша система платежей работает! 🎉

Начните с тестирования на локальном ПК, потом переходите на production.

---

**Версия:** 1.0  
**Обновлено:** January 10, 2026  
**Для:** Windows (PowerShell / CMD)

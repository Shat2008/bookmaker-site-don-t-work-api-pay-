import stripe
import os
from django.conf import settings

# Инициализация Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripePaymentService:
    """Сервис для работы с платежами через Stripe"""
    
    def __init__(self):
        self.public_key = settings.STRIPE_PUBLIC_KEY
        self.secret_key = settings.STRIPE_SECRET_KEY
        stripe.api_key = self.secret_key
    
    def create_customer(self, user):
        """Создание клиента в Stripe"""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.get_full_name() or user.username,
                metadata={
                    'user_id': user.id,
                    'username': user.username,
                }
            )
            return customer
        except stripe.error.StripeError as e:
            print(f"Ошибка при создании клиента Stripe: {str(e)}")
            return None
    
    def create_payment_intent(self, user, amount, currency='usd', description=''):
        """
        Создание Intent платежа для безопасной обработки платежа
        amount в центах (100 = 1 USD)
        """
        try:
            # Получаем или создаем клиента
            customer_id = getattr(user, 'stripe_customer_id', None)
            
            if not customer_id:
                customer = self.create_customer(user)
                if customer:
                    customer_id = customer.id
                    # Сохраняем ID в пользователя если поле существует
                    if hasattr(user, 'stripe_customer_id'):
                        user.stripe_customer_id = customer_id
                        user.save()
            
            # Создаем Payment Intent
            intent = stripe.PaymentIntent.create(
                amount=int(amount),  # Сумма в центах
                currency=currency,
                customer=customer_id,
                description=description or f"Deposit for {user.username}",
                metadata={
                    'user_id': user.id,
                    'username': user.username,
                    'transaction_type': 'deposit',
                }
            )
            return intent
        except stripe.error.StripeError as e:
            print(f"Ошибка при создании Payment Intent: {str(e)}")
            return None
    
    def create_setup_intent(self, user):
        """Создание Setup Intent для сохранения платежного метода"""
        try:
            customer_id = getattr(user, 'stripe_customer_id', None)
            
            if not customer_id:
                customer = self.create_customer(user)
                customer_id = customer.id if customer else None
            
            if customer_id:
                setup_intent = stripe.SetupIntent.create(
                    customer=customer_id,
                    usage='off_session',
                    metadata={
                        'user_id': user.id,
                    }
                )
                return setup_intent
        except stripe.error.StripeError as e:
            print(f"Ошибка при создании Setup Intent: {str(e)}")
            return None
    
    def confirm_payment_intent(self, payment_intent_id):
        """Подтверждение платежа"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return intent
        except stripe.error.StripeError as e:
            print(f"Ошибка при получении Payment Intent: {str(e)}")
            return None
    
    def get_payment_intent_status(self, payment_intent_id):
        """Получение статуса платежа"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'status': intent.status,
                'client_secret': intent.client_secret,
                'amount': intent.amount,
                'currency': intent.currency,
            }
        except stripe.error.StripeError as e:
            print(f"Ошибка при получении статуса: {str(e)}")
            return None
    
    def list_payment_methods(self, customer_id):
        """Получение списка сохраненных способов оплаты"""
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type="card"
            )
            return payment_methods.get('data', [])
        except stripe.error.StripeError as e:
            print(f"Ошибка при получении методов оплаты: {str(e)}")
            return []
    
    def refund_payment(self, charge_id, amount=None):
        """Возврат платежа (полный или частичный)"""
        try:
            refund_params = {'charge': charge_id}
            if amount:
                refund_params['amount'] = int(amount)  # в центах
            
            refund = stripe.Refund.create(**refund_params)
            return refund
        except stripe.error.StripeError as e:
            print(f"Ошибка при возврате платежа: {str(e)}")
            return None
    
    def verify_webhook_signature(self, payload, sig_header):
        """Проверка подписи webhook от Stripe"""
        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except stripe.error.SignatureVerificationError as e:
            print(f"Ошибка при проверке подписи webhook: {str(e)}")
            return None
        except ValueError as e:
            print(f"Ошибка при разборе webhook: {str(e)}")
            return None


# Функции-помощники
def convert_to_cents(amount):
    """Конвертирует сумму в центы"""
    return int(float(amount) * 100)


def convert_from_cents(amount_cents):
    """Конвертирует центы в сумму"""
    return float(amount_cents) / 100

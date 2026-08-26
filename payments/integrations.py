import requests
import hmac
import hashlib
import json
from django.conf import settings

class BankIntegration:
    """Интеграция с банковской системой"""
    
    def __init__(self):
        self.api_url = settings.BANK_API_URL
        self.api_key = settings.BANK_API_KEY
    
    def create_payment(self, user_id, amount, description):
        """
        Создание платежа в банковской системе
        В реальном проекте здесь будет интеграция с реальным банком
        """
        try:
            # Тестовый ответ (в реальном проекте замените на реальный API запрос)
            payment_data = {
                'success': True,
                'payment_id': f"test_{user_id}_{int(amount)}_{hashlib.md5(str(user_id).encode()).hexdigest()[:8]}",
                'payment_url': '/payments/success/',
                'amount': amount,
                'status': 'created',
            }
            
            return payment_data
            
        except Exception as e:
            print(f"Ошибка создания платежа: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_webhook(self, payload, signature):
        """
        Верификация вебхука от банка
        В реальном проекте используйте реальную проверку подписи
        """
        # Тестовая проверка (в реальном проекте используйте HMAC)
        expected_signature = hmac.new(
            self.api_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def get_payment_status(self, payment_id):
        """
        Проверка статуса платежа
        """
        try:
            # Тестовый ответ
            return {
                'success': True,
                'status': 'completed',
                'payment_id': payment_id,
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
import hashlib
import json
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from .models import Transaction
from django.contrib.auth.decorators import login_required
from django.utils import timezone


def _format_amount(amount):
    """Fondy expects amount in cents (integer)."""
    return int(round(float(amount) * 100))


def _fondy_generate_signature_from_dict(data: dict, secret: str) -> str:
    """Generate Fondy-style SHA1 signature from dict of values.

    Algorithm: take keys except 'signature', sort them alphabetically,
    join their values with '|' in that order, prefix with secret + '|' and
    return sha1 hex digest.

    This matches the common Fondy method; if your merchant account
    requires a different order, adjust accordingly.
    """
    items = []
    for k in sorted(data.keys()):
        if k == 'signature':
            continue
        v = data.get(k)
        # skip empty values
        if v is None:
            v = ''
        items.append(str(v))

    signature_raw = secret + '|' + '|'.join(items)
    return hashlib.sha1(signature_raw.encode('utf-8')).hexdigest()


@login_required
def fondy_deposit(request):
    """Инициация пополнения через Fondy: создаёт транзакцию и возвращает форму для редиректа."""
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if not amount:
            return JsonResponse({'status': 'error', 'message': 'Amount required'}, status=400)

        order_id = f"fondy-{int(timezone.now().timestamp())}-{request.user.id}"
        transaction = Transaction.objects.create(
            user=request.user,
            transaction_type='deposit',
            amount=float(amount),
            payment_method='fondy',
            external_id=order_id,
            description=f"Fondy deposit {amount} for {request.user.username}",
            status='pending',
        )

        # Fondy parameters
        data = {
            'order_id': order_id,
            'merchant_id': settings.FONDY_MERCHANT_ID,
            'amount': _format_amount(amount),
            'currency': 'UAH',
            'server_callback_url': f"{settings.SITE_URL}/payments/webhook/fondy/",
            'response_url': f"{settings.SITE_URL}/payments/success/?payment_id={transaction.id}",
            'description': f"Пополнение счета #{transaction.id}",
        }

        # Signature generation: Fondy требует контрольную подпись. Реализация зависит от версии API.
        # Ниже — простой пример формирования SHA1 подписи по значениям полей в определённом порядке.
        # Проверьте документацию Fondy и при необходимости скорректируйте порядок/алгоритм.
        values = [str(data.get('merchant_id', '')), str(data.get('order_id', '')), str(data.get('amount', ''))]
        signature_raw = settings.FONDY_SECRET + '|' + '|'.join(values)
        signature = hashlib.sha1(signature_raw.encode('utf-8')).hexdigest()
        data['signature'] = signature

        # Рендерим простую HTML-форму, которая автоматически отправит данные на Fondy
        return render(request, 'payments/fondy_redirect.html', {'fondy_url': settings.FONDY_CHECKOUT_URL, 'data': data})

    # GET — показываем форму пополнения
    return render(request, 'payments/fondy_deposit_form.html')


@csrf_exempt
def fondy_webhook(request):
    """Обработка callback'а от Fondy. Важно: добавить валидацию подписи по документации Fondy."""
    if request.method not in ('POST',):
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    # Fondy может отправлять application/x-www-form-urlencoded или JSON
    payload = request.POST.dict() if request.POST else {}
    if not payload:
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except Exception:
            payload = {}

    # TODO: Проверить подпись payload['signature'] с использованием settings.FONDY_SECRET
    # Проверка подписи
    received_sig = payload.get('signature')
    if received_sig:
        try:
            calc_sig = _fondy_generate_signature_from_dict(payload, settings.FONDY_SECRET)
            if calc_sig != received_sig:
                return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=400)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Signature verification error'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Signature missing'}, status=400)

    order_id = payload.get('order_id') or payload.get('orderId') or payload.get('merchant_data')
    status = payload.get('order_status') or payload.get('status')

    if not order_id:
        return JsonResponse({'status': 'error', 'message': 'order_id missing'}, status=400)

    try:
        transaction = Transaction.objects.get(external_id=order_id)
    except Transaction.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Transaction not found'}, status=404)

    if status in ('approved', 'success', 'completed'):
        transaction.complete({'fondy': payload})
        return JsonResponse({'status': 'success'})
    else:
        transaction.fail({'fondy': payload})
        return JsonResponse({'status': 'error', 'message': 'Payment failed'})
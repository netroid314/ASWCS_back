from credit.views import create_credit_log
from datetime import date, datetime, time
from django.core.exceptions import ImproperlyConfigured
from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import datetime
from django.urls import reverse
from django.conf import settings
from django.utils.safestring import mark_safe
from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from payment.iamport_rest import IamportRest
from credit.models import CreditLog
import json

User=get_user_model()

def get_payment_model():
    try:
        return django_apps.get_model(settings.PAYMENT_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("PAYMENT_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "AUTH_USER_MODEL refers to model '%s' that has not been installed" % settings.PAYMENT_MODEL
        )


def pay(request, payment_id):
    payment = get_object_or_404(get_payment_model(), pk=payment_id)

    payment_data = settings.PAYMENT_CONFIG.copy()
    payment_data.update({
        'merchant_uid' : payment.uid,
        'name' : payment.name,
        'amount' : payment.amount,
        'buyer_email' : payment.buyer_email or '',
        'buyer_name' : payment.buyer_name or '',
        'buyer_tel' : payment.buyer_tel or '',
        #'buyer_addr' : payment.buyer_addr or '',
        #'buyer_postcode' : payment.buyer_postcode or '',
        'm_redirect_url' : reverse('payment:update', args=[payment.pk, ])
    })

    iamport = IamportRest()
    iamport.auth()
    iamport.prepare(payment.uid, payment.amount)

    return render(request, 'payment/summary.html', {
        'payment_data_json': mark_safe(json.dumps(payment_data, ensure_ascii=False)),
        'payment_data': payment_data,
        'payment': payment,
        'merchant_id': settings.PAYMENT_MERCHANT_ID
    })


def update(request, payment_id):
    payment = get_object_or_404(get_payment_model(), pk=payment_id)

    imp_uid = request.GET.get('imp_uid', None)
    mct_uid = request.GET.get('merchant_uid', None)

    if not imp_uid or not mct_uid or payment.uid != mct_uid:
        raise Http404()

    iamport = IamportRest()
    iamport.auth()
    pay_result = iamport.payment(imp_uid)

    if pay_result['status'] == 'failed':
        payment.pay_result = 'failed'
        payment.imp_result = pay_result['fail_reason']
        payment.save()

    elif pay_result['status'] == 'paid':
        if pay_result['amount'] != payment.amount:
            iamport.cancel(imp_uid, payment.uid, '????????? ??????(????????????)')
            payment.pay_result = 'error'
            payment.imp_result = '????????? ??????'
            payment.save()
        else:
            payment.pay_result = 'success'
            payment.imp_result = '?????? ??????'
            payment.confirmed_at = timezone.now()
            payment.imp_uid = pay_result['imp_uid']
            payment.pg_tid = pay_result['pg_tid']
            payment.card_id = pay_result['apply_num']
            payment.receipt_url = pay_result['receipt_url']
            payment.on_success()
            payment.save()

    else:
        payment.pay_result = 'error'
        payment.imp_result = '?????? ??????'
        payment.save()

    return HttpResponseRedirect(reverse('payment:result', args=[payment.pk]))


def result(request, payment_id):
    payment = get_object_or_404(get_payment_model(), pk=payment_id)
    userKey=payment.order.userKey
    user = User.objects.get(key=userKey)
    if payment.pay_result == 'success':
        create_credit_log(1,userKey,payment.amount)

    home_url = payment.get_home_url() or '/'
    retry_url = payment.get_retry_url()

    return render(request, 'payment/result.html', {'payment': payment, 'home_url': home_url, 'retry_url': retry_url})

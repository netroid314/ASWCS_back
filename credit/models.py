from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
#iamport
from credit.iamport import validation_prepare, get_Payment
import time
import random
import hashlib
from django.db.models.signals import post_save

User=get_user_model()

class CreditLog(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    action=models.CharField(max_length=10,null=True, blank=True)
    details=models.TextField(null=True, blank=True)
    amount=models.IntegerField(null=True, blank=True)
    date=models.DateTimeField(default=timezone.now())

class CreditStatus(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    credit = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    timestamp = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return str(self.credit)

class CreditPayment(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=120, null=True, blank=True)
    order_id = models.CharField(max_length=120, unique=True)
    amount = models.PositiveIntegerField(default=0)
    success = models.BooleanField(default=False)
    payment_status = models.CharField(max_length=220, null=True, blank=True)
    type = models.CharField(max_length=120)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        return self.order_id

    class Meta:
        ordering = ['-created']

class PaymentManager(models.Manager):
    # 새로운 결제 생성
    def create_new(self, user, amount, type, success=None, transaction_status=None):
        if not user:
            raise ValueError("유저가 확인되지 않습니다.")
        short_hash = hashlib.sha1(str(random.random())).hexdigest()[:2]
        time_hash = hashlib.sha1(str(int(time.time()))).hexdigest()[-3:]
        base = str(user.email).split("@")[0]
        key = hashlib.sha1(short_hash + time_hash + base).hexdigest()[:10]
        new_order_id = "%s" % (key)

        # 아임포트 결제 사전 검증 단계
        validation_prepare(new_order_id, amount)

        # 결제 저장
        new_pay = self.model(
            user=user,
            order_id=new_order_id,
            amount=amount,
            type=type
        )

        if success is not None:
            new_pay.success = success
            new_pay.transaction_status = transaction_status

        new_pay.save(using=self._db)
        return new_pay.order_id

    # 생성된 결제 검증
    def validation_pay(self, merchant_id):
        result = get_Payment(merchant_id)

        if result['status'] is not 'paid':
            return result
        else:
            return None

    def all_for_user(self, user):
        return super(PaymentManager, self).filter(user=user)

    def get_recent_user(self, user, num):
        return super(PaymentManager, self).filter(user=user)[:num]

def new_credit_trans_validation(sender, instance, created, *args, **kwargs):
    if instance.transaction_id:
        # 거래 후 아임포트에서 넘긴 결과
        v_trans = PointTransaction.objects.validation_trans(
            merchant_id=instance.order_id
        )

        res_merchant_id = v_trans['merchant_id']
        res_imp_id = v_trans['imp_id']
        res_amount = v_trans['amount']

        # 데이터베이스에 실제 결제된 정보가 있는지 체크
        r_trans = PointTransaction.objects.filter(
            order_id=res_merchant_id,
            transaction_id=res_imp_id,
            amount=res_amount
        ).exists()

        if not v_trans or not r_trans:
            raise ValueError('비정상적인 거래입니다.')


post_save.connect(new_credit_trans_validation, sender=CreditPayment)

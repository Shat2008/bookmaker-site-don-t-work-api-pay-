# Generated migration for Stripe integration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='stripe_payment_intent_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Stripe Payment Intent ID'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='stripe_charge_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Stripe Charge ID'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['stripe_payment_intent_id'], name='payments_tr_stripe_p_idx'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='payment_method',
            field=models.CharField(blank=True, choices=[('card', 'Банковская карта'), ('stripe', 'Stripe'), ('qiwi', 'QIWI'), ('yoomoney', 'ЮMoney'), ('webmoney', 'WebMoney'), ('crypto', 'Криптовалюта'), ('bank_transfer', 'Банковский перевод')], max_length=50, verbose_name='Способ оплаты'),
        ),
    ]

from datetime import datetime
from api.models import CurrencyRate, UserCurrency


def normalize_iso_date(date_iso8601: str) -> str:
    # Получаем дату в формате ISO 8601
    if date_iso8601:
        date_parts = date_iso8601.split("T")  # Преобразуем дату из ISO 8601 в формат "YYYY-MM-DD"
        date_only = date_parts[0]  # дату в формате "YYYY-MM-DD"
    else:
        date_only = datetime.now().strftime("%Y-%m-%d")
    return date_only


def currency_create(items: dict, date: str):
    try:
        currency_rate = CurrencyRate(
            currency_id=items["ID"],
            num_code=items["NumCode"],
            char_code=items["CharCode"],
            nominal=items["Nominal"],
            name=items["Name"],
            value=items["Value"],
            previous=items["Previous"],
            date=date
        )
        currency_rate.save()
    except Exception as e:
        print("currency_create > Exception...", e.args)


def checks_threshold_and_email_sending():
    from api.tasks import send_threshold_user_email

    # проверки ПЗ и отправки email с асинхронный функциями (Celery)
    for item in UserCurrency.objects.all():
        latest_rate = CurrencyRate.objects.filter(currency_id=item.currency_id).latest('date')
        if latest_rate.value > item.threshold:
            send_threshold_user_email.apply_async((item.user.email, item.currency_id, item.threshold), countdown=3)

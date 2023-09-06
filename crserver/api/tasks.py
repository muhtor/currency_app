from celery import shared_task
import requests
from pytz import timezone
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from api.services.utils import normalize_iso_date, currency_create, checks_threshold_and_email_sending


@shared_task
def load_daily_exchange_rates():

    api_url = 'https://www.cbr-xml-daily.ru/daily_json.js'  # URL для API ЦБ РФ

    # Получит текущую дату и время в московском времени
    moscow_time = datetime.now(timezone('Europe/Moscow'))

    # check time 12:00 мск
    if moscow_time.hour == 12 and moscow_time.minute == 0:
        # запрос к API ЦБ РФ для загрузки котировок
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            date_only = normalize_iso_date(date_iso8601=data.get("Date", None))
            # Сохранение данных в базу данных
            for currency_code, currency_data in data['Valute'].items():
                currency_create(items=currency_data, date=date_only)

            checks_threshold_and_email_sending()  # проверки пороговое значение


@shared_task
def send_threshold_user_email(email, currency_id, threshold):
    subject = 'Превышено пороговое значение котировок'
    message = f'Уважаемый {email},\n\n'
    message += 'Следующие котируемые валюты превысили ваши пороговые значения:\n'
    message += f'- {currency_id}: {threshold}\n'
    message += '\nС уважением,\nВаш менеджер по отслеживанию курсов валют'
    send_mail(subject, message, settings.EMAIL_FROM, [email])

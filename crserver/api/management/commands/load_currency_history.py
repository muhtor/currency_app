from django.core.management.base import BaseCommand
import requests
from datetime import datetime, timedelta
from api.services.utils import normalize_iso_date, currency_create


class Command(BaseCommand):
    help = 'Load currency history from archive API'

    def handle(self, *args, **kwargs):
        api_url = 'https://www.cbr-xml-daily.ru/daily_json.js'  # URL для API ЦБ РФ

        # начальную и конечную даты для загрузки данных
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        # Проход по датам и загрузка данных
        current_date = start_date
        while current_date <= end_date:
            response = requests.get(api_url, params={'date': current_date})  # запрос к API ЦБ РФ для загрузки котировок
            if response.status_code == 200:
                data = response.json()
                date_only = normalize_iso_date(date_iso8601=data.get("Date", None))
                # Сохранение данных в базу данных
                for currency_code, currency_data in data['Valute'].items():
                    currency_create(items=currency_data, date=date_only)
            else:
                self.stdout.write(self.style.ERROR(f'Failed to fetch data for {current_date}'))

            # Переход к следующей дате
            current_date += timedelta(days=1)
        self.stdout.write(self.style.SUCCESS(f'Successfully loaded currency history for {current_date}'))

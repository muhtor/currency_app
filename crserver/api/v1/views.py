from django.utils.timezone import make_aware
from datetime import datetime
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, generics
from rest_framework.response import Response
from .serializers import (
    RegisterSerializer,
    UserCurrencyAddSerializer,
    CurrencyRateSerializer,
    CurrencyRate,
    AnalyticCurrencyRateSerializer
)


class UserCreateAPIView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    tags = ["Register API"]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)


class UserCurrencyAddView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserCurrencyAddSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrencyRateListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CurrencyRateSerializer

    @method_decorator(cache_page(60))
    def dispatch(self, *args, **kwargs):
        return super(CurrencyRateListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        order_by = self.request.query_params.get('order_by')
        if user.is_authenticated:
            # котировки для отслеживаемых валют текущего пользователя
            user_currency_id__in = user.usercurrency_set.values_list('currency_id', flat=True)
            queryset = CurrencyRate.objects.filter(
                currency_id__in=user_currency_id__in
            )
        else:
            queryset = CurrencyRate.objects.all()
            print("Q...", queryset)

        # сортировку by asc/desc
        if order_by == 'asc':
            queryset = queryset.order_by('value')
        elif order_by == 'desc':
            queryset = queryset.order_by('-value')

        return queryset


class AnalyticCurrencyRateListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnalyticCurrencyRateSerializer

    def get_queryset(self):
        date_from_str = self.request.query_params.get('date_from')
        date_to_str = self.request.query_params.get('date_to')

        date_from = make_aware(datetime.strptime(date_from_str, '%Y-%m-%d'))  # из строки в объекты datetime
        date_to = make_aware(datetime.strptime(date_to_str, '%Y-%m-%d'))  # из строки в объекты datetime
        queryset = CurrencyRate.objects.filter(
            # currency_id=currency_id,
            id=self.kwargs['id'],
            date__gte=date_from,
            date__lte=date_to
        )
        return queryset




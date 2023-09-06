from rest_framework import serializers
from ..models import User, CurrencyRate, UserCurrency
from rest_framework.validators import UniqueValidator, ValidationError
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    """Serializes registration requests and creates a new user."""

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    # password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        extra_kwargs = {'password': {'write_only': True}}
        fields = ('email', 'password')

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserCurrencyAddSerializer(serializers.Serializer):
    currency = serializers.CharField(max_length=10, required=True)  # ID котируемой валюты
    threshold = serializers.DecimalField(max_digits=10, decimal_places=4, min_value=1)

    def create(self, validated_data):
        user = self.context['request'].user
        currency_id = validated_data['currency']
        threshold = validated_data['threshold']

        user_currency = UserCurrency.objects.filter(user=user, currency_id=currency_id).first()
        if user_currency:
            # обновит пороговое значение
            user_currency.threshold = threshold
            user_currency.save()
        else:
            # создат новую
            user_currency = UserCurrency(user=user, currency_id=currency_id, threshold=threshold)
            user_currency.save()
        return user_currency


class CurrencyRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyRate
        fields = '__all__'


class AnalyticCurrencyRateSerializer(serializers.ModelSerializer):
    exceeded_threshold = serializers.SerializerMethodField()

    class Meta:
        model = CurrencyRate
        fields = '__all__'

    def get_exceeded_threshold(self, obj):
        request = self.context['request']
        threshold = float(request.query_params.get('threshold'))
        return obj.value > threshold

    def to_representation(self, instance: CurrencyRate):
        data = super().to_representation(instance)
        user_currency = UserCurrency.objects.filter(user=self.context['request'].user).first()
        if user_currency:
            threshold = user_currency.threshold
            percentage = (instance.value / threshold) * 100
        else:
            threshold = float(0.0)
            percentage = 0

        if instance.value > threshold:
            data['threshold_status'] = "превысило"
        elif instance.value == threshold:
            data['threshold_status'] = "равно"
        else:
            data['threshold_status'] = "меньше"

        max_rate = CurrencyRate.objects.filter(currency_id=instance.currency_id).order_by('-value').first()
        min_rate = CurrencyRate.objects.filter(currency_id=instance.currency_id).order_by('value').first()
        data['is_max_value'] = instance == max_rate
        data['is_min_value'] = instance == min_rate
        data['percentage_ratio'] = round(percentage, 2)  # Округляем до двух знаков после запятой

        return data




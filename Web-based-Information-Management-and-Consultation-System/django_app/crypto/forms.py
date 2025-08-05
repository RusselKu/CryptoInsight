from django import forms

class CryptoMarketForm(forms.Form):
    symbol = forms.CharField(max_length=20, required=True)
    price = forms.FloatField(required=True)
    volume = forms.FloatField(required=False)
    last_updated = forms.DateTimeField(required=False)

    def save(self, instance=None):
        data = self.cleaned_data
        if instance is None:
            from .models import CryptoMarket
            instance = CryptoMarket()
        instance.symbol = data['symbol']
        instance.price = data['price']
        instance.volume = data.get('volume', 0)
        instance.last_updated = data.get('last_updated')
        instance.save()
        return instance

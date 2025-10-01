from django import forms
from .models import Product

# Список запрещенных слов из задания
FORBIDDEN_WORDS = [
    'казино',
    'криптовалюта',
    'крипта',
    'биржа',
    'дешево',
    'бесплатно',
    'обман',
    'полиция',
    'радар',
]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price']  # 👈 Добавили price
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
        }
        labels = {
            'name': 'Название продукта',
            'description': 'Описание продукта',
            'price': 'Цена продукта',
        }

    def clean_price(self):
        """
        Кастомная валидация для поля price - проверка на отрицательные значения
        """
        price = self.cleaned_data.get('price')

        if price is not None and price < 0:
            raise forms.ValidationError("Цена не может быть отрицательной.")

        return price

    def clean(self):
        """
        Валидация на запрещенные слова
        """
        cleaned_data = super().clean()
        name = cleaned_data.get('name', '').lower()
        description = cleaned_data.get('description', '').lower()

        # Проверяем каждое запрещенное слово
        for word in FORBIDDEN_WORDS:
            if word in name or word in description:
                raise forms.ValidationError(
                    f"Ошибка: использование слова '{word}' запрещено в названии или описании товара."
                )

        return cleaned_data

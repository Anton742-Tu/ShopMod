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
        fields = ['name', 'description', 'price']

    def __init__(self, *args, **kwargs):
        """
        Стилизация формы через метод __init__
        """
        super().__init__(*args, **kwargs)

        # Базовые CSS классы для всех полей
        base_css_class = 'form-control'

        # Стилизация каждого поля
        self.fields['name'].widget.attrs.update({
            'class': base_css_class,
            'placeholder': 'Введите название товара',
            'autofocus': True
        })

        self.fields['description'].widget.attrs.update({
            'class': f'{base_css_class} form-control-lg',
            'placeholder': 'Опишите товар (необязательно)',
            'rows': 4
        })

        self.fields['price'].widget.attrs.update({
            'class': base_css_class,
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0'
        })

        # Кастомные лейблы с иконками
        self.fields['name'].label = '📝 Название товара'
        self.fields['description'].label = '📄 Описание товара'
        self.fields['price'].label = '💰 Цена товара'

        # Добавляем подсказки для полей
        self.fields['name'].help_text = 'Укажите краткое и понятное название'
        self.fields['description'].help_text = 'Можно добавить характеристики, особенности товара'
        self.fields['price'].help_text = 'Цена в рублях. Отрицательные значения не допускаются'

    def clean_price(self):
        """
        Кастомная валидация для поля price - проверка на отрицательные значения
        """
        price = self.cleaned_data.get('price')

        if price is not None and price < 0:
            raise forms.ValidationError("❌ Цена не может быть отрицательной.")

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
                    f"🚫 Ошибка: использование слова '{word}' запрещено в названии или описании товара."
                )

        return cleaned_data

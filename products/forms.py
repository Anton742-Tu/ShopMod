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
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'name': 'Название продукта',
            'description': 'Описание продукта',
        }

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

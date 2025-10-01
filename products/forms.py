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
        fields = ['name', 'description']  # Укажи все поля, которые нужно выводить в форме
        # Можно добавить виджеты для красоты, но это опционально
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        """
        Метод для валидации всех данных формы.
        Вызывается автоматически при вызове form.is_valid().
        """
        cleaned_data = super().clean() # Получаем базово очищенные данные
        name = cleaned_data.get('name', '').lower() # Приводим к нижнему регистру
        description = cleaned_data.get('description', '').lower()

        # Проверяем каждое запрещенное слово
        for word in FORBIDDEN_WORDS:
            if word in name or word in description:
                # Используем более общее сообщение об ошибке
                raise forms.ValidationError(
                    f"Использование запрещенного слова '{word}' в названии или описании недопустимо."
                )

        # Если все ок, возвращаем очищенные данные
        return cleaned_data

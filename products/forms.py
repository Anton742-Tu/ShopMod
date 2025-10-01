import os

from django import forms

from .models import Product

# Список запрещенных слов из задания
FORBIDDEN_WORDS = [
    "казино",
    "криптовалюта",
    "крипта",
    "биржа",
    "дешево",
    "бесплатно",
    "обман",
    "полиция",
    "радар",
]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "image"]

    def __init__(self, *args, **kwargs):
        """
        Стилизация формы через метод __init__
        """
        super().__init__(*args, **kwargs)

        # Базовые CSS классы для всех полей
        base_css_class = "form-control"

        # Стилизация каждого поля
        self.fields["name"].widget.attrs.update(
            {
                "class": base_css_class,
                "placeholder": "Введите название товара",
                "autofocus": True,
            }
        )

        self.fields["description"].widget.attrs.update(
            {
                "class": f"{base_css_class} form-control-lg",
                "placeholder": "Опишите товар (необязательно)",
                "rows": 4,
            }
        )

        self.fields["price"].widget.attrs.update(
            {
                "class": base_css_class,
                "placeholder": "0.00",
                "step": "0.01",
                "min": "0",
            }
        )

        self.fields["image"].widget.attrs.update(
            {
                "class": "form-control",
                "accept": "image/jpeg,image/png,image/jpg",
            }
        )

        # Кастомные лейблы с иконками
        self.fields["name"].label = "📝 Название товара"
        self.fields["description"].label = "📄 Описание товара"
        self.fields["price"].label = "💰 Цена товара"
        self.fields["image"].label = "🖼️ Изображение товара"

        # Добавляем подсказки для полей
        self.fields["name"].help_text = "Укажите краткое и понятное название"
        self.fields["description"].help_text = (
            "Можно добавить характеристики, особенности товара"
        )
        self.fields["price"].help_text = (
            "Цена в рублях. Отрицательные значения не допускаются"
        )
        self.fields["image"].help_text = "Форматы: JPEG, PNG. Максимальный размер: 5 МБ"

    def clean_image(self):
        """
        Валидация загружаемого изображения
        """
        image = self.cleaned_data.get("image")

        # Если изображение не загружено - пропускаем валидацию
        if not image:
            return image

        # Проверка формата файла
        valid_extensions = [".jpg", ".jpeg", ".png"]
        ext = os.path.splitext(image.name)[1].lower()

        if ext not in valid_extensions:
            raise forms.ValidationError("❌ Поддерживаются только форматы JPEG и PNG.")

        # Проверка размера файла (5 МБ = 5 * 1024 * 1024 байт)
        max_size = 5 * 1024 * 1024
        if image.size > max_size:
            raise forms.ValidationError(
                f"❌ Размер файла не должен превышать 5 МБ. Ваш файл: {image.size // 1024 // 1024} МБ"
            )

        # Проверка MIME-type для дополнительной безопасности
        valid_mime_types = ["image/jpeg", "image/png", "image/jpg"]
        if (
            hasattr(image, "content_type")
            and image.content_type not in valid_mime_types
        ):
            raise forms.ValidationError(
                "❌ Недопустимый тип файла. Разрешены только JPEG и PNG."
            )

        return image

    def clean_price(self):
        """
        Кастомная валидация для поля price - проверка на отрицательные значения
        """
        price = self.cleaned_data.get("price")

        if price is not None and price < 0:
            raise forms.ValidationError("❌ Цена не может быть отрицательной.")

        return price

    def clean(self):
        """
        Валидация на запрещенные слова
        """
        cleaned_data = super().clean()
        name = cleaned_data.get("name", "").lower()
        description = cleaned_data.get("description", "").lower()

        # Проверяем каждое запрещенное слово
        for word in FORBIDDEN_WORDS:
            if word in name or word in description:
                raise forms.ValidationError(
                    f"🚫 Ошибка: использование слова '{word}' запрещено в названии или описании товара."
                )

        return cleaned_data

from django import forms

from .models import BlogPost


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ["title", "content", "image", "status"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите заголовок статьи",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 10,
                    "placeholder": "Напишите содержание статьи...",
                }
            ),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["title"].label = "📝 Заголовок"
        self.fields["content"].label = "📄 Содержание"
        self.fields["image"].label = "🖼️ Изображение"
        self.fields["status"].label = "📢 Статус"

        self.fields["title"].help_text = "Придумайте catchy-заголовок"
        self.fields["content"].help_text = "Основное содержание статьи"
        self.fields["image"].help_text = "Главное изображение статьи (необязательно)"

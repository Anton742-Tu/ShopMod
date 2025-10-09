from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_welcome_email(user_email, username):
    """Отправка приветственного письма после регистрации"""

    subject = "Добро пожаловать в ShopMod! 🛍️"

    html_message = render_to_string(
        "users/emails/welcome_email.html",
        {
            "username": username,
            "user_email": user_email,
        },
    )

    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Ошибка отправки email: {e}")
        return False

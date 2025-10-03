import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from products.views import HomeView


def test_auth():
    print("🧪 Testing authentication...")

    # Создаем тестовый запрос
    factory = RequestFactory()
    request = factory.get('/')

    # Добавляем middleware
    session_middleware = SessionMiddleware(lambda x: None)
    auth_middleware = AuthenticationMiddleware(lambda x: None)

    # Обрабатываем запрос через middleware
    session_middleware.process_request(request)
    auth_middleware.process_request(request)

    print(f"User: {request.user}")
    print(f"Authenticated: {request.user.is_authenticated}")
    print(f"Session: {request.session.session_key}")

    # Тестируем представление
    view = HomeView()
    view.request = request
    context = view.get_context_data()

    print(f"Context user: {context.get('user')}")
    print(f"Context authenticated: {context.get('user').is_authenticated if context.get('user') else 'No user'}")


if __name__ == "__main__":
    test_auth()
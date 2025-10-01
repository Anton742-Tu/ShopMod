from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import UserLoginForm, UserProfileForm, UserRegisterForm
from .models import User
from .utils import send_welcome_email


class RegisterView(CreateView):
    """Представление для регистрации пользователя"""

    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("product_list")

    def form_valid(self, form):
        """Обработка успешной регистрации"""
        response = super().form_valid(form)

        # Автоматический вход после регистрации
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password1")
        user = authenticate(email=email, password=password)

        if user is not None:
            login(self.request, user)

            # Отправка приветственного письма
            send_welcome_email(user.email, user.username)

            messages.success(
                self.request,
                f"🎉 Добро пожаловать, {user.email}! Регистрация прошла успешно.",
            )

        return response

    def form_invalid(self, form):
        """Обработка ошибок регистрации"""
        messages.error(
            self.request, "❌ Ошибка регистрации. Проверьте введенные данные."
        )
        return super().form_invalid(form)


def login_view(request):
    """Представление для авторизации пользователя"""
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get(
                "username"
            )  # В форме это поле называется username
            password = form.cleaned_data.get("password")
            user = authenticate(email=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"👋 Добро пожаловать, {user.email}!")
                return redirect("product_list")
            else:
                messages.error(request, "❌ Неверный email или пароль.")
        else:
            messages.error(request, "❌ Ошибка в форме. Проверьте данные.")
    else:
        form = UserLoginForm()

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    """Представление для выхода из системы"""
    logout(request)
    messages.info(request, "👋 Вы успешно вышли из системы.")
    return redirect("product_list")


@login_required
def profile_view(request):
    """Профиль пользователя"""
    return render(request, "users/profile.html", {"user": request.user})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования профиля"""

    model = User
    form_class = UserProfileForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        """Возвращает текущего пользователя"""
        return self.request.user

    def form_valid(self, form):
        """Обработка успешного сохранения профиля"""
        messages.success(self.request, "✅ Профиль успешно обновлен!")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Обработка ошибок валидации"""
        messages.error(self.request, "❌ Ошибка обновления профиля. Проверьте данные.")
        return super().form_invalid(form)

from django.urls import path
from .views import SignUpApiView, LoginApiView

urlpatterns = [
    path("register/", SignUpApiView.as_view(), name="signup"),
    path("login/", LoginApiView.as_view(), name="login"),
]

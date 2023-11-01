"""URL mappings for the user API"""

from django.urls import path

from user import views


app_name = "user"

urlpatterns = [
    path("create/", views.CreateUserView.as_view(), name="create"),
    path("login/", views.CreateTokenView.as_view(), name="login"),
    path("update/", views.ManageUserView.as_view(), name="update"),
    path("users/", views.UserListView.as_view(), name="users"),
]

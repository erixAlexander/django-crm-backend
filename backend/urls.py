from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from api.views import (
    CreateOrgUserView,
    MyTokenObtainPairView,
    RegisterAdminWithOrgView,
    DeleteUserView,
    UpdateOrgUserView,
)  # Import the new custom token view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/user/register/", RegisterAdminWithOrgView.as_view(), name="register"),
    path("api/user/create_new/", CreateOrgUserView.as_view(), name="create_new"),
    path("api/user/delete/<str:pk>/", DeleteUserView.as_view(), name="delete_user"),
    path("api/user/update/<str:pk>/", UpdateOrgUserView.as_view(), name="update_user"),
    path(
        "api/token/", MyTokenObtainPairView.as_view(), name="get_token"
    ),  # Custom token view
    path("api/token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include("api.urls")),
]

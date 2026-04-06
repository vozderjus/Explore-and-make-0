from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('auth/', TokenRefreshView.as_view(), name="token_refresh"),
    path('auth/', TokenVerifyView.as_view(), name="token_verify"),
    path('api/schema', SpectacularAPIView.as_view(), name="schema"),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc')
]

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DiagnosticCentreViewSet,
    DiagnosticTestViewSet,
)


router = DefaultRouter()

router.register(
    "centres",
    DiagnosticCentreViewSet,
    basename="centre",
)

router.register(
    "tests",
    DiagnosticTestViewSet,
    basename="test",
)


urlpatterns = [
    path("", include(router.urls)),
]
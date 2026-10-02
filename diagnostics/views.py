from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import DiagnosticCentre, DiagnosticTest
from .permissions import IsStaffOrReadOnly
from .serializers import (
    DiagnosticCentreSerializer,
    DiagnosticTestSerializer,
)


class DiagnosticCentreViewSet(viewsets.ModelViewSet):
    queryset = DiagnosticCentre.objects.prefetch_related(
        "tests"
    ).all()
    serializer_class = DiagnosticCentreSerializer
    permission_classes = [IsStaffOrReadOnly]


class DiagnosticTestViewSet(viewsets.ModelViewSet):
    queryset = DiagnosticTest.objects.select_related(
        "centre"
    ).all()
    serializer_class = DiagnosticTestSerializer
    permission_classes = [IsStaffOrReadOnly]
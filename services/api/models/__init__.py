"""
models/__init__.py — Re-exporta todos los modelos del módulo models.

Facilita los imports: en lugar de importar de cada sub-módulo,
se puede importar directamente de models:
    from models import Supplier, SupplierCreate, ...
"""

from .supplier_models import (
    Category,
    Country,
    Currency,
    RateUpdate,
    StatusUpdate,
    Supplier,
    SupplierCreate,
    SupplierStatus,
)
from .incident import (
    IncidentCreate,
    IncidentUpdateStatus,
    IncidentResponse,
    SummaryResponse,
)
try:
    from .message_models import MessageResponse
    from .analysis_models import AnalysisResponse, AppInfo, HealthResponse, SatisfactionSummary, PercentageBreakdown
except ImportError:
    from models.message_models import MessageResponse
    from models.analysis_models import AnalysisResponse, AppInfo, HealthResponse, SatisfactionSummary, PercentageBreakdown

__all__ = [
    "Category",
    "Country",
    "Currency",
    "RateUpdate",
    "StatusUpdate",
    "Supplier",
    "SupplierCreate",
    "SupplierStatus",
    "IncidentCreate",
    "IncidentUpdateStatus",
    "IncidentResponse",
    "SummaryResponse",
    "MessageResponse",
    "AnalysisResponse",
    "AppInfo",
    "HealthResponse",
    "SatisfactionSummary",
    "PercentageBreakdown",
]
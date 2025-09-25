"""
FBS DMS API URLs

REST API endpoints for Document Management System.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .. import views

# Create router for DMS APIs
router = DefaultRouter()

# Document management endpoints
router.register(r'documents', views.DocumentViewSet, basename='document')
router.register(r'document-types', views.DocumentTypeViewSet, basename='documenttype')
router.register(r'categories', views.DocumentCategoryViewSet, basename='documentcategory')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # Additional document endpoints
    path('documents/<int:pk>/download/', views.DocumentDownloadView.as_view(), name='document-download'),
    path('documents/<int:pk>/approve/', views.DocumentApprovalView.as_view(), name='document-approve'),

    # Bulk operations
    path('documents/bulk-delete/', views.BulkDocumentDeleteView.as_view(), name='bulk-delete'),
    path('documents/bulk-approve/', views.BulkDocumentApprovalView.as_view(), name='bulk-approve'),
]

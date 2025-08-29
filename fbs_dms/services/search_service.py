"""
FBS DMS Search Service

Core business logic for document search and filtering.
"""

import logging
from typing import Dict, Any, List, Optional
from django.db import transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q, QuerySet
from django.conf import settings

from ..models import DMSDocument, DMSDocumentType, DMSDocumentCategory, DMSDocumentTag, DMSFileAttachment

logger = logging.getLogger('fbs_dms')


class SearchService:
    """Service for advanced document search"""
    
    def __init__(self, company_id: str):
        self.company_id = company_id
    
    def full_text_search(
        self, 
        query: str, 
        filters: Dict[str, Any] = None,
        limit: int = 50
    ) -> QuerySet[DMSDocument]:
        """Full-text search with optional filters"""
        try:
            queryset = DMSDocument.objects.filter(company_id=self.company_id)
            
            # Text search
            if query:
                queryset = queryset.filter(
                    Q(name__icontains=query) |
                    Q(title__icontains=query) |
                    Q(description__icontains=query)
                )
            
            # Apply filters
            if filters:
                queryset = self._apply_search_filters(queryset, filters)
            
            return queryset.order_by('-created_at')[:limit]
            
        except Exception as e:
            logger.error(f"Full-text search failed: {str(e)}")
            return DMSDocument.objects.none()
    
    def search_by_metadata(
        self, 
        metadata_filters: Dict[str, Any],
        limit: int = 50
    ) -> QuerySet[DMSDocument]:
        """Search documents by metadata"""
        try:
            queryset = DMSDocument.objects.filter(company_id=self.company_id)
            
            for key, value in metadata_filters.items():
                if key == 'tags':
                    # Handle tag search
                    if isinstance(value, list):
                        queryset = queryset.filter(tags__name__in=value)
                    else:
                        queryset = queryset.filter(tags__name=value)
                elif key == 'created_by':
                    # Handle user search
                    queryset = queryset.filter(created_by__username__icontains=value)
                elif key == 'date_range':
                    # Handle date range search
                    queryset = self._apply_date_range_filter(queryset, value)
                else:
                    # Handle other metadata fields
                    queryset = queryset.filter(metadata__contains={key: value})
            
            return queryset.order_by('-created_at')[:limit]
            
        except Exception as e:
            logger.error(f"Metadata search failed: {str(e)}")
            return DMSDocument.objects.none()
    
    def search_by_workflow_status(
        self, 
        status_filters: Dict[str, Any],
        limit: int = 50
    ) -> QuerySet[DMSDocument]:
        """Search documents by workflow status"""
        try:
            queryset = DMSDocument.objects.filter(company_id=self.company_id)
            
            if 'workflow_status' in status_filters:
                workflow_status = status_filters['workflow_status']
                if workflow_status == 'pending_approval':
                    queryset = queryset.filter(state='pending')
                elif workflow_status == 'approved':
                    queryset = queryset.filter(state='approved')
                elif workflow_status == 'rejected':
                    queryset = queryset.filter(state='rejected')
                elif workflow_status == 'draft':
                    queryset = queryset.filter(state='draft')
            
            if 'approver' in status_filters:
                approver_username = status_filters['approver']
                queryset = queryset.filter(
                    workflow__approval_steps__approver__username__icontains=approver_username
                )
            
            if 'approval_date_from' in status_filters:
                date_from = status_filters['approval_date_from']
                queryset = queryset.filter(
                    workflow__approval_steps__approved_at__gte=date_from
                )
            
            if 'approval_date_to' in status_filters:
                date_to = status_filters['approval_date_to']
                queryset = queryset.filter(
                    workflow__approval_steps__approved_at__lte=date_to
                )
            
            return queryset.order_by('-created_at')[:limit]
            
        except Exception as e:
            logger.error(f"Workflow status search failed: {str(e)}")
            return DMSDocument.objects.none()
    
    def advanced_search(
        self, 
        search_params: Dict[str, Any],
        limit: int = 50
    ) -> QuerySet[DMSDocument]:
        """Advanced search combining multiple search types"""
        try:
            queryset = DMSDocument.objects.filter(company_id=self.company_id)
            
            # Text search
            if 'query' in search_params:
                query = search_params['query']
                queryset = queryset.filter(
                    Q(name__icontains=query) |
                    Q(title__icontains=query) |
                    Q(description__icontains=query)
                )
            
            # Basic filters
            if 'filters' in search_params:
                queryset = self._apply_search_filters(queryset, search_params['filters'])
            
            # Metadata search
            if 'metadata' in search_params:
                queryset = self._apply_metadata_filters(queryset, search_params['metadata'])
            
            # Workflow search
            if 'workflow' in search_params:
                queryset = self._apply_workflow_filters(queryset, search_params['workflow'])
            
            # Date search
            if 'dates' in search_params:
                queryset = self._apply_date_filters(queryset, search_params['dates'])
            
            # Ordering
            ordering = search_params.get('ordering', '-created_at')
            queryset = queryset.order_by(ordering)
            
            return queryset[:limit]
            
        except Exception as e:
            logger.error(f"Advanced search failed: {str(e)}")
            return DMSDocument.objects.none()
    
    def get_search_suggestions(self, query: str, limit: int = 10) -> List[str]:
        """Get search suggestions based on query"""
        try:
            suggestions = []
            
            # Document name suggestions
            name_suggestions = DMSDocument.objects.filter(
                company_id=self.company_id,
                name__icontains=query
            ).values_list('name', flat=True)[:limit//2]
            suggestions.extend(name_suggestions)
            
            # Document title suggestions
            title_suggestions = DMSDocument.objects.filter(
                company_id=self.company_id,
                title__icontains=query
            ).values_list('title', flat=True)[:limit//2]
            suggestions.extend(title_suggestions)
            
            # Tag suggestions
            tag_suggestions = DMSDocumentTag.objects.filter(
                documents__company_id=self.company_id,
                name__icontains=query
            ).values_list('name', flat=True)[:limit//4]
            suggestions.extend(tag_suggestions)
            
            # Remove duplicates and limit
            unique_suggestions = list(set(suggestions))[:limit]
            
            return unique_suggestions
            
        except Exception as e:
            logger.error(f"Search suggestions failed: {str(e)}")
            return []
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Get search statistics for the company"""
        try:
            total_documents = DMSDocument.objects.filter(company_id=self.company_id).count()
            
            # Document type distribution
            type_distribution = DMSDocument.objects.filter(
                company_id=self.company_id
            ).values('document_type__name').annotate(
                count=models.Count('id')
            )
            
            # State distribution
            state_distribution = DMSDocument.objects.filter(
                company_id=self.company_id
            ).values('state').annotate(
                count=models.Count('id')
            )
            
            # Recent activity
            recent_documents = DMSDocument.objects.filter(
                company_id=self.company_id,
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count()
            
            return {
                'total_documents': total_documents,
                'type_distribution': list(type_distribution),
                'state_distribution': list(state_distribution),
                'recent_documents': recent_documents,
                'last_updated': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Search statistics failed: {str(e)}")
            return {}
    
    def _apply_search_filters(self, queryset: QuerySet, filters: Dict[str, Any]) -> QuerySet:
        """Apply basic search filters"""
        if 'document_type' in filters:
            queryset = queryset.filter(document_type_id=filters['document_type'])
        
        if 'category' in filters:
            queryset = queryset.filter(category_id=filters['category'])
        
        if 'state' in filters:
            queryset = queryset.filter(state=filters['state'])
        
        if 'confidentiality_level' in filters:
            queryset = queryset.filter(confidentiality_level=filters['confidentiality_level'])
        
        if 'created_by' in filters:
            queryset = queryset.filter(created_by__username__icontains=filters['created_by'])
        
        return queryset
    
    def _apply_metadata_filters(self, queryset: QuerySet, metadata: Dict[str, Any]) -> QuerySet:
        """Apply metadata filters"""
        for key, value in metadata.items():
            if key == 'tags':
                if isinstance(value, list):
                    queryset = queryset.filter(tags__name__in=value)
                else:
                    queryset = queryset.filter(tags__name=value)
            else:
                queryset = queryset.filter(metadata__contains={key: value})
        
        return queryset
    
    def _apply_workflow_filters(self, queryset: QuerySet, workflow: Dict[str, Any]) -> QuerySet:
        """Apply workflow filters"""
        if 'status' in workflow:
            queryset = queryset.filter(state=workflow['status'])
        
        if 'approver' in workflow:
            queryset = queryset.filter(
                workflow__approval_steps__approver__username__icontains=workflow['approver']
            )
        
        return queryset
    
    def _apply_date_filters(self, queryset: QuerySet, dates: Dict[str, Any]) -> QuerySet:
        """Apply date filters"""
        if 'created_from' in dates:
            queryset = queryset.filter(created_at__gte=dates['created_from'])
        
        if 'created_to' in dates:
            queryset = queryset.filter(created_at__lte=dates['created_to'])
        
        if 'expiry_from' in dates:
            queryset = queryset.filter(expiry_date__gte=dates['expiry_from'])
        
        if 'expiry_to' in dates:
            queryset = queryset.filter(expiry_date__lte=dates['expiry_to'])
        
        return queryset
    
    def _apply_date_range_filter(self, queryset: QuerySet, date_range: Dict[str, Any]) -> QuerySet:
        """Apply date range filter"""
        if 'from' in date_range and 'to' in date_range:
            queryset = queryset.filter(
                created_at__range=[date_range['from'], date_range['to']]
            )
        
        return queryset

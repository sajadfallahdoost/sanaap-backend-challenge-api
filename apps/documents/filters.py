"""
Django filters for document queryset filtering.

This module provides filter classes for advanced document filtering
using django-filter.
"""
import django_filters
from apps.documents.models import Document


class DocumentFilter(django_filters.FilterSet):
    """
    Filter class for Document model.
    
    Provides various filtering options for document queries.
    """
    
    title = django_filters.CharFilter(lookup_expr='icontains')
    file_extension = django_filters.CharFilter(lookup_expr='iexact')
    file_type = django_filters.CharFilter(lookup_expr='icontains')
    uploaded_by = django_filters.NumberFilter(field_name='uploaded_by__id')
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte'
    )
    processing_status = django_filters.ChoiceFilter(
        choices=Document.ProcessingStatus.choices
    )
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Document
        fields = [
            'title', 'file_extension', 'file_type', 'uploaded_by',
            'processing_status'
        ]
    
    def filter_search(self, queryset, name, value):
        """
        Custom search filter for title and description.
        
        Args:
            queryset: Document queryset
            name: Filter name
            value: Search value
            
        Returns:
            Filtered queryset
        """
        from django.db.models import Q
        return queryset.filter(
            Q(title__icontains=value) | Q(description__icontains=value)
        )


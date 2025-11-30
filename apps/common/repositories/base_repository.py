"""
Base repository pattern implementation for data access layer.

This module implements the Repository pattern to provide a clean abstraction
over data access operations, following SOLID principles.
"""
from typing import Generic, TypeVar, Optional, List, Dict, Any
from django.db import models, transaction
from django.db.models import QuerySet
from django.core.exceptions import ObjectDoesNotExist
from apps.common.exceptions import NotFoundError

# Type variable for model class
ModelType = TypeVar('ModelType', bound=models.Model)


class BaseRepository(Generic[ModelType]):
    """
    Base repository providing common CRUD operations for Django models.
    
    This class follows the Repository pattern to separate data access logic
    from business logic, adhering to the Single Responsibility Principle.
    
    Type Parameters:
        ModelType: The Django model class this repository manages
        
    Attributes:
        model: The Django model class
    """
    
    def __init__(self, model: type[ModelType]):
        """
        Initialize the repository with a model class.
        
        Args:
            model: Django model class to manage
        """
        self.model = model
    
    def get_by_id(self, id: Any) -> Optional[ModelType]:
        """
        Retrieve a model instance by its ID.
        
        Args:
            id: The primary key value
            
        Returns:
            Model instance if found, None otherwise
        """
        try:
            return self.model.objects.get(pk=id)
        except ObjectDoesNotExist:
            return None
    
    def get_or_raise(self, id: Any) -> ModelType:
        """
        Retrieve a model instance by ID or raise NotFoundError.
        
        Args:
            id: The primary key value
            
        Returns:
            Model instance
            
        Raises:
            NotFoundError: If the instance does not exist
        """
        instance = self.get_by_id(id)
        if instance is None:
            raise NotFoundError(f"{self.model.__name__} with id {id} not found")
        return instance
    
    def filter(self, **kwargs) -> QuerySet[ModelType]:
        """
        Filter model instances by given criteria.
        
        Args:
            **kwargs: Filter parameters
            
        Returns:
            QuerySet of matching instances
        """
        return self.model.objects.filter(**kwargs)
    
    def all(self) -> QuerySet[ModelType]:
        """
        Get all model instances.
        
        Returns:
            QuerySet of all instances
        """
        return self.model.objects.all()
    
    def create(self, **kwargs) -> ModelType:
        """
        Create a new model instance.
        
        Args:
            **kwargs: Field values for the new instance
            
        Returns:
            Created model instance
        """
        return self.model.objects.create(**kwargs)
    
    @transaction.atomic
    def bulk_create(self, instances: List[ModelType]) -> List[ModelType]:
        """
        Create multiple model instances in a single transaction.
        
        Args:
            instances: List of model instances to create
            
        Returns:
            List of created instances
        """
        return self.model.objects.bulk_create(instances)
    
    def update(self, instance: ModelType, **kwargs) -> ModelType:
        """
        Update a model instance with given field values.
        
        Args:
            instance: The model instance to update
            **kwargs: Field values to update
            
        Returns:
            Updated model instance
        """
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    
    def delete(self, instance: ModelType) -> None:
        """
        Delete a model instance.
        
        Args:
            instance: The model instance to delete
        """
        instance.delete()
    
    def delete_by_id(self, id: Any) -> bool:
        """
        Delete a model instance by its ID.
        
        Args:
            id: The primary key value
            
        Returns:
            True if deleted, False if not found
        """
        instance = self.get_by_id(id)
        if instance:
            self.delete(instance)
            return True
        return False
    
    def exists(self, **kwargs) -> bool:
        """
        Check if an instance exists matching the given criteria.
        
        Args:
            **kwargs: Filter parameters
            
        Returns:
            True if exists, False otherwise
        """
        return self.model.objects.filter(**kwargs).exists()
    
    def count(self, **kwargs) -> int:
        """
        Count instances matching the given criteria.
        
        Args:
            **kwargs: Filter parameters
            
        Returns:
            Count of matching instances
        """
        return self.model.objects.filter(**kwargs).count()
    
    def get_or_create(self, defaults: Optional[Dict] = None, **kwargs) -> tuple[ModelType, bool]:
        """
        Get an existing instance or create a new one.
        
        Args:
            defaults: Field values for creation if instance doesn't exist
            **kwargs: Lookup parameters
            
        Returns:
            Tuple of (instance, created) where created is a boolean
        """
        return self.model.objects.get_or_create(defaults=defaults or {}, **kwargs)
    
    def select_related(self, *fields) -> QuerySet[ModelType]:
        """
        Perform a SQL join to fetch related objects in a single query.
        
        Useful for foreign key relationships to reduce database queries.
        
        Args:
            *fields: Related field names to select
            
        Returns:
            QuerySet with related objects pre-fetched
        """
        return self.model.objects.select_related(*fields)
    
    def prefetch_related(self, *fields) -> QuerySet[ModelType]:
        """
        Prefetch related objects for many-to-many and reverse foreign key relationships.
        
        Args:
            *fields: Related field names to prefetch
            
        Returns:
            QuerySet with related objects pre-fetched
        """
        return self.model.objects.prefetch_related(*fields)


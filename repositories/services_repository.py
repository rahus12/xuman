from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, insert, select, update, delete
from sqlalchemy.exc import IntegrityError
import json

from models import Service


class ServicesRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_services(self) -> List[Service]:
        query = select(text("*")).select_from(text("services"))
        result = self.db.execute(query)
        return [self._row_to_model(row) for row in result]

    def get_service(self, service_id: str) -> Optional[Service]:
        query = select(text("*")).select_from(text("services")).where(text("id = :service_id"))
        result = self.db.execute(query, {"service_id": service_id}).fetchone()
        return self._row_to_model(result) if result else None

    def create_service(self, service: Service) -> Service:
        try:
            query = text("""
                INSERT INTO services (id, provider_id, title, description, category, price, currency, duration, availability, images, is_active, created_at)
                VALUES (:id, :provider_id, :title, :description, :category, :price, :currency, :duration, :availability, :images, :is_active, :created_at)
            """)
            
            self.db.execute(query, {
                "id": service.id,
                "provider_id": service.providerId,
                "title": service.title,
                "description": service.description,
                "category": service.category,
                "price": service.price,
                "currency": service.currency,
                "duration": service.duration,
                "availability": service.availability.model_dump_json(),
                "images": json.dumps(service.images),
                "is_active": service.isActive,
                "created_at": service.createdAt
            })
            self.db.commit()
            return service
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Service creation failed: {str(e)}") from e

    def update_service(self, service_id: str, updated: Service) -> Optional[Service]:
        try:
            query = text("""
                UPDATE services 
                SET provider_id = :provider_id, title = :title, description = :description, 
                    category = :category, price = :price, currency = :currency, 
                    duration = :duration, availability = :availability, 
                    images = :images, is_active = :is_active
                WHERE id = :service_id
            """)
            
            result = self.db.execute(query, {
                "service_id": service_id,
                "provider_id": updated.providerId,
                "title": updated.title,
                "description": updated.description,
                "category": updated.category,
                "price": updated.price,
                "currency": updated.currency,
                "duration": updated.duration,
                "availability": updated.availability.model_dump_json(),
                "images": json.dumps(updated.images),
                "is_active": updated.isActive
            })
            self.db.commit()
            return updated if result.rowcount > 0 else None
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Service update failed: {str(e)}") from e

    def delete_service(self, service_id: str) -> bool:
        query = text("DELETE FROM services WHERE id = :service_id")
        result = self.db.execute(query, {"service_id": service_id})
        self.db.commit()
        return result.rowcount > 0

    def _row_to_model(self, row) -> Service:
        from models import ServiceAvailability
        return Service(
            id=str(row.id),
            providerId=str(row.provider_id),
            title=row.title,
            description=row.description,
            category=row.category,
            price=float(row.price),
            currency=row.currency,
            duration=row.duration,
            availability=ServiceAvailability(**json.loads(row.availability)),
            images=json.loads(row.images),
            isActive=row.is_active,
            createdAt=row.created_at,
        )
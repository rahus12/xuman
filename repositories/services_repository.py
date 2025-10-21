from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, insert, select, update, delete
from sqlalchemy.exc import IntegrityError
import json

from models import Service, ServiceAvailability


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
                INSERT INTO services (id, provider_id, name, description, price, duration_minutes, availability, status, created_at, updated_at)
                VALUES (:id, :provider_id, :name, :description, :price, :duration_minutes, :availability, :status, :created_at, :updated_at)
            """)
            
            self.db.execute(query, {
                "id": service.id,
                "provider_id": service.providerId,
                "name": service.name,
                "description": service.description,
                "price": service.price,
                "duration_minutes": service.durationMinutes,
                "availability": service.availability.model_dump_json(),
                "status": service.status,
                "created_at": service.createdAt,
                "updated_at": service.updatedAt
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
                SET provider_id = :provider_id, name = :name, description = :description, 
                    price = :price, duration_minutes = :duration_minutes, 
                    availability = :availability, status = :status, updated_at = :updated_at
                    
                WHERE id = :service_id
            """)
            
            result = self.db.execute(query, {
                "service_id": service_id,
                "provider_id": updated.providerId,
                "name": updated.name,
                "description": updated.description,
                "price": updated.price,
                "duration_minutes": updated.durationMinutes,
                "availability": updated.availability.model_dump_json(),
                "status": updated.status,
                "updated_at": updated.updatedAt
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
        # Parse availability JSON
        availability_data = row.availability if hasattr(row, 'availability') and row.availability else {}
        availability = ServiceAvailability(**availability_data)
        
        return Service(
            id=str(row.id),
            providerId=str(row.provider_id),
            name=row.name,
            description=row.description,
            price=float(row.price),
            durationMinutes=row.duration_minutes,
            availability=availability,
            status=row.status,
            createdAt=row.created_at,
            updatedAt=row.updated_at
        )
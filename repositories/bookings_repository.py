from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text, insert, select, update, delete
from sqlalchemy.exc import IntegrityError

from models import Booking


class BookingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_bookings(self, customer_id: Optional[str] = None, provider_id: Optional[str] = None) -> List[Booking]:
        query = select(text("*")).select_from(text("bookings"))
        params = {}
        
        if customer_id:
            query = query.where(text("customer_id = :customer_id"))
            params["customer_id"] = customer_id
        if provider_id:
            query = query.where(text("provider_id = :provider_id"))
            params["provider_id"] = provider_id
        
        result = self.db.execute(query, params)
        return [self._row_to_model(row) for row in result]

    def get_booking(self, booking_id: str) -> Optional[Booking]:
        query = select(text("*")).select_from(text("bookings")).where(text("id = :booking_id"))
        result = self.db.execute(query, {"booking_id": booking_id}).fetchone()
        return self._row_to_model(result) if result else None

    def create_booking(self, booking: Booking) -> Booking:
        try:
            query = text("""
                INSERT INTO bookings (id, customer_id, service_id, provider_id, status,
                                    scheduled_at, duration_minutes, total_amount, notes,
                                    created_at, updated_at)
                VALUES (:id, :customer_id, :service_id, :provider_id, :status,
                        :scheduled_at, :duration_minutes, :total_amount, :notes,
                        :created_at, :updated_at)
                RETURNING *
            """)
            
            result = self.db.execute(query, {
                "id": booking.id,
                "customer_id": booking.customerId,
                "service_id": booking.serviceId,
                "provider_id": booking.providerId,
                "status": booking.status.value,
                "scheduled_at": booking.scheduledAt,
                "duration_minutes": booking.duration,
                "total_amount": booking.totalAmount,
                "notes": booking.notes,
                "created_at": booking.createdAt,
                "updated_at": booking.updatedAt
            }).fetchone()
            self.db.commit()
            return self._row_to_model(result)
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Booking creation failed: {str(e)}") from e

    def update_booking(self, booking_id: str, updated: Booking) -> Optional[Booking]:
        try:
            query = text("""
                UPDATE bookings 
                SET customer_id = :customer_id,
                    service_id = :service_id,
                    provider_id = :provider_id,
                    status = :status,
                    scheduled_at = :scheduled_at,
                    duration_minutes = :duration_minutes,
                    total_amount = :total_amount,
                    notes = :notes,
                    updated_at = :updated_at
                WHERE id = :booking_id
                RETURNING *
            """)
            
            result = self.db.execute(query, {
                "booking_id": booking_id,
                "customer_id": updated.customerId,
                "service_id": updated.serviceId,
                "provider_id": updated.providerId,
                "status": updated.status.value,
                "scheduled_at": updated.scheduledAt,
                "duration_minutes": updated.duration,
                "total_amount": updated.totalAmount,
                "notes": updated.notes,
                "updated_at": datetime.now(timezone.utc)
            }).fetchone()
            
            if not result:
                return None
            self.db.commit()
            return self._row_to_model(result)
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Booking update failed: {str(e)}") from e

    def delete_booking(self, booking_id: str) -> bool:
        query = text("DELETE FROM bookings WHERE id = :booking_id RETURNING id")
        result = self.db.execute(query, {"booking_id": booking_id}).fetchone()
        if result:
            self.db.commit()
            return True
        return False

    def _row_to_model(self, row) -> Booking:
        from models import BookingStatus
        return Booking(
            id=str(row.id),
            customerId=str(row.customer_id),
            serviceId=str(row.service_id),
            providerId=str(row.provider_id),
            status=BookingStatus(row.status),
            scheduledAt=row.scheduled_at,
            duration=row.duration_minutes,
            totalAmount=float(row.total_amount),
            notes=row.notes,
            createdAt=row.created_at,
            updatedAt=row.updated_at
        )
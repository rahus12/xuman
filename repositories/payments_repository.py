from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, insert, select, update, delete
from sqlalchemy.exc import IntegrityError
import json

from models import PaymentResponse, RefundResponse


class PaymentsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_payment(self, payment: PaymentResponse) -> PaymentResponse:
        """Create a new payment record"""
        try:
            query = text("""
                INSERT INTO payments (id, booking_id, status, transaction_id, amount, currency, 
                                    payment_method, failure_reason, created_at, updated_at)
                VALUES (:id, :booking_id, :status, :transaction_id, :amount, :currency, 
                        :payment_method, :failure_reason, :created_at, :updated_at)
            """)

            self.db.execute(query, {
                "id": payment.id,
                "booking_id": payment.bookingId,
                "status": payment.status,
                "transaction_id": payment.transactionId,
                "amount": payment.amount,
                "currency": payment.currency,
                "payment_method": payment.paymentMethod.model_dump_json(),
                "failure_reason": payment.failureReason,
                "created_at": payment.createdAt,
                "updated_at": payment.updatedAt
            })
            self.db.commit()
            return payment
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Payment creation failed: {str(e)}") from e

    def get_payment(self, payment_id: str) -> Optional[PaymentResponse]:
        """Get payment by ID"""
        query = select(text("*")).select_from(text("payments")).where(text("id = :payment_id"))
        result = self.db.execute(query, {"payment_id": payment_id}).fetchone()
        return self._row_to_model(result) if result else None

    def get_payment_by_booking(self, booking_id: str) -> Optional[PaymentResponse]:
        """Get payment by booking ID"""
        query = select(text("*")).select_from(text("payments")).where(text("booking_id = :booking_id"))
        result = self.db.execute(query, {"booking_id": booking_id}).fetchone()
        return self._row_to_model(result) if result else None

    def update_payment_status(self, payment_id: str, status: str, failure_reason: Optional[str] = None) -> bool:
        """Update payment status"""
        try:
            query = text("""
                UPDATE payments 
                SET status = :status, failure_reason = :failure_reason, updated_at = :updated_at
                WHERE id = :payment_id
            """)

            from datetime import datetime, timezone
            result = self.db.execute(query, {
                "payment_id": payment_id,
                "status": status,
                "failure_reason": failure_reason,
                "updated_at": datetime.now(timezone.utc)
            })
            self.db.commit()
            return result.rowcount > 0
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Payment update failed: {str(e)}") from e

    def create_refund(self, refund: RefundResponse) -> RefundResponse:
        """Create a refund record"""
        try:
            query = text("""
                INSERT INTO refunds (id, payment_id, status, amount, reason, created_at)
                VALUES (:id, :payment_id, :status, :amount, :reason, :created_at)
            """)

            self.db.execute(query, {
                "id": refund.id,
                "payment_id": refund.paymentId,
                "status": refund.status,
                "amount": refund.amount,
                "reason": refund.reason,
                "created_at": refund.createdAt
            })
            self.db.commit()
            return refund
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Refund creation failed: {str(e)}") from e

    def get_refunds_by_payment(self, payment_id: str) -> List[RefundResponse]:
        """Get all refunds for a payment"""
        query = select(text("*")).select_from(text("refunds")).where(text("payment_id = :payment_id"))
        result = self.db.execute(query, {"payment_id": payment_id})
        return [self._row_to_refund_model(row) for row in result]

    def _row_to_model(self, row) -> PaymentResponse:
        from models import PaymentMethod
        # Handle both string and dict payment_method
        if isinstance(row.payment_method, str):
            payment_method_data = json.loads(row.payment_method)
        else:
            payment_method_data = row.payment_method
            
        return PaymentResponse(
            id=str(row.id),
            bookingId=str(row.booking_id),
            status=row.status,
            transactionId=row.transaction_id,
            amount=float(row.amount),
            currency=row.currency,
            paymentMethod=PaymentMethod(**payment_method_data),
            failureReason=row.failure_reason,
            createdAt=row.created_at,
            updatedAt=row.updated_at
        )

    def _row_to_refund_model(self, row) -> RefundResponse:
        return RefundResponse(
            id=str(row.id),
            paymentId=str(row.payment_id),
            status=row.status,
            amount=float(row.amount),
            reason=row.reason,
            createdAt=row.created_at
        )

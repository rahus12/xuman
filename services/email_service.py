from typing import Optional
from datetime import datetime, timezone
import os
import json
from pathlib import Path

from models import User, Service, Booking, BookingStatus


class EmailService:
    def __init__(self, output_dir: str = None):
        # Use environment variable for email notifications directory
        if output_dir is None:
            output_dir = os.getenv("EMAIL_NOTIFICATIONS_DIR", "email_notifications")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def send_booking_confirmation(self, customer: User, provider: User, service: Service, booking: Booking) -> str:
        """Send booking confirmation email to customer"""
        subject = f"Booking Confirmed - {service.title}"
        
        content = f"""
        <html>
        <body>
            <h2>Booking Confirmation</h2>
            <p>Hello {customer.profile.firstName} {customer.profile.lastName},</p>
            
            <p>Your booking has been confirmed! Here are the details:</p>
            
            <h3>Service Details</h3>
            <ul>
                <li><strong>Service:</strong> {service.title}</li>
                <li><strong>Provider:</strong> {provider.profile.firstName} {provider.profile.lastName}</li>
                <li><strong>Description:</strong> {service.description}</li>
                <li><strong>Price:</strong> ${service.price} {service.currency}</li>
                <li><strong>Duration:</strong> {service.duration} minutes</li>
            </ul>
            
            <h3>Booking Details</h3>
            <ul>
                <li><strong>Booking ID:</strong> {booking.id}</li>
                <li><strong>Scheduled Date:</strong> {booking.scheduledAt.strftime('%Y-%m-%d %H:%M')}</li>
                <li><strong>Total Amount:</strong> ${booking.totalAmount}</li>
                <li><strong>Status:</strong> {booking.status.value.title()}</li>
                {f'<li><strong>Notes:</strong> {booking.notes}</li>' if booking.notes else ''}
            </ul>
            
            <p>Thank you for using our service marketplace!</p>
            
            <hr>
            <p><small>This is a mock email notification. In production, this would be sent via SMTP.</small></p>
        </body>
        </html>
        """
        
        return self._save_email(
            recipient=customer,
            subject=subject,
            content=content,
            email_type="booking_confirmation"
        )

    def send_booking_notification_to_provider(self, customer: User, provider: User, service: Service, booking: Booking) -> str:
        """Send new booking notification to service provider"""
        subject = f"New Booking Received - {service.title}"
        
        content = f"""
        <html>
        <body>
            <h2>New Booking Received</h2>
            <p>Hello {provider.profile.firstName} {provider.profile.lastName},</p>
            
            <p>You have received a new booking for your service!</p>
            
            <h3>Customer Details</h3>
            <ul>
                <li><strong>Name:</strong> {customer.profile.firstName} {customer.profile.lastName}</li>
                <li><strong>Email:</strong> {customer.email}</li>
                <li><strong>Phone:</strong> {customer.profile.phone}</li>
            </ul>
            
            <h3>Service Details</h3>
            <ul>
                <li><strong>Service:</strong> {service.title}</li>
                <li><strong>Description:</strong> {service.description}</li>
                <li><strong>Price:</strong> ${service.price} {service.currency}</li>
                <li><strong>Duration:</strong> {service.duration} minutes</li>
            </ul>
            
            <h3>Booking Details</h3>
            <ul>
                <li><strong>Booking ID:</strong> {booking.id}</li>
                <li><strong>Scheduled Date:</strong> {booking.scheduledAt.strftime('%Y-%m-%d %H:%M')}</li>
                <li><strong>Total Amount:</strong> ${booking.totalAmount}</li>
                <li><strong>Status:</strong> {booking.status.value.title()}</li>
                {f'<li><strong>Customer Notes:</strong> {booking.notes}</li>' if booking.notes else ''}
            </ul>
            
            <p>Please confirm or update the booking status as needed.</p>
            
            <hr>
            <p><small>This is a mock email notification. In production, this would be sent via SMTP.</small></p>
        </body>
        </html>
        """
        
        return self._save_email(
            recipient=provider,
            subject=subject,
            content=content,
            email_type="booking_notification_provider"
        )

    def send_booking_update(self, customer: User, provider: User, service: Service, booking: Booking, old_status: BookingStatus) -> str:
        """Send booking update notification"""
        subject = f"Booking Updated - {service.title}"
        
        content = f"""
        <html>
        <body>
            <h2>Booking Status Updated</h2>
            <p>Hello {customer.profile.firstName} {customer.profile.lastName},</p>
            
            <p>Your booking status has been updated:</p>
            
            <h3>Status Change</h3>
            <ul>
                <li><strong>Previous Status:</strong> {old_status.value.title()}</li>
                <li><strong>New Status:</strong> {booking.status.value.title()}</li>
            </ul>
            
            <h3>Service Details</h3>
            <ul>
                <li><strong>Service:</strong> {service.title}</li>
                <li><strong>Provider:</strong> {provider.profile.firstName} {provider.profile.lastName}</li>
                <li><strong>Scheduled Date:</strong> {booking.scheduledAt.strftime('%Y-%m-%d %H:%M')}</li>
                <li><strong>Total Amount:</strong> ${booking.totalAmount}</li>
                {f'<li><strong>Notes:</strong> {booking.notes}</li>' if booking.notes else ''}
            </ul>
            
            <p>If you have any questions, please contact the service provider.</p>
            
            <hr>
            <p><small>This is a mock email notification. In production, this would be sent via SMTP.</small></p>
        </body>
        </html>
        """
        
        return self._save_email(
            recipient=customer,
            subject=subject,
            content=content,
            email_type="booking_update"
        )

    def send_booking_cancellation(self, customer: User, provider: User, service: Service, booking: Booking) -> str:
        """Send booking cancellation notification"""
        subject = f"Booking Cancelled - {service.title}"
        
        content = f"""
        <html>
        <body>
            <h2>Booking Cancelled</h2>
            <p>Hello {customer.profile.firstName} {customer.profile.lastName},</p>
            
            <p>Your booking has been cancelled.</p>
            
            <h3>Booking Details</h3>
            <ul>
                <li><strong>Service:</strong> {service.title}</li>
                <li><strong>Provider:</strong> {provider.profile.firstName} {provider.profile.lastName}</li>
                <li><strong>Booking ID:</strong> {booking.id}</li>
                <li><strong>Scheduled Date:</strong> {booking.scheduledAt.strftime('%Y-%m-%d %H:%M')}</li>
                <li><strong>Total Amount:</strong> ${booking.totalAmount}</li>
            </ul>
            
            <p>If you have any questions or would like to reschedule, please contact the service provider.</p>
            
            <hr>
            <p><small>This is a mock email notification. In production, this would be sent via SMTP.</small></p>
        </body>
        </html>
        """
        
        return self._save_email(
            recipient=customer,
            subject=subject,
            content=content,
            email_type="booking_cancellation"
        )

    def _save_email(self, recipient: User, subject: str, content: str, email_type: str) -> str:
        """Save email to file (mock implementation)"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{recipient.profile.firstName}_{recipient.profile.lastName}_{email_type}_{timestamp}.html"
        filepath = self.output_dir / filename
        
        email_data = {
            "to": recipient.email,
            "to_name": f"{recipient.profile.firstName} {recipient.profile.lastName}",
            "subject": subject,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": email_type
        }
        
        # Save as HTML file for easy viewing
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Also save metadata as JSON
        json_filepath = filepath.with_suffix('.json')
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(email_data, f, indent=2, default=str)
        
        return str(filepath)

    def get_email_history(self, user_email: Optional[str] = None) -> list:
        """Get email history (for testing/debugging)"""
        emails = []
        for json_file in self.output_dir.glob("*.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                email_data = json.load(f)
                if not user_email or email_data['to'] == user_email:
                    emails.append(email_data)
        return sorted(emails, key=lambda x: x['timestamp'], reverse=True)

    def send_password_reset_email(self, user: User, reset_token: str) -> str:
        """Send password reset email with reset link"""
        subject = "Password Reset Request - Service Marketplace"
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"  # Frontend URL placeholder
        
        content = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hello {user.profile.firstName} {user.profile.lastName},</p>
            
            <p>You have requested to reset your password for your Service Marketplace account.</p>
            
            <p>To reset your password, please click on the following link:</p>
            <p><a href="{reset_link}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
            
            <p>Or copy and paste this link into your browser:</p>
            <p><code>{reset_link}</code></p>
            
            <p><strong>Important:</strong></p>
            <ul>
                <li>This link will expire in 24 hours for security reasons</li>
                <li>If you did not request this password reset, please ignore this email</li>
                <li>Do not share this link with anyone</li>
            </ul>
            
            <p>Best regards,<br>The Service Marketplace Team</p>
            
            <hr>
            <p><small>This is a mock email notification. In production, this would be sent via SMTP.</small></p>
        </body>
        </html>
        """
        
        return self._save_email(user, subject, content, "password_reset")

    def send_password_reset_confirmation(self, user: User) -> str:
        """Send confirmation email after successful password reset"""
        subject = "Password Successfully Reset - Service Marketplace"
        
        content = f"""
        <html>
        <body>
            <h2>Password Successfully Reset</h2>
            <p>Hello {user.profile.firstName} {user.profile.lastName},</p>
            
            <p>Your password has been successfully reset for your Service Marketplace account.</p>
            
            <p>If you did not make this change, please contact our support team immediately.</p>
            
            <p>Best regards,<br>The Service Marketplace Team</p>
            
            <hr>
            <p><small>This is a mock email notification. In production, this would be sent via SMTP.</small></p>
        </body>
        </html>
        """
        
        return self._save_email(user, subject, content, "password_reset_confirmation")

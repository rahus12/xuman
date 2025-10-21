"""
Unit tests for email notification functionality
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta

from models import User, UserRole, UserProfile, Service, ServiceAvailability, Booking, BookingStatus
from services.email_service import EmailService


class TestEmailService:
    """Test cases for EmailService"""
    
    @pytest.fixture
    def temp_email_dir(self):
        """Create a temporary directory for email files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def email_service(self, temp_email_dir):
        """Create EmailService instance with temporary directory"""
        return EmailService(output_dir=temp_email_dir)
    
    def test_send_booking_confirmation(self, email_service, sample_customer, sample_provider, sample_service, sample_booking):
        """Test sending booking confirmation email"""
        result = email_service.send_booking_confirmation(sample_customer, sample_provider, sample_service, sample_booking)
        
        assert isinstance(result, str)
        assert os.path.exists(result)
        
        # Check email content
        with open(result, 'r') as f:
            content = f.read()
            assert sample_customer.profile.firstName in content
            assert sample_service.title in content
            assert sample_provider.profile.firstName in content
            assert "Booking Confirmation" in content
    
    def test_send_booking_notification_to_provider(self, email_service, sample_customer, sample_provider, sample_service, sample_booking):
        """Test sending booking notification to provider"""
        result = email_service.send_booking_notification_to_provider(sample_customer, sample_provider, sample_service, sample_booking)
        
        assert isinstance(result, str)
        assert os.path.exists(result)
        
        # Check email content
        with open(result, 'r') as f:
            content = f.read()
            assert sample_provider.profile.firstName in content
            assert sample_customer.profile.firstName in content
            assert sample_service.title in content
            assert "New Booking Received" in content
    
    def test_send_booking_update(self, email_service, sample_customer, sample_provider, sample_service, sample_booking):
        """Test sending booking update email"""
        old_status = BookingStatus.PENDING
        sample_booking.status = BookingStatus.CONFIRMED
        
        result = email_service.send_booking_update(sample_customer, sample_provider, sample_service, sample_booking, old_status)
        
        assert isinstance(result, str)
        assert os.path.exists(result)
        
        # Check email content
        with open(result, 'r') as f:
            content = f.read()
            assert sample_customer.profile.firstName in content
            assert "Booking Update" in content
            assert "Status Changed" in content
    
    def test_send_booking_cancellation(self, email_service, sample_customer, sample_provider, sample_service, sample_booking):
        """Test sending booking cancellation email"""
        sample_booking.status = BookingStatus.CANCELLED
        
        result = email_service.send_booking_cancellation(sample_customer, sample_provider, sample_service, sample_booking)
        
        assert isinstance(result, str)
        assert os.path.exists(result)
        
        # Check email content
        with open(result, 'r') as f:
            content = f.read()
            assert sample_customer.profile.firstName in content
            assert "Booking Cancelled" in content
    
    def test_send_password_reset_email(self, email_service, sample_customer):
        """Test sending password reset email"""
        reset_token = "test_reset_token_123"
        
        result = email_service.send_password_reset_email(sample_customer, reset_token)
        
        assert isinstance(result, str)
        assert os.path.exists(result)
        
        # Check email content
        with open(result, 'r') as f:
            content = f.read()
            assert sample_customer.profile.firstName in content
            assert "Password Reset Request" in content
            assert reset_token in content
            assert "localhost:3000/reset-password" in content
    
    def test_send_password_reset_confirmation(self, email_service, sample_customer):
        """Test sending password reset confirmation email"""
        result = email_service.send_password_reset_confirmation(sample_customer)
        
        assert isinstance(result, str)
        assert os.path.exists(result)
        
        # Check email content
        with open(result, 'r') as f:
            content = f.read()
            assert sample_customer.profile.firstName in content
            assert "Password Successfully Reset" in content
    
    def test_email_file_creation(self, email_service, sample_customer):
        """Test that email files are created with proper naming"""
        reset_token = "test_token"
        
        result = email_service.send_password_reset_email(sample_customer, reset_token)
        
        # Check file naming pattern
        filename = os.path.basename(result)
        assert filename.startswith("customer_")  # Based on email prefix
        assert filename.endswith(".html")
        
        # Check JSON metadata file
        json_file = result.replace('.html', '.json')
        assert os.path.exists(json_file)
        
        # Check JSON content
        import json
        with open(json_file, 'r') as f:
            metadata = json.load(f)
            assert metadata['to'] == sample_customer.email
            assert metadata['type'] == 'password_reset'
            assert 'timestamp' in metadata
    
    def test_get_email_history(self, email_service, sample_customer, sample_provider):
        """Test retrieving email history"""
        # Send some emails
        email_service.send_password_reset_email(sample_customer, "token1")
        email_service.send_password_reset_email(sample_provider, "token2")
        
        # Get all emails
        all_emails = email_service.get_email_history()
        assert len(all_emails) == 2
        
        # Get emails for specific user
        customer_emails = email_service.get_email_history(sample_customer.email)
        assert len(customer_emails) == 1
        assert customer_emails[0]['to'] == sample_customer.email
        
        provider_emails = email_service.get_email_history(sample_provider.email)
        assert len(provider_emails) == 1
        assert provider_emails[0]['to'] == sample_provider.email
    
    def test_email_content_formatting(self, email_service, sample_customer, sample_provider, sample_service, sample_booking):
        """Test that email content is properly formatted"""
        result = email_service.send_booking_confirmation(sample_customer, sample_provider, sample_service, sample_booking)
        
        with open(result, 'r') as f:
            content = f.read()
            
            # Check HTML structure
            assert "<html>" in content
            assert "<body>" in content
            assert "</body>" in content
            assert "</html>" in content
            
            # Check specific content elements
            assert f"Hello {sample_customer.profile.firstName}" in content
            assert f"<strong>Service:</strong> {sample_service.title}" in content
            assert f"<strong>Provider:</strong> {sample_provider.profile.firstName}" in content
            assert f"<strong>Price:</strong> ${sample_service.price}" in content
    
    def test_email_with_notes(self, email_service, sample_customer, sample_provider, sample_service, sample_booking):
        """Test email content with booking notes"""
        sample_booking.notes = "Please clean the kitchen thoroughly"
        
        result = email_service.send_booking_confirmation(sample_customer, sample_provider, sample_service, sample_booking)
        
        with open(result, 'r') as f:
            content = f.read()
            assert sample_booking.notes in content
    
    def test_email_without_notes(self, email_service, sample_customer, sample_provider, sample_service, sample_booking):
        """Test email content without booking notes"""
        sample_booking.notes = None
        
        result = email_service.send_booking_confirmation(sample_customer, sample_provider, sample_service, sample_booking)
        
        with open(result, 'r') as f:
            content = f.read()
            # Should not contain notes section or show N/A
            assert "N/A" in content or "notes" not in content.lower()
    
    def test_email_service_initialization(self):
        """Test EmailService initialization"""
        # Test with default directory
        service1 = EmailService()
        assert os.path.exists(service1.output_dir)
        
        # Test with custom directory
        with tempfile.TemporaryDirectory() as temp_dir:
            service2 = EmailService(output_dir=temp_dir)
            assert service2.output_dir == temp_dir
    
    def test_email_service_directory_creation(self):
        """Test that EmailService creates directory if it doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_dir = os.path.join(temp_dir, "custom_emails")
            service = EmailService(output_dir=custom_dir)
            
            # Directory should be created
            assert os.path.exists(custom_dir)
            assert os.path.isdir(custom_dir)

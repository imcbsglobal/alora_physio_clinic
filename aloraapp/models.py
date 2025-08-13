from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone

class Booking(models.Model):
    name = models.CharField(max_length=100, verbose_name="Patient Name")
    mobile = models.CharField(max_length=15, verbose_name="Mobile Number")
    branch = models.CharField(max_length=50, verbose_name="Clinic Branch")
    service = models.CharField(max_length=50, verbose_name="Service Type")
    date = models.DateField(verbose_name="Appointment Date")
    time = models.CharField(max_length=10, verbose_name="Appointment Time")
    created_at = models.DateTimeField(auto_now_add=True)  # Changed from default=timezone.now

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.service} on {self.date}"
    





    from django.db import models

class ContactSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submission_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contact from {self.name} ({self.email})"
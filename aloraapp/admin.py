from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['name', 'mobile', 'service', 'branch', 'date', 'time', 'created_at']
    list_filter = ['branch', 'service', 'date', 'created_at']
    search_fields = ['name', 'mobile', 'service']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('name', 'mobile')
        }),
        ('Appointment Details', {
            'fields': ('branch', 'service', 'date', 'time')
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)
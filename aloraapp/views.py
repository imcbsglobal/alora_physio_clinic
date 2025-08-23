import datetime
from logging import DEBUG
from pyexpat.errors import messages
import traceback
from venv import logger
from django.shortcuts import render
from django.http import BadHeaderError, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from .models import Booking
import json
from django.middleware.csrf import get_token
from django.db import transaction
from datetime import datetime, date
from django.conf import settings

# Regular views
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def booking(request):
    return render(request, 'booking.html')

def services(request):
    return render(request, 'services.html')

def media(request):
    return render(request, 'media.html')

def contact(request):
    return render(request, 'contact.html')

def dashboard(request):
    return render(request, 'dashboard.html')

from django.shortcuts import redirect
from django.contrib.auth import authenticate, login

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

# Test API endpoint
def test_api(request):
    """Simple test endpoint to check if API is working"""
    return JsonResponse({
        'status': 'success',
        'message': 'API is working!',
        'method': request.method,
        'path': request.path,
        'timestamp': datetime.now().isoformat()
    })

# API Views
@csrf_exempt  # This disables CSRF for this view since we're handling it manually
@require_http_methods(["POST"])
@transaction.atomic
def create_booking(request):
    try:
        # Debug: Print request info
        print(f"Request method: {request.method}")
        print(f"Content type: {request.content_type}")
        print(f"Raw request body: {request.body}")
        
        # Parse JSON data
        try:
            data = json.loads(request.body)
            print(f"Parsed JSON data: {data}")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data',
                'detail': str(e)
            }, status=400)

        # Validate required fields
        required_fields = ['name', 'mobile', 'branch', 'service', 'date', 'time']
        missing_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(f"{field} (missing)")
            elif not data[field] or str(data[field]).strip() == "":
                missing_fields.append(f"{field} (empty)")
        
        if missing_fields:
            print(f"Missing/empty fields: {missing_fields}")
            return JsonResponse({
                'status': 'error',
                'message': 'Missing or empty required fields',
                'missing_fields': missing_fields,
                'received_data': data
            }, status=400)

        # Validate and parse date
        try:
            booking_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            if booking_date < date.today():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Appointment date cannot be in the past'
                }, status=400)
        except ValueError as e:
            print(f"Date parsing error: {e}")
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid date format. Use YYYY-MM-DD',
                'detail': str(e)
            }, status=400)

        # Validate mobile number
        mobile = str(data['mobile']).strip()
        if not mobile.isdigit() or len(mobile) < 10 or len(mobile) > 15:
            return JsonResponse({
                'status': 'error',
                'message': 'Mobile number must be 10-15 digits'
            }, status=400)

        # Create and save booking
        try:
            booking = Booking.objects.create(
                name=str(data['name']).strip(),
                mobile=mobile,
                branch=str(data['branch']).strip(),
                service=str(data['service']).strip(),
                date=booking_date,
                time=str(data['time']).strip()
            )
            
            # Force save and refresh from database
            booking.save()
            booking.refresh_from_db()
            
            print(f"✅ Booking created successfully - ID: {booking.id}, Name: {booking.name}")
            
            return JsonResponse({
                'status': 'success',
                'id': booking.id,
                'message': 'Booking created successfully',
                'data': {
                    'id': booking.id,
                    'name': booking.name,
                    'mobile': booking.mobile,
                    'branch': booking.branch,
                    'service': booking.service,
                    'date': booking.date.isoformat(),
                    'time': booking.time,
                    'created_at': booking.created_at.isoformat()
                }
            }, status=201)
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to save booking to database',
                'detail': str(e),
                'traceback': traceback.format_exc() if settings.DEBUG else None
            }, status=500)

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error',
            'detail': str(e),
            'traceback': traceback.format_exc() if settings.DEBUG else None
        }, status=500)

@require_http_methods(["GET"])
def list_bookings(request):
    try:
        print("📋 Listing bookings...")
        
        # Get all bookings with error handling
        try:
            bookings = Booking.objects.all().order_by('-created_at')
            count = bookings.count()
            print(f"📊 Found {count} bookings in database")
            
            # Convert to list with detailed logging
            bookings_data = []
            for booking in bookings:
                booking_dict = {
                    'id': booking.id,
                    'name': booking.name,
                    'mobile': booking.mobile,
                    'branch': booking.branch,
                    'service': booking.service,
                    'date': booking.date.isoformat(),
                    'time': booking.time,
                    'created_at': booking.created_at.isoformat()
                }
                bookings_data.append(booking_dict)
                print(f"  📝 Booking {booking.id}: {booking.name} - {booking.service}")
            
            return JsonResponse({
                'status': 'success',
                'count': count,
                'bookings': bookings_data
            })
            
        except Exception as db_error:
            print(f"❌ Database query error: {db_error}")
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to retrieve bookings from database',
                'detail': str(db_error)
            }, status=500)
            
    except Exception as e:
        print(f"❌ Error in list_bookings: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error',
            'detail': str(e),
            'traceback': traceback.format_exc() if settings.DEBUG else None
        }, status=500)
    






from django.http import HttpResponse
from django.shortcuts import render
import xlwt
from datetime import datetime
from .models import ContactSubmission  # Assuming you have a model for contact submissions

def export_contacts(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="contacts.xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Contacts')
    
    # Header row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    
    columns = ['Name', 'Email', 'Message', 'Submission Date']
    
    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)
    
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Convert string dates to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Filter submissions by date range
    submissions = ContactSubmission.objects.filter(
        submission_date__gte=start_date,
        submission_date__lte=end_date
    ).order_by('submission_date')
    
    # Data rows
    font_style = xlwt.XFStyle()
    
    for row, submission in enumerate(submissions, 1):
        ws.write(row, 0, submission.name, font_style)
        ws.write(row, 1, submission.email, font_style)
        ws.write(row, 2, submission.message, font_style)
        ws.write(row, 3, submission.submission_date.strftime('%Y-%m-%d'), font_style)
    
    wb.save(response)
    return response



from django.conf import settings
from django.core.mail import send_mail, BadHeaderError, EmailMessage, get_connection
from django.shortcuts import render, redirect
from django.contrib import messages

def contact_view(request):
    """
    Sends an email and shows clear, actionable error messages when it fails.
    Also adds a DEBUG-only trace so you can see what's wrong.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not all([name, email, subject, message]):
            messages.error(request, "Please fill in all fields.")
            return redirect('contact')

        # Decide who receives the contact mail
        recipients = getattr(settings, "CONTACT_RECIPIENTS", None) or \
                     [getattr(settings, "EMAIL_HOST_USER", "") or getattr(settings, "DEFAULT_FROM_EMAIL", "")]
        recipients = [r for r in recipients if r]  # drop empties

        if not recipients:
            messages.error(request, "Email is not configured: set CONTACT_RECIPIENTS or EMAIL_HOST_USER/DEFAULT_FROM_EMAIL in settings.")
            return redirect('contact')

        body = f"From: {name} <{email}>\n\n{message}"

        try:
            # Use EmailMessage so we can set reply_to (helps replying to the user)
            em = EmailMessage(
                subject=subject,
                body=body,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", getattr(settings, "EMAIL_HOST_USER", None)),
                to=recipients,
                reply_to=[email] if email else None,
            )

            # Open connection explicitly to surface connection/auth errors
            with get_connection(
                backend=getattr(settings, "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"),
                host=getattr(settings, "EMAIL_HOST", None),
                port=getattr(settings, "EMAIL_PORT", None),
                username=getattr(settings, "EMAIL_HOST_USER", None),
                password=getattr(settings, "EMAIL_HOST_PASSWORD", None),
                use_tls=getattr(settings, "EMAIL_USE_TLS", False),
                use_ssl=getattr(settings, "EMAIL_USE_SSL", False),
                timeout=20,
            ) as conn:
                conn.send_messages([em])

        except BadHeaderError:
            messages.error(request, "Invalid header found.")
            return redirect('contact')
        except Exception as e:
            # Show full details only when DEBUG = True
            if getattr(settings, "DEBUG", False):
                messages.error(request, f"Email failed: {type(e).__name__}: {e}")
            else:
                messages.error(request, "Sorry, we couldn't send your message. Please try again later.")
            return redirect('contact')

        messages.success(request, "Thanks! Your message has been sent.")
        return redirect('contact')

    # GET
    # Tiny DEBUG breadcrumb so you can see if the page loaded the right view
    if getattr(settings, "DEBUG", False):
        messages.info(request, "Loaded contact_view ✅")
    return render(request, 'contact.html')


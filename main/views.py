import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Order, Payment, PurchasedCourse, Course
from django.views.decorators.http import require_POST

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Course, Order

@login_required
def create_checkout(request, slug):
    import razorpay
    from django.conf import settings

    try:
        course = Course.objects.get(slug=slug)
    except Course.DoesNotExist:
        return JsonResponse({"error": "course_not_found"}, status=404)

    amount_paise = int(course.price * 100)

    # Create Razorpay order
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payment = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": "1"
    })

    # Save order in DB
    order = Order.objects.create(
        user=request.user,
        course=course,
        amount=amount_paise,
        razorpay_order_id=payment["id"]
    )

    return JsonResponse({
        "order_id": payment["id"],
        "amount": amount_paise,
        "key": settings.RAZORPAY_KEY_ID,
        "course_title": course.title,
        "order_db_id": order.id
    })



from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from .models import Order, Payment, PurchasedCourse

@require_POST
@login_required
def verify_payment(request):
    """
    Mock-friendly verify endpoint.
    The frontend will POST form data containing:
      - order_db_id
      - razorpay_payment_id (optional in mock)
      - razorpay_order_id (optional in mock)
      - razorpay_signature (optional in mock)
    We will mark the Order as paid and create a PurchasedCourse.
    """
    order_db_id = request.POST.get('order_db_id')
    if not order_db_id:
        return HttpResponseBadRequest("Missing order_db_id")

    try:
        order = Order.objects.get(id=order_db_id, user=request.user)
    except Order.DoesNotExist:
        return JsonResponse({"status": "failure", "message": "Order not found"}, status=404)

    # In mock flow: accept as success and mark paid
    order.paid = True
    order.save()

    # Create fake Payment record (optional)
    razorpay_payment_id = request.POST.get('razorpay_payment_id') or f"mock_pay_{order.id}"
    razorpay_signature = request.POST.get('razorpay_signature') or "mock_signature"

    try:
        Payment.objects.create(
            order=order,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature
        )
    except Exception:
        pass

    # give ownership to user
    PurchasedCourse.objects.get_or_create(user=request.user, course=order.course)

    return JsonResponse({"status": "success"})



from django.shortcuts import render, get_object_or_404
from .models import Course

def home(request):
    return render(request, 'main/index.html')

def courses_list(request):
    courses = Course.objects.all()
    return render(request, 'main/courses.html', {'courses': courses})

from django.shortcuts import render, get_object_or_404
from .models import Course
from urllib.parse import urlparse, parse_qs

def make_embed_url(url: str) -> str:
    """
    Convert YouTube URLs to embed URLs.
    Example: https://www.youtube.com/watch?v=ID -> https://www.youtube.com/embed/ID
    """
    if not url:
        return ""
    url = url.strip()
    if "youtube.com" in url:
        if "watch?v=" in url:
            return url.replace("watch?v=", "embed/")
        parsed = urlparse(url)
        q = parse_qs(parsed.query)
        if "v" in q:
            return f"https://www.youtube.com/embed/{q['v'][0]}"
    if "youtu.be" in url:
        parts = url.split("/")
        video_id = parts[-1]
        return f"https://www.youtube.com/embed/{video_id}"
    return url

def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    lessons = list(course.lessons.all())
    for lesson in lessons:
        lesson.embed_url = make_embed_url(lesson.video_url)
    return render(request, 'main/course_detail.html', {'course': course, 'lessons': lessons})

# ---- Payment Result Pages ----
from django.shortcuts import render

def payment_success(request):
    return render(request, "main/payment_success.html")

def payment_failed(request):
    return render(request, "main/payment_failed.html")


from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def my_courses(request):
    """
    Show courses the logged-in user has purchased.
    """
    purchased = request.user.purchasedcourse_set.select_related('course').all()
    courses = [p.course for p in purchased]
    return render(request, 'main/my_courses.html', {'courses': courses})

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from .models import ContactMessage

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        # Save message to database
        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message
        )

        messages.success(request, "Thanks for contacting us! We'll reach out soon.")
        return redirect("contact")

    return render(request, "main/contact.html")

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'main/my_orders.html', {'orders': orders})

def contact(request):
    return render(request, 'main/contact.html')

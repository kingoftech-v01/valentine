import re
from datetime import date

from django.db.models import Count


def extract_youtube_id(url):
    """Extract YouTube video ID from various URL formats."""
    if not url:
        return None
    patterns = [
        r'(?:youtube\.com/watch\?.*v=|youtu\.be/|youtube\.com/embed/|music\.youtube\.com/watch\?.*v=)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def check_rate_limit(ip, recipient_name):
    """Check if this IP has sent to fewer than 3 distinct recipients today.
    Re-sending to the same recipient is allowed."""
    from core.models import Valentine

    today = date.today()
    distinct_recipients = (
        Valentine.objects.filter(sender_ip=ip, created_at__date=today)
        .values("recipient_name")
        .annotate(c=Count("id"))
        .count()
    )

    # If already sent to this recipient today, it doesn't count as new
    already_sent_to_this = Valentine.objects.filter(
        sender_ip=ip, created_at__date=today, recipient_name__iexact=recipient_name
    ).exists()

    if already_sent_to_this:
        return True

    return distinct_recipients < 3


def get_client_ip(request):
    """Get client IP from request, supporting proxies."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")

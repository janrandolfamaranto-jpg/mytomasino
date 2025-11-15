
from tickets.models import Notification

def notifications(request):
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).order_by('-created_at')[:5]  # Get latest 5 unread
        
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return {
            'notifications': unread_notifications,
            'unread_count': unread_count
        }
    return {
        'notifications': [],
        'unread_count': 0
    }
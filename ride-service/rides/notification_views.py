from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing user notifications
    """
    serializer_class = NotificationSerializer

    def get_queryset(self):
        """
        Return notifications for authenticated user only
        """
        user_id = getattr(self.request, 'user_id', None)
        
        if not user_id:
            return Notification.objects.none()
        
        return Notification.objects.filter(user_id=user_id)

    def list(self, request, *args, **kwargs):
        """
        GET /api/notifications/
        List all notifications for current user
        """
        queryset = self.get_queryset()
        
        # Optional filtering
        is_read = request.query_params.get('is_read', None)
        if is_read is not None:
            is_read_bool = is_read.lower() == 'true'
            queryset = queryset.filter(is_read=is_read_bool)
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            "count": queryset.count(),
            "unread_count": queryset.filter(is_read=False).count(),
            "notifications": serializer.data
        })

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        """
        POST /api/notifications/{id}/mark_as_read/
        Mark a notification as read
        """
        user_id = getattr(request, 'user_id', None)
        
        try:
            notification = Notification.objects.get(pk=pk, user_id=user_id)
        except Notification.DoesNotExist:
            return Response(
                {"detail": "Notification not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        notification.is_read = True
        notification.save()
        
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=["post"])
    def mark_all_as_read(self, request):
        """
        POST /api/notifications/mark_all_as_read/
        Mark all notifications as read for current user
        """
        user_id = getattr(request, 'user_id', None)
        
        updated = Notification.objects.filter(
            user_id=user_id,
            is_read=False
        ).update(is_read=True)
        
        return Response({
            "detail": f"Marked {updated} notifications as read"
        })

    @action(detail=False, methods=["get"])
    def unread(self, request):
        """
        GET /api/notifications/unread/
        Get only unread notifications
        """
        user_id = getattr(request, 'user_id', None)
        
        notifications = Notification.objects.filter(
            user_id=user_id,
            is_read=False
        )
        
        serializer = self.get_serializer(notifications, many=True)
        
        return Response({
            "count": notifications.count(),
            "notifications": serializer.data
        })

    @action(detail=False, methods=["get"])
    def poll(self, request):
        """
        GET /api/notifications/poll/?since=<timestamp>
        Real-time polling endpoint for new notifications
        Returns notifications created after 'since' timestamp
        """
        user_id = getattr(request, 'user_id', None)
        
        # Get 'since' parameter (ISO format timestamp)
        since = request.query_params.get('since', None)
        
        if since:
            try:
                since_time = timezone.datetime.fromisoformat(since.replace('Z', '+00:00'))
            except ValueError:
                return Response(
                    {"detail": "Invalid 'since' timestamp format"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Default: last 5 minutes
            since_time = timezone.now() - timedelta(minutes=5)
        
        # Get new notifications
        new_notifications = Notification.objects.filter(
            user_id=user_id,
            created_at__gt=since_time
        ).order_by('-created_at')
        
        serializer = self.get_serializer(new_notifications, many=True)
        
        return Response({
            "count": new_notifications.count(),
            "notifications": serializer.data,
            "timestamp": timezone.now().isoformat()
        })
from .models import Notification, Ride

class NotificationService:
    """
    Service to create and manage notifications
    """
    
    @staticmethod
    def create_notification(user_id, ride, notification_type, title, message):
        """
        Create a notification for a user about a ride event
        """
        notification = Notification.objects.create(
            user_id=user_id,
            ride=ride,
            notification_type=notification_type,
            title=title,
            message=message
        )
        return notification
    
    #  PASSENGER NOTIFICATIONS 
    
    @staticmethod
    def notify_ride_requested(ride):
        """
        Notify passenger that their ride request was received
        """
        return NotificationService.create_notification(
            user_id=ride.passenger,
            ride=ride,
            notification_type='ride_requested',
            title='Ride Request Received',
            message=f'Your ride from {ride.origin} to {ride.destination} has been requested. Searching for a driver...'
        )
    
    @staticmethod
    def notify_ride_offered(ride):
        """
        Notify driver about new ride offer
        """
        if not ride.driver:
            return None
            
        return NotificationService.create_notification(
            user_id=ride.driver,
            ride=ride,
            notification_type='ride_offered',
            title='New Ride Offer',
            message=f'New ride available from {ride.origin} to {ride.destination}. Do you want to accept?'
        )
    
    @staticmethod
    def notify_ride_accepted(ride):
        """
        Notify passenger that driver accepted their ride
        """
        return NotificationService.create_notification(
            user_id=ride.passenger,
            ride=ride,
            notification_type='ride_accepted',
            title='Driver Accepted Your Ride',
            message=f'A driver has accepted your ride! They will pick you up at {ride.origin}.'
        )
    
    @staticmethod
    def notify_ride_rejected(ride):
        """
        Notify passenger that driver rejected their ride
        """
        return NotificationService.create_notification(
            user_id=ride.passenger,
            ride=ride,
            notification_type='ride_rejected',
            title='Driver Rejected Ride',
            message=f'The driver rejected your ride. Searching for another driver...'
        )
    
    @staticmethod
    def notify_ride_completed(ride):
        """
        Notify both passenger and driver that ride is completed
        """
        notifications = []
        
        # Notify passenger
        notifications.append(
            NotificationService.create_notification(
                user_id=ride.passenger,
                ride=ride,
                notification_type='ride_completed',
                title='Ride Completed',
                message=f'Your ride has been completed. Total: ${ride.price}'
            )
        )
        
        # Notify driver
        if ride.driver:
            notifications.append(
                NotificationService.create_notification(
                    user_id=ride.driver,
                    ride=ride,
                    notification_type='ride_completed',
                    title='Ride Completed',
                    message=f'Ride completed successfully. You earned ${ride.price}'
                )
            )
        
        return notifications
    
    @staticmethod
    def notify_ride_cancelled(ride, cancelled_by_user_id):
        """
        Notify the other party that ride was cancelled
        """
        # If passenger cancelled, notify driver
        if ride.driver and cancelled_by_user_id == ride.passenger:
            return NotificationService.create_notification(
                user_id=ride.driver,
                ride=ride,
                notification_type='ride_cancelled',
                title='Ride Cancelled by Passenger',
                message=f'The passenger cancelled the ride from {ride.origin} to {ride.destination}.'
            )
        
        # If driver cancelled, notify passenger
        elif cancelled_by_user_id == ride.driver:
            return NotificationService.create_notification(
                user_id=ride.passenger,
                ride=ride,
                notification_type='ride_cancelled',
                title='Ride Cancelled by Driver',
                message=f'Your driver cancelled the ride. Searching for another driver...'
            )
        
        return None
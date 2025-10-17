"""
Services - lógica de negócio da aplicação.
"""

from app.services.user_service import (
    UserService,
    UserServiceError,
)

from app.services.politician_service import (
    PoliticianService,
    PoliticianServiceError,
)

from app.services.follow_service import (
    FollowService,
    FollowServiceError,
)

from app.services.notification_service import (
    NotificationService,
    NotificationServiceError,
)

__all__ = [
    # User Service
    "UserService",
    "UserServiceError",
    # Politician Service
    "PoliticianService",
    "PoliticianServiceError",
    # Follow Service
    "FollowService",
    "FollowServiceError",
    # Notification Service
    "NotificationService",
    "NotificationServiceError",
]

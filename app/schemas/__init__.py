"""
Schemas Pydantic - validação de request/response.
"""

from app.schemas.user import (
    PlanType,
    UserPreferences,
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    PlanResponse,
)

from app.schemas.politician import (
    PoliticalPosition,
    SocialMedia,
    PoliticianBase,
    PoliticianCreate,
    PoliticianUpdate,
    PoliticianResponse,
    PoliticianListResponse,
    PoliticianFilters,
)

from app.schemas.follow import (
    FollowBase,
    FollowCreate,
    FollowResponse,
    FollowListResponse,
    FollowStatsResponse,
)

from app.schemas.notification import (
    NotificationStatus,
    EventType,
    NotificationBase,
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationListResponse,
    NotificationStatsResponse,
)

from app.schemas.political_event import (
    PoliticalEventBase,
    PoliticalEventCreate,
    PoliticalEventResponse,
    PoliticalEventListResponse,
    PoliticalEventFilters,
)

__all__ = [
    # User
    "PlanType",
    "UserPreferences",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponse",
    "PlanResponse",
    # Politician
    "PoliticalPosition",
    "SocialMedia",
    "PoliticianBase",
    "PoliticianCreate",
    "PoliticianUpdate",
    "PoliticianResponse",
    "PoliticianListResponse",
    "PoliticianFilters",
    # Follow
    "FollowBase",
    "FollowCreate",
    "FollowResponse",
    "FollowListResponse",
    "FollowStatsResponse",
    # Notification
    "NotificationStatus",
    "EventType",
    "NotificationBase",
    "NotificationCreate",
    "NotificationUpdate",
    "NotificationResponse",
    "NotificationListResponse",
    "NotificationStatsResponse",
    # Political Event
    "PoliticalEventBase",
    "PoliticalEventCreate",
    "PoliticalEventResponse",
    "PoliticalEventListResponse",
    "PoliticalEventFilters",
]

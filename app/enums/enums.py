import enum

class OrderStatus(enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    PAID = "PAID"

class UserRoles(enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    CUSTOMER = "CUSTOMER"
    SELLER = "SELLER"


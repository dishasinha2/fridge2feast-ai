"""User data model."""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class User:
    id: Optional[int]
    email: str
    name: str
    password_hash: str = ""
    salt: str = ""
    created_at: str = ""
    preferences: Dict[str, Any] = field(default_factory=dict)

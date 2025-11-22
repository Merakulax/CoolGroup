"""
User Profile Models - Python
Auto-generated from contracts/user_profile.json
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class UserProfile:
    """User profile and preferences"""
    user_id: str
    name: str
    pet_name: str
    age: Optional[int] = None
    health_goals: List[str] = field(default_factory=list)
    avatar_url: Optional[str] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        result = {
            'user_id': self.user_id,
            'name': self.name,
            'pet_name': self.pet_name,
            'health_goals': self.health_goals
        }
        if self.age is not None:
            result['age'] = self.age
        if self.avatar_url:
            result['avatar_url'] = self.avatar_url
        return result

    @staticmethod
    def from_dict(data: dict) -> 'UserProfile':
        """Create from dictionary (e.g., from JSON)"""
        return UserProfile(
            user_id=data['user_id'],
            name=data['name'],
            pet_name=data['pet_name'],
            age=data.get('age'),
            health_goals=data.get('health_goals', []),
            avatar_url=data.get('avatar_url')
        )

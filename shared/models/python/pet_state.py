"""
Pet State Models - Python
Auto-generated from contracts/pet_state.json
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class PetMood(Enum):
    HAPPY = "Happy"
    ENERGETIC = "Energetic"
    SLEEPY = "Sleepy"
    CONCERNED = "Concerned"
    ANXIOUS = "Anxious"
    RECOVERING = "Recovering"
    PROUD = "Proud"


class Animation(Enum):
    SMILE = "smile"
    JUMP = "jump"
    SLEEP = "sleep"
    WORRY = "worry"
    CELEBRATE = "celebrate"
    BREATHE = "breathe"


class HapticPattern(Enum):
    GENTLE = "gentle"
    ALERT = "alert"
    CELEBRATION = "celebration"
    WARNING = "warning"


@dataclass
class PetState:
    """Pet state update from Cloud to Phone/Watch"""
    mood: PetMood
    energy: int  # 0-100 percentage
    timestamp: int
    message: Optional[str] = None
    animation: Optional[Animation] = None
    haptic_pattern: Optional[HapticPattern] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        result = {
            'mood': self.mood.value,
            'energy': self.energy,
            'timestamp': self.timestamp
        }
        if self.message:
            result['message'] = self.message
        if self.animation:
            result['animation'] = self.animation.value
        if self.haptic_pattern:
            result['hapticPattern'] = self.haptic_pattern.value

        return result

    @staticmethod
    def from_dict(data: dict) -> 'PetState':
        """Create from dictionary (e.g., from JSON)"""
        return PetState(
            mood=PetMood(data['mood']),
            energy=data['energy'],
            timestamp=data['timestamp'],
            message=data.get('message'),
            animation=Animation(data['animation']) if 'animation' in data else None,
            haptic_pattern=HapticPattern(data['hapticPattern']) if 'hapticPattern' in data else None
        )

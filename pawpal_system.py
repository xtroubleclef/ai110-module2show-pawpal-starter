# PawPal+ System Classes
# Classes for pet care planning and scheduling

from dataclasses import dataclass
from typing import List
from enum import Enum


class Priority(Enum):
    """Enum for task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    """Represents a pet care task."""
    title: str
    duration_minutes: int
    priority: Priority
    description: str = ""
    
    def __post_init__(self):
        """Validate task attributes."""
        pass
    
    def get_priority_level(self) -> int:
        """Return numeric priority level."""
        pass
    
    def is_urgent(self) -> bool:
        """Check if task is high priority."""
        pass


@dataclass
class Pet:
    """Represents a pet."""
    name: str
    species: str
    age: int = 0
    preferences: str = ""
    
    def __post_init__(self):
        """Validate pet attributes."""
        pass
    
    def get_care_requirements(self) -> List[str]:
        """Return list of care requirements based on species."""
        pass


@dataclass
class Owner:
    """Represents a pet owner."""
    name: str
    contact_info: str = ""
    availability: str = ""
    preferences: str = ""
    
    def __post_init__(self):
        """Validate owner attributes."""
        pass
    
    def get_available_time(self) -> int:
        """Return available time in minutes."""
        pass


class Schedule:
    """Represents a daily pet care schedule."""
    
    def __init__(self, pet: Pet, owner: Owner, tasks: List[Task]):
        """Initialize a schedule with pet, owner, and tasks."""
        self.pet = pet
        self.owner = owner
        self.tasks = tasks
        self.scheduled_tasks = []
    
    def build_schedule(self) -> List[Task]:
        """Build and return optimized task schedule."""
        pass
    
    def add_task_to_schedule(self, task: Task, start_time: int) -> None:
        """Add a task to the schedule at a specific time."""
        pass
    
    def get_schedule_explanation(self) -> str:
        """Return explanation of why tasks were scheduled in this order."""
        pass
    
    def is_feasible(self) -> bool:
        """Check if schedule fits within available time."""
        pass

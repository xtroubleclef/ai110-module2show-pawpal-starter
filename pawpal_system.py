# PawPal+ System Classes
# Classes for pet care planning and scheduling

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
from datetime import datetime


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
    completed: bool = False
    frequency: str = "daily"  # daily, weekly, as-needed
    
    def __post_init__(self):
        """Validate task attributes."""
        if self.duration_minutes <= 0:
            raise ValueError("Duration must be positive")
        if not self.title:
            raise ValueError("Task title cannot be empty")
    
    def get_priority_level(self) -> int:
        """Return numeric priority level."""
        return self.priority.value
    
    def is_urgent(self) -> bool:
        """Check if task is high priority."""
        return self.priority == Priority.HIGH
    
    def mark_completed(self) -> None:
        """Mark the task as completed."""
        self.completed = True
    
    def __str__(self) -> str:
        """Return string representation of task."""
        return f"{self.title} ({self.duration_minutes}min, {self.priority.name})"


@dataclass
class Pet:
    """Represents a pet."""
    name: str
    species: str
    age: int = 0
    preferences: str = ""
    tasks: List[Task] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate pet attributes."""
        if not self.name:
            raise ValueError("Pet name cannot be empty")
        if not self.species:
            raise ValueError("Species cannot be empty")
        if self.age < 0:
            raise ValueError("Age cannot be negative")
    
    def get_care_requirements(self) -> List[str]:
        """Return list of care requirements based on species."""
        requirements = {
            "dog": ["walk", "feed", "play", "bathroom"],
            "cat": ["feed", "litter box", "play", "grooming"],
            "rabbit": ["feed", "hay", "exercise", "clean cage"],
            "bird": ["feed", "water", "cleaning", "interaction"],
        }
        return requirements.get(self.species.lower(), ["feed", "water", "clean"])
    
    def add_task(self, task: Task) -> None:
        """Add a task to the pet's task list."""
        self.tasks.append(task)
    
    def get_all_tasks(self) -> List[Task]:
        """Return all tasks for this pet."""
        return self.tasks
    
    def get_urgent_tasks(self) -> List[Task]:
        """Return only urgent (high priority) tasks."""
        return [task for task in self.tasks if task.is_urgent()]
    
    def __str__(self) -> str:
        """Return string representation of pet."""
        return f"{self.name} ({self.species}, {self.age} years old)"


@dataclass
class Owner:
    """Represents a pet owner."""
    name: str
    contact_info: str = ""
    availability_minutes: int = 480  # Default 8 hours per day
    preferences: str = ""
    pets: List[Pet] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate owner attributes."""
        if not self.name:
            raise ValueError("Owner name cannot be empty")
        if self.availability_minutes <= 0:
            raise ValueError("Availability must be positive")
    
    def get_available_time(self) -> int:
        """Return available time in minutes."""
        return self.availability_minutes
    
    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's list."""
        self.pets.append(pet)
    
    def get_all_pets(self) -> List[Pet]:
        """Return all pets owned by this owner."""
        return self.pets
    
    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks across all owned pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_all_tasks())
        return all_tasks
    
    def get_pet_by_name(self, pet_name: str) -> Optional[Pet]:
        """Get a specific pet by name."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return pet
        return None
    
    def __str__(self) -> str:
        """Return string representation of owner."""
        return f"{self.name} ({len(self.pets)} pet(s))"


class Schedule:
    """Represents a daily pet care schedule."""
    
    def __init__(self, owner: Owner, tasks: Optional[List[Task]] = None):
        """Initialize a schedule with an owner and optional task list."""
        self.owner = owner
        # If no tasks provided, retrieve all tasks from owner's pets
        self.tasks = tasks if tasks is not None else owner.get_all_tasks()
        self.scheduled_tasks: List[tuple[Task, int]] = []  # List of (task, start_time_in_minutes)
        self.total_time_used = 0
    
    def build_schedule(self) -> List[tuple[Task, int]]:
        """Build and return optimized task schedule based on priority and time constraints."""
        if not self.tasks:
            return []
        
        # Sort tasks by priority (high first) then by duration (shorter first for efficiency)
        sorted_tasks = sorted(
            self.tasks,
            key=lambda t: (-t.get_priority_level(), t.duration_minutes)
        )
        
        # Greedily add tasks to schedule if they fit
        self.scheduled_tasks = []
        self.total_time_used = 0
        current_time = 0
        
        for task in sorted_tasks:
            if current_time + task.duration_minutes <= self.owner.get_available_time():
                self.scheduled_tasks.append((task, current_time))
                current_time += task.duration_minutes
                self.total_time_used += task.duration_minutes
        
        return self.scheduled_tasks
    
    def add_task_to_schedule(self, task: Task, start_time: int) -> bool:
        """Add a task to the schedule at a specific time. Returns True if successful."""
        # Check for time conflicts
        end_time = start_time + task.duration_minutes
        
        for scheduled_task, scheduled_time in self.scheduled_tasks:
            scheduled_end = scheduled_time + scheduled_task.duration_minutes
            # Check if there's overlap
            if not (end_time <= scheduled_time or start_time >= scheduled_end):
                return False  # Conflict detected
        
        # Check if it fits within available time
        if end_time > self.owner.get_available_time():
            return False
        
        self.scheduled_tasks.append((task, start_time))
        self.total_time_used += task.duration_minutes
        return True
    
    def get_schedule_explanation(self) -> str:
        """Return explanation of why tasks were scheduled in this order."""
        if not self.scheduled_tasks:
            return "No tasks could be scheduled within the available time."
        
        explanation = f"Schedule for {self.owner.name}:\n"
        explanation += f"Available time: {self.owner.get_available_time()} minutes\n"
        explanation += f"Total time used: {self.total_time_used} minutes\n\n"
        explanation += "Tasks scheduled (in order):\n"
        
        for i, (task, start_time) in enumerate(self.scheduled_tasks, 1):
            hours = start_time // 60
            minutes = start_time % 60
            end_time = start_time + task.duration_minutes
            end_hours = end_time // 60
            end_minutes = end_time % 60
            
            explanation += f"{i}. {task.title}\n"
            explanation += f"   Time: {hours:02d}:{minutes:02d} - {end_hours:02d}:{end_minutes:02d}\n"
            explanation += f"   Duration: {task.duration_minutes} minutes\n"
            explanation += f"   Priority: {task.priority.name}\n"
            explanation += f"   Reason: {self._get_scheduling_reason(task)}\n\n"
        
        return explanation
    
    def _get_scheduling_reason(self, task: Task) -> str:
        """Generate explanation for why a task was scheduled."""
        if task.is_urgent():
            return "High priority - scheduled early to ensure completion"
        elif task.duration_minutes <= 15:
            return "Short duration - fits efficiently into schedule"
        else:
            return "Included based on priority and available time"
    
    def is_feasible(self) -> bool:
        """Check if all high-priority tasks fit within available time."""
        urgent_tasks = [t for t in self.tasks if t.is_urgent()]
        urgent_time = sum(t.duration_minutes for t in urgent_tasks)
        return urgent_time <= self.owner.get_available_time()
    
    def get_unscheduled_tasks(self) -> List[Task]:
        """Return tasks that could not be fit into the schedule."""
        scheduled_task_set = {task for task, _ in self.scheduled_tasks}
        return [task for task in self.tasks if task not in scheduled_task_set]
    
    def __str__(self) -> str:
        """Return string representation of schedule."""
        return f"Schedule for {self.owner.name}: {len(self.scheduled_tasks)} tasks scheduled"


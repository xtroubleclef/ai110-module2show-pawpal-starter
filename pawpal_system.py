# PawPal+ System Classes
# Classes for pet care planning and scheduling

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
from enum import Enum
from datetime import datetime, timedelta
from copy import copy


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
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate task attributes."""
        if self.duration_minutes <= 0:
            raise ValueError("Duration must be positive")
        if not self.title:
            raise ValueError("Task title cannot be empty")
        # Set default due date to today if not specified
        if self.due_date is None:
            self.due_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    def get_priority_level(self) -> int:
        """Return numeric priority level."""
        return self.priority.value
    
    def is_urgent(self) -> bool:
        """Check if task is high priority."""
        return self.priority == Priority.HIGH
    
    def mark_completed(self) -> Optional['Task']:
        """Mark the task as completed and create next occurrence if recurring.
        
        Returns:
            New Task instance for next occurrence (if recurring), else None.
        """
        self.completed = True
        self.completed_at = datetime.now()
        
        # If task is recurring, create next occurrence
        if self.frequency == "daily":
            next_task = self._create_next_occurrence(days=1)
            return next_task
        elif self.frequency == "weekly":
            next_task = self._create_next_occurrence(days=7)
            return next_task
        
        return None
    
    def _create_next_occurrence(self, days: int) -> "Task":
        """Create a new task instance for the next occurrence.
        
        Args:
            days: Number of days until next occurrence
        
        Returns:
            New Task with due date updated by timedelta.
        """
        next_due_date = self.due_date + timedelta(days=days) if self.due_date else datetime.now() + timedelta(days=days)
        
        next_task = Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            description=self.description,
            completed=False,
            frequency=self.frequency,
            due_date=next_due_date,
            completed_at=None
        )
        return next_task
    
    def is_overdue(self) -> bool:
        """Check if task is overdue (due date is in the past)."""
        if self.completed or self.due_date is None:
            return False
        return self.due_date < datetime.now()
    
    def __str__(self) -> str:
        """Return string representation of task."""
        status = "DONE" if self.completed else "TODO"
        due_str = self.due_date.strftime("%Y-%m-%d") if self.due_date else "No date"
        return f"{self.title} ({self.duration_minutes}min, {self.priority.name}, {status}, due: {due_str})"


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
    
    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Mark a task as complete and auto-create next occurrence if recurring.
        
        Args:
            task: The task to mark complete
            
        Returns:
            New Task instance if recurring, otherwise None
        """
        # Find and mark the task
        if task in self.tasks:
            next_task = task.mark_completed()
            
            # If recurring, automatically add next occurrence
            if next_task:
                self.add_task(next_task)
                return next_task
        
        return None
    
    def get_overdue_tasks(self) -> List[Task]:
        """Return all overdue incomplete tasks."""
        return [t for t in self.tasks if t.is_overdue() and not t.completed]
    
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
    
    # ============ ALGORITHMIC METHODS - SORTING ============
    
    def get_sorted_tasks(self, sort_by: str = "priority") -> List[Task]:
        """Return all tasks sorted by specified criteria.
        
        Args:
            sort_by: "priority" (HIGH first), "duration" (short first), 
                    "pet" (grouped by pet), "frequency" (daily first)
        """
        all_tasks = self.get_all_tasks()
        
        if sort_by == "priority":
            return sorted(all_tasks, key=lambda t: -t.get_priority_level())
        elif sort_by == "duration":
            return sorted(all_tasks, key=lambda t: t.duration_minutes)
        elif sort_by == "pet":
            # Group by pet name
            return sorted(all_tasks, 
                         key=lambda t: self._get_task_pet_name(t))
        elif sort_by == "frequency":
            frequency_order = {"daily": 0, "weekly": 1, "as-needed": 2}
            return sorted(all_tasks, 
                         key=lambda t: frequency_order.get(t.frequency, 999))
        else:
            return all_tasks
    
    def _get_task_pet_name(self, task: Task) -> str:
        """Helper: Find which pet owns a task."""
        for pet in self.pets:
            if task in pet.get_all_tasks():
                return pet.name
        return "unknown"
    
    # ============ ALGORITHMIC METHODS - FILTERING ============
    
    def get_tasks_for_pet(self, pet_name: str) -> List[Task]:
        """Return only tasks for a specific pet."""
        pet = self.get_pet_by_name(pet_name)
        return pet.get_all_tasks() if pet else []
    
    def get_incomplete_tasks(self) -> List[Task]:
        """Return all incomplete tasks."""
        return [t for t in self.get_all_tasks() if not t.completed]
    
    def get_completed_tasks(self) -> List[Task]:
        """Return all completed tasks."""
        return [t for t in self.get_all_tasks() if t.completed]
    
    def get_high_priority_tasks(self) -> List[Task]:
        """Return only HIGH priority tasks."""
        return [t for t in self.get_all_tasks() if t.priority == Priority.HIGH]
    
    def get_medium_priority_tasks(self) -> List[Task]:
        """Return only MEDIUM priority tasks."""
        return [t for t in self.get_all_tasks() if t.priority == Priority.MEDIUM]
    
    def get_low_priority_tasks(self) -> List[Task]:
        """Return only LOW priority tasks."""
        return [t for t in self.get_all_tasks() if t.priority == Priority.LOW]
    
    def get_urgent_incomplete_tasks(self) -> List[Task]:
        """Return HIGH priority tasks that aren't completed yet."""
        return [t for t in self.get_all_tasks() 
                if t.priority == Priority.HIGH and not t.completed]
    
    def get_urgent_incomplete_tasks_for_pet(self, pet_name: str) -> List[Task]:
        """Return HIGH priority incomplete tasks for a specific pet."""
        pet_tasks = self.get_tasks_for_pet(pet_name)
        return [t for t in pet_tasks 
                if t.priority == Priority.HIGH and not t.completed]
    
    def get_recurring_tasks(self) -> List[Task]:
        """Return tasks that recur (daily or weekly)."""
        return [t for t in self.get_all_tasks() 
                if t.frequency in ["daily", "weekly"]]
    
    def get_task_completion_rate(self) -> float:
        """Return percentage of tasks that are completed (0.0 to 1.0)."""
        all_tasks = self.get_all_tasks()
        if not all_tasks:
            return 0.0
        completed = len(self.get_completed_tasks())
        return completed / len(all_tasks)
    
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
        self.scheduled_tasks: List[Tuple[Task, int]] = []  # List of (task, start_time_in_minutes)
        self.total_time_used = 0
    
    def build_schedule(self) -> List[Tuple[Task, int]]:
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
    
    def sort_scheduled_by_time(self) -> List[Tuple[Task, int]]:
        """Sort currently scheduled tasks by their start time (earliest first).
        
        Algorithm: O(n log n) sorting by start_time value.
        Useful for presenting the schedule in chronological order.
        
        Returns:
            List of (task, start_time) tuples sorted by start_time in ascending order.
            start_time is in minutes since midnight (e.g., 480 = 8:00 AM).
        """
        return sorted(self.scheduled_tasks, key=lambda x: x[1])
    
    def sort_tasks_by_time_format(self, tasks: List[Task]) -> List[Tuple[Task, str]]:
        """Sort tasks by time in HH:MM format (useful for display).
        
        Converts minutes to HH:MM format and sorts. Useful for presenting
        scheduled times in a human-readable format.
        
        Args:
            tasks: List of Task objects (typically from scheduled_tasks)
        
        Returns:
            List of (task, time_string) tuples sorted by time value.
        """
        task_time_pairs = []
        for task, start_time in self.scheduled_tasks:
            hours = start_time // 60
            minutes = start_time % 60
            time_str = f"{hours:02d}:{minutes:02d}"
            task_time_pairs.append((task, time_str, start_time))
        
        # Sort by the actual minutes value (third element)
        sorted_pairs = sorted(task_time_pairs, key=lambda x: x[2])
        
        # Return only task and time string
        return [(task, time_str) for task, time_str, _ in sorted_pairs]
    
    def filter_scheduled_by_completion(self, completed: bool = False) -> List[Tuple[Task, int]]:
        """Filter scheduled tasks by completion status.
        
        Args:
            completed: If True, return only completed tasks. If False, return incomplete.
        
        Returns:
            List of (task, start_time) tuples matching the completion status.
        """
        return [(task, time) for task, time in self.scheduled_tasks 
                if task.completed == completed]
    
    def filter_scheduled_by_pet(self, pet_name: str) -> List[Tuple[Task, int]]:
        """Filter scheduled tasks by pet name.
        
        Algorithm: O(n) linear scan of scheduled tasks.
        Finds all tasks belonging to a specific pet and returns them with their
        scheduled start times.
        
        Args:
            pet_name: Name of the pet to filter by (case-sensitive)
        
        Returns:
            List of (task, start_time) tuples for that pet's tasks.
            Returns empty list if pet not found or no tasks scheduled for pet.
        """
        filtered = []
        pet = self.owner.get_pet_by_name(pet_name)
        
        if not pet:
            return []
        
        pet_tasks = pet.get_all_tasks()
        
        return [(task, time) for task, time in self.scheduled_tasks 
                if task in pet_tasks]
    
    def filter_scheduled_by_priority(self, priority: Priority) -> List[Tuple[Task, int]]:
        """Filter scheduled tasks by priority level.
        
        Args:
            priority: Priority enum value (Priority.HIGH, MEDIUM, or LOW)
        
        Returns:
            List of (task, start_time) tuples matching the priority.
        """
        return [(task, time) for task, time in self.scheduled_tasks 
                if task.priority == priority]
    
    def get_tasks_by_pet_sorted(self, pet_name: str) -> List[Tuple[Task, str]]:
        """Get a pet's scheduled tasks sorted by time with HH:MM format.
        
        Convenience method combining filtering by pet and sorting by time.
        
        Args:
            pet_name: Name of the pet
        
        Returns:
            List of (task, time_string) tuples sorted by time.
        """
        pet_tasks = self.filter_scheduled_by_pet(pet_name)
        
        if not pet_tasks:
            return []
        
        # Convert to (task, time_string) format
        result = []
        for task, start_time in pet_tasks:
            hours = start_time // 60
            minutes = start_time % 60
            time_str = f"{hours:02d}:{minutes:02d}"
            result.append((task, time_str))
        
        # Sort by time
        return sorted(result, key=lambda x: x[1])
    
    def get_incomplete_scheduled_tasks_sorted(self) -> List[Tuple[Task, str]]:
        """Get incomplete scheduled tasks sorted by time.
        
        Returns:
            List of (task, time_string) tuples for incomplete tasks, sorted by time.
        """
        incomplete = self.filter_scheduled_by_completion(completed=False)
        
        result = []
        for task, start_time in incomplete:
            hours = start_time // 60
            minutes = start_time % 60
            time_str = f"{hours:02d}:{minutes:02d}"
            result.append((task, time_str))
        
        return sorted(result, key=lambda x: x[1])
    
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
        scheduled_task_objects = [task for task, _ in self.scheduled_tasks]
        return [task for task in self.tasks if task not in scheduled_task_objects]
    
    # ============ ALGORITHMIC METHODS - RECURRING TASKS ============
    
    def expand_recurring_tasks(self, num_days: int = 7) -> List[Task]:
        """Expand recurring (daily/weekly) tasks into multiple instances.
        
        Algorithm: O(n * d) where n = tasks and d = num_days.
        Useful for multi-day scheduling or planning purposes.
        
        Recurrence logic:
        - Daily tasks: Duplicated for each day (creates num_days copies)
        - Weekly tasks: Included once (assumed to repeat weekly)
        - As-needed tasks: Included once (no automatic recurrence)
        
        Args:
            num_days: Number of days to expand across (default 7 for a week)
        
        Returns:
            List of tasks with recurring tasks duplicated for each day.
            Each copy is tagged with the day number for identification.
        """
        expanded_tasks = []
        
        for task in self.tasks:
            if task.frequency == "daily":
                # Create a copy for each day
                for day in range(num_days):
                    expanded_tasks.append(self._create_task_copy(task, day))
            elif task.frequency == "weekly":
                # Just add once (weekly)
                expanded_tasks.append(task)
            else:
                # "as-needed" tasks only appear once
                expanded_tasks.append(task)
        
        return expanded_tasks
    
    def _create_task_copy(self, task: Task, day: int) -> Task:
        """Create a copy of a task with a day identifier."""
        new_task = copy(task)
        new_task.title = f"{task.title} (Day {day + 1})"
        return new_task
    
    # ============ ALGORITHMIC METHODS - CONFLICT DETECTION ============
    
    def find_conflicts_in_schedule(self) -> List[Tuple[Task, Task, int, int]]:
        """Find all overlapping tasks in the current schedule.
        
        Uses interval overlap detection to identify conflicts. Two tasks conflict
        if their scheduled time windows overlap at all.
        
        Algorithm: O(n²) comparison of all task pairs.
        - For tasks (T1, T2) with start times (S1, S2) and durations (D1, D2):
        - Tasks overlap if NOT(end1 <= start2 OR start1 >= end2)
        - Equivalently: (start1 < end2) AND (start2 < end1)
        
        This uses exact time matching without buffer time, prioritizing simplicity
        and clarity over strict time separation. See reflection.md section 2b for
        tradeoff discussion.
        
        Returns:
            List of (task1, task2, time1, time2) tuples showing conflicts.
            Each conflict represents two tasks with overlapping time windows.
        """
        conflicts = []
        
        for i, (task1, time1) in enumerate(self.scheduled_tasks):
            end1 = time1 + task1.duration_minutes
            
            for task2, time2 in self.scheduled_tasks[i + 1:]:
                end2 = time2 + task2.duration_minutes
                
                # Check if intervals overlap
                if not (end1 <= time2 or time1 >= end2):
                    conflicts.append((task1, task2, time1, time2))
        
        return conflicts
    
    def validate_schedule(self) -> Tuple[bool, str]:
        """Validate the schedule for conflicts and feasibility.
        
        Returns:
            (is_valid, message) tuple
        """
        conflicts = self.find_conflicts_in_schedule()
        
        if conflicts:
            msg = f"Schedule has {len(conflicts)} conflict(s):\n"
            for task1, task2, _, _ in conflicts:
                msg += f"  - {task1.title} overlaps with {task2.title}\n"
            return False, msg
        
        if not self.is_feasible():
            return False, "Not all high-priority tasks fit in available time"
        
        return True, "Schedule is valid!"
    
    def get_conflict_warnings(self) -> List[str]:
        """Generate lightweight conflict warnings without crashing.
        
        This is a user-friendly wrapper around find_conflicts_in_schedule() that:
        1. Identifies conflicts using interval overlap detection
        2. Determines which pet owns each conflicting task
        3. Formats times in HH:MM format for readability
        4. Generates descriptive warning messages for same-pet and cross-pet conflicts
        
        The system never crashes on conflicts; it generates warnings and returns
        them for the user to review and resolve. This enables graceful degradation
        when tasks overlap.
        
        Algorithm: O(n²) for finding conflicts + O(k log k) for generating k warnings.
        
        Returns:
            List of warning message strings. If no conflicts, returns a single
            message: "No conflicts detected. Schedule is valid!"
            
        Example output:
            "WARNING: Max's tasks 'Morning walk' and 'Breakfast prep' overlap!"
            "  Morning walk: 08:00 - 08:30"
            "  Breakfast prep: 08:15 - 08:25"
        """
        warnings = []
        conflicts = self.find_conflicts_in_schedule()
        
        if not conflicts:
            return ["No conflicts detected. Schedule is valid!"]
        
        for task1, task2, time1, time2 in conflicts:
            # Find which pets these tasks belong to
            pet1_name = self._get_task_pet_name(task1)
            pet2_name = self._get_task_pet_name(task2)
            
            # Format times as HH:MM
            start1 = self._minutes_to_hhmm(time1)
            start2 = self._minutes_to_hhmm(time2)
            end1 = self._minutes_to_hhmm(time1 + task1.duration_minutes)
            end2 = self._minutes_to_hhmm(time2 + task2.duration_minutes)
            
            # Generate warning message
            if pet1_name == pet2_name:
                warning = f"WARNING: {pet1_name}'s tasks '{task1.title}' and '{task2.title}' overlap!\n"
            else:
                warning = f"WARNING: Cross-pet conflict! '{task1.title}' ({pet1_name}) overlaps with '{task2.title}' ({pet2_name})!\n"
            
            warning += f"  {task1.title}: {start1} - {end1}\n"
            warning += f"  {task2.title}: {start2} - {end2}"
            
            warnings.append(warning)
        
        return warnings
    
    def _get_task_pet_name(self, task: Task) -> str:
        """Helper: Find which pet owns a task."""
        for pet in self.owner.get_all_pets():
            if task in pet.get_all_tasks():
                return pet.name
        return "Unknown"
    
    def _minutes_to_hhmm(self, minutes: int) -> str:
        """Helper: Convert minutes since midnight to HH:MM format."""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"
    
    # ============ ALGORITHMIC METHODS - TIME ANALYSIS ============
    
    def get_time_by_pet(self) -> Dict[str, int]:
        """Return dictionary of time allocated to each pet.
        
        Algorithm: O(n * p) where n = scheduled tasks, p = number of pets.
        Aggregates task durations grouped by pet ownership.
        
        Returns:
            Dict mapping pet names to minutes allocated. Example:
            {"Mochi": 60, "Whiskers": 30} means 60 minutes for Mochi, 30 for Whiskers.
        """
        time_map: Dict[str, int] = {}
        
        for task, _ in self.scheduled_tasks:
            # Find which pet owns this task
            for pet in self.owner.get_all_pets():
                if task in pet.get_all_tasks():
                    time_map[pet.name] = time_map.get(pet.name, 0) + task.duration_minutes
                    break
        
        return time_map
    
    def get_time_by_priority(self) -> Dict[str, int]:
        """Return time allocated to each priority level.
        
        Algorithm: O(n) linear scan of scheduled tasks.
        Aggregates task durations grouped by priority level (HIGH, MEDIUM, LOW).
        
        Returns:
            Dict mapping priority names to minutes allocated. Example:
            {"HIGH": 90, "MEDIUM": 30} means 90 minutes high-priority, 30 medium.
        """
        time_map: Dict[str, int] = {}
        
        for task, _ in self.scheduled_tasks:
            priority_name = task.priority.name
            time_map[priority_name] = time_map.get(priority_name, 0) + task.duration_minutes
        
        return time_map
    
    def get_utilization_percentage(self) -> float:
        """Return percentage of available time that's scheduled (0.0 to 100.0).
        
        Algorithm: O(1) simple division.
        Shows how much of the owner's available time is actually used.
        
        Returns:
            Float from 0.0 (nothing scheduled) to 100.0 (fully booked).
            Example: 75.0 means 75% of available time is scheduled.
        """
        if self.owner.get_available_time() == 0:
            return 0.0
        return (self.total_time_used / self.owner.get_available_time()) * 100
    
    def get_free_time_remaining(self) -> int:
        """Return minutes of unscheduled time remaining.
        
        Algorithm: O(1) simple subtraction.
        
        Returns:
            Integer number of minutes available for additional tasks.
            Example: 120 means 2 hours (120 minutes) still available.
        """
        return self.owner.get_available_time() - self.total_time_used
    
    def get_free_time_percentage(self) -> float:
        """Return percentage of available time that's still free (0.0 to 100.0).
        
        Algorithm: O(1) derived from get_utilization_percentage().
        Complement of utilization: 100% - utilization%.
        
        Returns:
            Float from 0.0 (fully booked) to 100.0 (completely free).
        """
        return 100.0 - self.get_utilization_percentage()
    
    def get_time_breakdown_summary(self) -> str:
        """Return human-readable summary of time allocation."""
        summary = f"Time Breakdown for {self.owner.name}:\n"
        summary += f"=" * 50 + "\n"
        
        # By pet
        time_by_pet = self.get_time_by_pet()
        if time_by_pet:
            summary += "\nTime per Pet:\n"
            for pet_name, minutes in sorted(time_by_pet.items(), key=lambda x: -x[1]):
                hours = minutes // 60
                mins = minutes % 60
                percentage = (minutes / self.owner.get_available_time()) * 100
                summary += f"  {pet_name}: {hours}h {mins}m ({percentage:.1f}%)\n"
        
        # By priority
        time_by_priority = self.get_time_by_priority()
        if time_by_priority:
            summary += "\nTime per Priority:\n"
            for priority, minutes in sorted(time_by_priority.items(), 
                                          key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}.get(x[0], 3)):
                hours = minutes // 60
                mins = minutes % 60
                percentage = (minutes / self.owner.get_available_time()) * 100
                summary += f"  {priority}: {hours}h {mins}m ({percentage:.1f}%)\n"
        
        # Summary
        summary += f"\nTotal: {self.total_time_used}/{self.owner.get_available_time()} minutes\n"
        summary += f"Utilization: {self.get_utilization_percentage():.1f}%\n"
        summary += f"Free time: {self.get_free_time_remaining()} minutes ({self.get_free_time_percentage():.1f}%)\n"
        
        return summary
    
    def __str__(self) -> str:
        """Return string representation of schedule."""
        return f"Schedule for {self.owner.name}: {len(self.scheduled_tasks)} tasks scheduled"


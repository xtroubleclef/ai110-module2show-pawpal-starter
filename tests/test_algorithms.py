"""
Phase 4: Algorithmic Layer Tests
Tests for sorting, filtering, recurring tasks, conflict detection, and time analysis.
"""

import pytest
from pawpal_system import Owner, Pet, Task, Schedule, Priority


class TestSorting:
    """Tests for task sorting algorithms."""
    
    def test_sort_by_priority(self):
        """Test sorting tasks by priority (HIGH first)."""
        owner = Owner("Owner", availability_minutes=480)
        pet = Pet("Pet", "dog")
        
        low = Task("Low priority", 10, Priority.LOW)
        high = Task("High priority", 10, Priority.HIGH)
        medium = Task("Medium priority", 10, Priority.MEDIUM)
        
        pet.add_task(low)
        pet.add_task(high)
        pet.add_task(medium)
        owner.add_pet(pet)
        
        sorted_tasks = owner.get_sorted_tasks("priority")
        
        assert sorted_tasks[0].priority == Priority.HIGH
        assert sorted_tasks[1].priority == Priority.MEDIUM
        assert sorted_tasks[2].priority == Priority.LOW
    
    def test_sort_by_duration(self):
        """Test sorting tasks by duration (short first)."""
        owner = Owner("Owner", availability_minutes=480)
        pet = Pet("Pet", "dog")
        
        long_task = Task("Long", 60, Priority.LOW)
        short_task = Task("Short", 5, Priority.LOW)
        medium_task = Task("Medium", 30, Priority.LOW)
        
        pet.add_task(long_task)
        pet.add_task(short_task)
        pet.add_task(medium_task)
        owner.add_pet(pet)
        
        sorted_tasks = owner.get_sorted_tasks("duration")
        
        assert sorted_tasks[0].duration_minutes == 5
        assert sorted_tasks[1].duration_minutes == 30
        assert sorted_tasks[2].duration_minutes == 60
    
    def test_sort_by_frequency(self):
        """Test sorting tasks by frequency (daily first)."""
        owner = Owner("Owner", availability_minutes=480)
        pet = Pet("Pet", "dog")
        
        daily = Task("Daily walk", 20, Priority.HIGH, frequency="daily")
        weekly = Task("Weekly bath", 30, Priority.MEDIUM, frequency="weekly")
        asneeded = Task("As needed", 10, Priority.LOW, frequency="as-needed")
        
        pet.add_task(weekly)
        pet.add_task(asneeded)
        pet.add_task(daily)
        owner.add_pet(pet)
        
        sorted_tasks = owner.get_sorted_tasks("frequency")
        
        assert sorted_tasks[0].frequency == "daily"
        assert sorted_tasks[1].frequency == "weekly"
        assert sorted_tasks[2].frequency == "as-needed"


class TestFiltering:
    """Tests for task filtering algorithms."""
    
    def test_filter_by_pet(self):
        """Test filtering tasks for a specific pet."""
        owner = Owner("Owner", availability_minutes=480)
        
        dog = Pet("Max", "dog")
        dog.add_task(Task("Walk", 30, Priority.HIGH))
        dog.add_task(Task("Feed", 10, Priority.HIGH))
        
        cat = Pet("Whiskers", "cat")
        cat.add_task(Task("Feed", 10, Priority.HIGH))
        cat.add_task(Task("Litter", 15, Priority.HIGH))
        
        owner.add_pet(dog)
        owner.add_pet(cat)
        
        dog_tasks = owner.get_tasks_for_pet("Max")
        
        assert len(dog_tasks) == 2
        assert all(t in dog.get_all_tasks() for t in dog_tasks)
    
    def test_filter_incomplete_tasks(self):
        """Test filtering incomplete tasks."""
        owner = Owner("Owner", availability_minutes=480)
        pet = Pet("Pet", "dog")
        
        task1 = Task("Task 1", 10, Priority.HIGH)
        task2 = Task("Task 2", 10, Priority.HIGH)
        task3 = Task("Task 3", 10, Priority.HIGH)
        
        task1.mark_completed()
        
        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        owner.add_pet(pet)
        
        incomplete = owner.get_incomplete_tasks()
        
        assert len(incomplete) == 2
        assert task1 not in incomplete
        assert task2 in incomplete
        assert task3 in incomplete
    
    def test_filter_completed_tasks(self):
        """Test filtering completed tasks."""
        owner = Owner("Owner", availability_minutes=480)
        pet = Pet("Pet", "dog")
        
        task1 = Task("Task 1", 10, Priority.HIGH)
        task2 = Task("Task 2", 10, Priority.HIGH)
        
        task1.mark_completed()
        
        pet.add_task(task1)
        pet.add_task(task2)
        owner.add_pet(pet)
        
        completed = owner.get_completed_tasks()
        
        assert len(completed) == 1
        assert task1 in completed
    
    def test_filter_high_priority_tasks(self):
        """Test filtering high priority tasks."""
        owner = Owner("Owner", availability_minutes=480)
        pet = Pet("Pet", "dog")
        
        pet.add_task(Task("High 1", 10, Priority.HIGH))
        pet.add_task(Task("Medium", 10, Priority.MEDIUM))
        pet.add_task(Task("High 2", 10, Priority.HIGH))
        pet.add_task(Task("Low", 10, Priority.LOW))
        
        owner.add_pet(pet)
        
        high_priority = owner.get_high_priority_tasks()
        
        assert len(high_priority) == 2
        assert all(t.priority == Priority.HIGH for t in high_priority)
    
    def test_filter_urgent_incomplete(self):
        """Test filtering urgent incomplete tasks."""
        owner = Owner("Owner", availability_minutes=480)
        pet = Pet("Pet", "dog")
        
        urgent = Task("Urgent", 10, Priority.HIGH)
        urgent_completed = Task("Urgent Done", 10, Priority.HIGH)
        not_urgent = Task("Not urgent", 10, Priority.MEDIUM)
        
        urgent_completed.mark_completed()
        
        pet.add_task(urgent)
        pet.add_task(urgent_completed)
        pet.add_task(not_urgent)
        owner.add_pet(pet)
        
        result = owner.get_urgent_incomplete_tasks()
        
        assert len(result) == 1
        assert result[0] == urgent
    
    def test_filter_urgent_incomplete_for_pet(self):
        """Test filtering urgent incomplete for specific pet."""
        owner = Owner("Owner", availability_minutes=480)
        
        dog = Pet("Max", "dog")
        dog_urgent = Task("Dog urgent", 10, Priority.HIGH)
        dog.add_task(dog_urgent)
        
        cat = Pet("Whiskers", "cat")
        cat_urgent = Task("Cat urgent", 10, Priority.HIGH)
        cat.add_task(cat_urgent)
        
        owner.add_pet(dog)
        owner.add_pet(cat)
        
        result = owner.get_urgent_incomplete_tasks_for_pet("Max")
        
        assert len(result) == 1
        assert result[0] == dog_urgent
    
    def test_filter_recurring_tasks(self):
        """Test filtering recurring tasks."""
        owner = Owner("Owner", availability_minutes=480)
        pet = Pet("Pet", "dog")
        
        daily = Task("Daily", 10, Priority.HIGH, frequency="daily")
        weekly = Task("Weekly", 10, Priority.HIGH, frequency="weekly")
        asneeded = Task("As needed", 10, Priority.HIGH, frequency="as-needed")
        
        pet.add_task(daily)
        pet.add_task(weekly)
        pet.add_task(asneeded)
        owner.add_pet(pet)
        
        recurring = owner.get_recurring_tasks()
        
        assert len(recurring) == 2
        assert daily in recurring
        assert weekly in recurring
        assert asneeded not in recurring
    
    def test_task_completion_rate(self):
        """Test calculating task completion rate."""
        owner = Owner("Owner", availability_minutes=480)
        pet = Pet("Pet", "dog")
        
        task1 = Task("Task 1", 10, Priority.HIGH)
        task2 = Task("Task 2", 10, Priority.HIGH)
        task3 = Task("Task 3", 10, Priority.HIGH)
        task4 = Task("Task 4", 10, Priority.HIGH)
        
        task1.mark_completed()
        task2.mark_completed()
        
        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        pet.add_task(task4)
        owner.add_pet(pet)
        
        rate = owner.get_task_completion_rate()
        
        assert rate == 0.5  # 2 of 4 completed


class TestRecurringTasks:
    """Tests for recurring task expansion."""
    
    def test_expand_daily_task(self):
        """Test expanding a daily task across multiple days."""
        owner = Owner("Owner", availability_minutes=480)
        pet = Pet("Pet", "dog")
        
        daily_walk = Task("Walk", 20, Priority.HIGH, frequency="daily")
        pet.add_task(daily_walk)
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        expanded = schedule.expand_recurring_tasks(num_days=7)
        
        # Daily task should appear 7 times
        daily_copies = [t for t in expanded if "Walk" in t.title]
        assert len(daily_copies) == 7
    
    def test_expand_weekly_task(self):
        """Test expanding a weekly task (appears once)."""
        owner = Owner("Owner", availability_minutes=480)
        pet = Pet("Pet", "dog")
        
        weekly_bath = Task("Bath", 30, Priority.MEDIUM, frequency="weekly")
        pet.add_task(weekly_bath)
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        expanded = schedule.expand_recurring_tasks(num_days=7)
        
        # Weekly task should appear once
        bath_copies = [t for t in expanded if "Bath" in t.title]
        assert len(bath_copies) == 1
    
    def test_expand_asneeded_task(self):
        """Test as-needed task (appears once)."""
        owner = Owner("Owner", availability_minutes=480)
        pet = Pet("Pet", "dog")
        
        groom = Task("Grooming", 45, Priority.LOW, frequency="as-needed")
        pet.add_task(groom)
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        expanded = schedule.expand_recurring_tasks(num_days=7)
        
        # As-needed task should appear once
        groom_copies = [t for t in expanded if "Grooming" in t.title]
        assert len(groom_copies) == 1


class TestConflictDetection:
    """Tests for conflict detection and validation."""
    
    def test_find_no_conflicts_in_clean_schedule(self):
        """Test that a properly scheduled schedule has no conflicts."""
        owner = Owner("Owner", availability_minutes=480)
        pet = Pet("Pet", "dog")
        
        pet.add_task(Task("Task 1", 20, Priority.HIGH))
        pet.add_task(Task("Task 2", 20, Priority.HIGH))
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        schedule.build_schedule()
        
        conflicts = schedule.find_conflicts_in_schedule()
        
        assert len(conflicts) == 0
    
    def test_find_conflicts_in_overlapping_schedule(self):
        """Test detecting conflicts in manually created overlapping schedule."""
        owner = Owner("Owner", availability_minutes=480)
        pet = Pet("Pet", "dog")
        
        task1 = Task("Task 1", 30, Priority.HIGH)
        task2 = Task("Task 2", 30, Priority.HIGH)
        pet.add_task(task1)
        pet.add_task(task2)
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        # Manually create overlapping schedule
        schedule.scheduled_tasks = [
            (task1, 0),    # 0-30
            (task2, 15),   # 15-45 (overlaps with task1)
        ]
        
        conflicts = schedule.find_conflicts_in_schedule()
        
        assert len(conflicts) == 1
        assert conflicts[0][0] == task1
        assert conflicts[0][1] == task2
    
    def test_validate_schedule_success(self):
        """Test validating a good schedule."""
        owner = Owner("Owner", availability_minutes=480)
        pet = Pet("Pet", "dog")
        
        pet.add_task(Task("Task 1", 20, Priority.HIGH))
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        schedule.build_schedule()
        
        is_valid, message = schedule.validate_schedule()
        
        assert is_valid is True
        assert "valid" in message.lower()


class TestTimeAnalysis:
    """Tests for time breakdown and utilization calculations."""
    
    def test_get_time_by_pet(self):
        """Test calculating time allocated to each pet."""
        owner = Owner("Owner", availability_minutes=480)
        
        dog = Pet("Max", "dog")
        dog.add_task(Task("Walk", 30, Priority.HIGH))
        dog.add_task(Task("Dog Feed", 10, Priority.HIGH))
        
        cat = Pet("Whiskers", "cat")
        cat.add_task(Task("Cat Feed", 10, Priority.HIGH))
        
        owner.add_pet(dog)
        owner.add_pet(cat)
        
        schedule = Schedule(owner)
        schedule.build_schedule()
        
        time_by_pet = schedule.get_time_by_pet()
        
        assert time_by_pet["Max"] == 40  # 30 + 10
        assert time_by_pet["Whiskers"] == 10
    
    def test_get_time_by_priority(self):
        """Test calculating time by priority level."""
        owner = Owner("Owner", availability_minutes=480)
        pet = Pet("Pet", "dog")
        
        pet.add_task(Task("High 1", 20, Priority.HIGH))
        pet.add_task(Task("High 2", 10, Priority.HIGH))
        pet.add_task(Task("Medium", 15, Priority.MEDIUM))
        
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        schedule.build_schedule()
        
        time_by_priority = schedule.get_time_by_priority()
        
        assert time_by_priority["HIGH"] == 30
        assert time_by_priority["MEDIUM"] == 15
    
    def test_utilization_percentage(self):
        """Test calculating utilization percentage."""
        owner = Owner("Owner", availability_minutes=100)
        pet = Pet("Pet", "dog")
        
        pet.add_task(Task("Task", 25, Priority.HIGH))
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        schedule.build_schedule()
        
        utilization = schedule.get_utilization_percentage()
        
        assert utilization == 25.0  # 25/100 * 100
    
    def test_free_time_remaining(self):
        """Test calculating free time remaining."""
        owner = Owner("Owner", availability_minutes=100)
        pet = Pet("Pet", "dog")
        
        pet.add_task(Task("Task", 30, Priority.HIGH))
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        schedule.build_schedule()
        
        free = schedule.get_free_time_remaining()
        
        assert free == 70  # 100 - 30
    
    def test_free_time_percentage(self):
        """Test calculating free time percentage."""
        owner = Owner("Owner", availability_minutes=100)
        pet = Pet("Pet", "dog")
        
        pet.add_task(Task("Task", 25, Priority.HIGH))
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        schedule.build_schedule()
        
        free_pct = schedule.get_free_time_percentage()
        
        assert free_pct == 75.0  # 100% - 25%
    
    def test_time_breakdown_summary(self):
        """Test generating time breakdown summary."""
        owner = Owner("Owner", availability_minutes=480)
        
        dog = Pet("Max", "dog")
        dog.add_task(Task("Walk", 30, Priority.HIGH))
        dog.add_task(Task("Feed", 10, Priority.HIGH))
        
        owner.add_pet(dog)
        
        schedule = Schedule(owner)
        schedule.build_schedule()
        
        summary = schedule.get_time_breakdown_summary()
        
        assert "Max" in summary
        assert "40m" in summary or "40" in summary
        assert "Utilization" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

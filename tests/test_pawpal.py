"""
Test suite for PawPal+ system classes.
Tests Task, Pet, Owner, and Schedule functionality.
"""

import pytest
from pawpal_system import Task, Pet, Owner, Schedule, Priority


class TestTask:
    """Tests for the Task class."""
    
    def test_task_creation(self):
        """Test that a task can be created with required attributes."""
        task = Task(
            title="Morning walk",
            duration_minutes=30,
            priority=Priority.HIGH
        )
        assert task.title == "Morning walk"
        assert task.duration_minutes == 30
        assert task.priority == Priority.HIGH
        assert task.completed is False
    
    def test_mark_completed(self):
        """Test that mark_completed() changes task completion status."""
        task = Task(
            title="Feeding",
            duration_minutes=10,
            priority=Priority.HIGH
        )
        # Initially, task should not be completed
        assert task.completed is False
        
        # Mark as completed
        task.mark_completed()
        
        # Verify task is now marked as completed
        assert task.completed is True
    
    def test_is_urgent(self):
        """Test that is_urgent() correctly identifies high priority tasks."""
        high_priority = Task(
            title="Emergency vet visit",
            duration_minutes=60,
            priority=Priority.HIGH
        )
        medium_priority = Task(
            title="Regular checkup",
            duration_minutes=30,
            priority=Priority.MEDIUM
        )
        
        assert high_priority.is_urgent() is True
        assert medium_priority.is_urgent() is False
    
    def test_get_priority_level(self):
        """Test that get_priority_level() returns correct numeric values."""
        low = Task("task", 10, Priority.LOW)
        medium = Task("task", 10, Priority.MEDIUM)
        high = Task("task", 10, Priority.HIGH)
        
        assert low.get_priority_level() == 1
        assert medium.get_priority_level() == 2
        assert high.get_priority_level() == 3


class TestPet:
    """Tests for the Pet class."""
    
    def test_pet_creation(self):
        """Test that a pet can be created with required attributes."""
        pet = Pet(
            name="Mochi",
            species="dog",
            age=3
        )
        assert pet.name == "Mochi"
        assert pet.species == "dog"
        assert pet.age == 3
        assert len(pet.tasks) == 0
    
    def test_add_task_to_pet(self):
        """Test that adding a task to a Pet increases task count."""
        pet = Pet(name="Whiskers", species="cat")
        
        # Initially, pet should have no tasks
        assert len(pet.get_all_tasks()) == 0
        
        # Create and add a task
        task = Task(
            title="Feeding",
            duration_minutes=10,
            priority=Priority.HIGH
        )
        pet.add_task(task)
        
        # Verify task count increased
        assert len(pet.get_all_tasks()) == 1
        assert pet.get_all_tasks()[0] == task
    
    def test_add_multiple_tasks(self):
        """Test that multiple tasks can be added to a pet."""
        pet = Pet(name="Buddy", species="dog")
        
        task1 = Task("Walk", 30, Priority.HIGH)
        task2 = Task("Feeding", 10, Priority.HIGH)
        task3 = Task("Play", 20, Priority.MEDIUM)
        
        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        
        assert len(pet.get_all_tasks()) == 3
    
    def test_get_urgent_tasks(self):
        """Test that get_urgent_tasks() returns only high priority tasks."""
        pet = Pet(name="Rex", species="dog")
        
        high1 = Task("Walk", 30, Priority.HIGH)
        high2 = Task("Feed", 10, Priority.HIGH)
        medium = Task("Play", 20, Priority.MEDIUM)
        low = Task("Groom", 30, Priority.LOW)
        
        pet.add_task(high1)
        pet.add_task(medium)
        pet.add_task(high2)
        pet.add_task(low)
        
        urgent = pet.get_urgent_tasks()
        assert len(urgent) == 2
        assert high1 in urgent
        assert high2 in urgent
        assert medium not in urgent
        assert low not in urgent
    
    def test_get_care_requirements(self):
        """Test that care requirements are based on species."""
        dog = Pet(name="Fido", species="dog")
        cat = Pet(name="Fluffy", species="cat")
        
        dog_requirements = dog.get_care_requirements()
        cat_requirements = cat.get_care_requirements()
        
        assert "walk" in dog_requirements
        assert "litter box" in cat_requirements
        assert "litter box" not in dog_requirements


class TestOwner:
    """Tests for the Owner class."""
    
    def test_owner_creation(self):
        """Test that an owner can be created with required attributes."""
        owner = Owner(
            name="Jordan",
            availability_minutes=480
        )
        assert owner.name == "Jordan"
        assert owner.get_available_time() == 480
        assert len(owner.get_all_pets()) == 0
    
    def test_add_pet_to_owner(self):
        """Test that pets can be added to an owner."""
        owner = Owner(name="Sarah", availability_minutes=420)
        pet = Pet(name="Charlie", species="dog")
        
        # Initially owner has no pets
        assert len(owner.get_all_pets()) == 0
        
        # Add a pet
        owner.add_pet(pet)
        
        # Verify pet was added
        assert len(owner.get_all_pets()) == 1
        assert owner.get_all_pets()[0] == pet
    
    def test_get_all_tasks_from_pets(self):
        """Test that owner can retrieve all tasks from all pets."""
        owner = Owner(name="Mike", availability_minutes=480)
        
        # Create pets with tasks
        dog = Pet(name="Max", species="dog")
        dog.add_task(Task("Walk", 30, Priority.HIGH))
        dog.add_task(Task("Feed", 10, Priority.HIGH))
        
        cat = Pet(name="Mittens", species="cat")
        cat.add_task(Task("Feed", 10, Priority.HIGH))
        cat.add_task(Task("Litter", 15, Priority.HIGH))
        cat.add_task(Task("Groom", 20, Priority.MEDIUM))
        
        owner.add_pet(dog)
        owner.add_pet(cat)
        
        # Get all tasks from owner
        all_tasks = owner.get_all_tasks()
        
        # Verify we got all 5 tasks
        assert len(all_tasks) == 5
    
    def test_get_pet_by_name(self):
        """Test that owner can retrieve a specific pet by name."""
        owner = Owner(name="Alex", availability_minutes=480)
        
        dog = Pet(name="Barkley", species="dog")
        cat = Pet(name="Whiskers", species="cat")
        
        owner.add_pet(dog)
        owner.add_pet(cat)
        
        # Retrieve pets by name
        found_dog = owner.get_pet_by_name("Barkley")
        found_cat = owner.get_pet_by_name("Whiskers")
        not_found = owner.get_pet_by_name("NonExistent")
        
        assert found_dog == dog
        assert found_cat == cat
        assert not_found is None


class TestSchedule:
    """Tests for the Schedule class."""
    
    def test_schedule_creation(self):
        """Test that a schedule can be created."""
        owner = Owner(name="Test Owner", availability_minutes=480)
        schedule = Schedule(owner)
        
        assert schedule.owner == owner
        assert len(schedule.scheduled_tasks) == 0
    
    def test_build_schedule_with_tasks(self):
        """Test that build_schedule() schedules tasks."""
        owner = Owner(name="Owner", availability_minutes=480)
        
        dog = Pet(name="Dog", species="dog")
        dog.add_task(Task("Walk", 30, Priority.HIGH))
        dog.add_task(Task("Feed", 10, Priority.HIGH))
        
        owner.add_pet(dog)
        
        schedule = Schedule(owner)
        scheduled = schedule.build_schedule()
        
        # Verify schedule was built
        assert len(scheduled) == 2
        assert schedule.total_time_used == 40
    
    def test_schedule_respects_priority(self):
        """Test that schedule prioritizes high priority tasks."""
        owner = Owner(name="Owner", availability_minutes=480)
        
        pet = Pet(name="Pet", species="dog")
        pet.add_task(Task("Low priority", 10, Priority.LOW))
        pet.add_task(Task("High priority", 20, Priority.HIGH))
        pet.add_task(Task("Medium priority", 15, Priority.MEDIUM))
        
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        scheduled = schedule.build_schedule()
        
        # First task should be HIGH priority
        first_task = scheduled[0][0]
        assert first_task.priority == Priority.HIGH
    
    def test_is_feasible(self):
        """Test feasibility check for schedule."""
        owner = Owner(name="Owner", availability_minutes=100)
        
        pet = Pet(name="Pet", species="dog")
        pet.add_task(Task("Walk", 30, Priority.HIGH))
        pet.add_task(Task("Feed", 10, Priority.HIGH))
        pet.add_task(Task("Play", 20, Priority.HIGH))
        
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        
        # All urgent tasks (60 min) fit in available time (100 min)
        assert schedule.is_feasible() is True
    
    def test_is_not_feasible(self):
        """Test feasibility check when urgent tasks don't fit."""
        owner = Owner(name="Owner", availability_minutes=50)
        
        pet = Pet(name="Pet", species="dog")
        pet.add_task(Task("Walk", 30, Priority.HIGH))
        pet.add_task(Task("Feed", 10, Priority.HIGH))
        pet.add_task(Task("Groom", 20, Priority.HIGH))
        
        owner.add_pet(pet)
        
        schedule = Schedule(owner)
        
        # Urgent tasks (60 min) don't fit in available time (50 min)
        assert schedule.is_feasible() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

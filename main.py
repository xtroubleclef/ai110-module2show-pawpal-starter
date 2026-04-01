"""
PawPal+ Demo Script - Phase 4.5: Recurring Tasks & Conflict Detection
Testing the logic layer with automated recurring tasks and conflict detection
"""

from pawpal_system import Owner, Pet, Task, Schedule, Priority
from datetime import datetime, timedelta


def demo_recurring_tasks():
    """Demonstrate automatic recurring task creation."""
    print("=" * 70)
    print("DEMO 1: AUTOMATED RECURRING TASKS")
    print("=" * 70)
    print()
    
    # Create owner and pet
    owner = Owner(name="Jordan", availability_minutes=480)
    dog = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(dog)
    
    # Create daily task
    daily_walk = Task(
        title="Morning walk",
        duration_minutes=30,
        priority=Priority.HIGH,
        frequency="daily"
    )
    dog.add_task(daily_walk)
    
    print(f"Created task: {daily_walk}")
    print(f"Due date: {daily_walk.due_date.strftime('%Y-%m-%d')}")
    print(f"Frequency: {daily_walk.frequency}")
    print()
    
    # Mark task as completed - should auto-create next occurrence
    print("Marking task as complete...")
    next_task = dog.mark_task_complete(daily_walk)
    
    if next_task:
        print(f"✓ Next occurrence auto-created!")
        print(f"Original: {daily_walk.title} - due {daily_walk.due_date.strftime('%Y-%m-%d')} (COMPLETED)")
        print(f"Next:     {next_task.title} - due {next_task.due_date.strftime('%Y-%m-%d')} (TODO)")
        print()
        
        # Verify both tasks are in the pet's task list
        all_tasks = dog.get_all_tasks()
        print(f"Total tasks on {dog.name}: {len(all_tasks)}")
        for task in all_tasks:
            print(f"  - {task}")
    else:
        print("✗ Failed to create next occurrence")
    
    print()


def demo_conflict_detection():
    """Demonstrate conflict detection with warning messages."""
    print("=" * 70)
    print("DEMO 2: CONFLICT DETECTION WITH WARNINGS")
    print("=" * 70)
    print()
    
    # Create owner with one pet
    owner = Owner(name="Alex", availability_minutes=480)
    dog = Pet(name="Max", species="dog")
    owner.add_pet(dog)
    
    # Create overlapping tasks (same time)
    morning_walk = Task(
        title="Morning walk",
        duration_minutes=30,
        priority=Priority.HIGH
    )
    breakfast = Task(
        title="Breakfast prep",
        duration_minutes=15,
        priority=Priority.HIGH
    )
    
    dog.add_task(morning_walk)
    dog.add_task(breakfast)
    
    # Create schedule with manual overlap
    schedule = Schedule(owner)
    schedule.scheduled_tasks = [
        (morning_walk, 0),      # 00:00 - 00:30
        (breakfast, 15),        # 00:15 - 00:30 (OVERLAPS!)
    ]
    
    print("Scheduled tasks (with conflict):")
    for task, time in schedule.scheduled_tasks:
        end_time = time + task.duration_minutes
        start_hhmm = f"{time // 60:02d}:{time % 60:02d}"
        end_hhmm = f"{end_time // 60:02d}:{end_time % 60:02d}"
        print(f"  {task.title}: {start_hhmm} - {end_hhmm}")
    print()
    
    # Get conflict warnings
    print("Checking for conflicts...")
    warnings = schedule.get_conflict_warnings()
    
    if len(warnings) == 1 and "valid" in warnings[0].lower():
        print("✓ No conflicts found")
    else:
        for warning in warnings:
            print(f"⚠️  {warning}")
    
    print()


def demo_conflict_detection_multiple_pets():
    """Demonstrate cross-pet conflict detection."""
    print("=" * 70)
    print("DEMO 3: CROSS-PET CONFLICT DETECTION")
    print("=" * 70)
    print()
    
    # Create owner with two pets
    owner = Owner(name="Casey", availability_minutes=480)
    
    dog = Pet(name="Rex", species="dog")
    dog_walk = Task("Dog walk", 30, Priority.HIGH)
    dog.add_task(dog_walk)
    owner.add_pet(dog)
    
    cat = Pet(name="Whiskers", species="cat")
    cat_feed = Task("Cat feeding", 20, Priority.HIGH)
    cat.add_task(cat_feed)
    owner.add_pet(cat)
    
    # Create schedule with cross-pet conflict
    schedule = Schedule(owner)
    schedule.scheduled_tasks = [
        (dog_walk, 60),    # 01:00 - 01:30
        (cat_feed, 70),    # 01:10 - 01:30 (OVERLAPS with dog walk!)
    ]
    
    print("Scheduled tasks (with cross-pet conflict):")
    for task, time in schedule.scheduled_tasks:
        end_time = time + task.duration_minutes
        start_hhmm = f"{time // 60:02d}:{time % 60:02d}"
        end_hhmm = f"{end_time // 60:02d}:{end_time % 60:02d}"
        print(f"  {task.title}: {start_hhmm} - {end_hhmm}")
    print()
    
    # Get conflict warnings
    print("Checking for conflicts...")
    warnings = schedule.get_conflict_warnings()
    
    for warning in warnings:
        if "valid" not in warning.lower():
            print(f"⚠️  {warning}")
        else:
            print(f"✓ {warning}")
    
    print()


def demo_no_conflicts():
    """Demonstrate a clean schedule with no conflicts."""
    print("=" * 70)
    print("DEMO 4: CLEAN SCHEDULE (NO CONFLICTS)")
    print("=" * 70)
    print()
    
    owner = Owner(name="Sam", availability_minutes=480)
    
    dog = Pet(name="Buddy", species="dog")
    dog_walk = Task("Dog walk", 30, Priority.HIGH)
    dog_feed = Task("Dog food", 10, Priority.HIGH)
    dog.add_task(dog_walk)
    dog.add_task(dog_feed)
    owner.add_pet(dog)
    
    cat = Pet(name="Mittens", species="cat")
    cat_feed = Task("Cat food", 10, Priority.HIGH)
    cat.add_task(cat_feed)
    owner.add_pet(cat)
    
    # Build a proper schedule
    schedule = Schedule(owner)
    schedule.build_schedule()
    
    print("Scheduled tasks (clean schedule):")
    for task, time in schedule.scheduled_tasks:
        end_time = time + task.duration_minutes
        start_hhmm = f"{time // 60:02d}:{time % 60:02d}"
        end_hhmm = f"{end_time // 60:02d}:{end_time % 60:02d}"
        print(f"  {task.title}: {start_hhmm} - {end_hhmm}")
    print()
    
    # Check for conflicts
    print("Checking for conflicts...")
    warnings = schedule.get_conflict_warnings()
    
    for warning in warnings:
        print(f"✓ {warning}")
    
    print()


if __name__ == "__main__":
    demo_recurring_tasks()
    demo_conflict_detection()
    demo_conflict_detection_multiple_pets()
    demo_no_conflicts()
    print("=" * 70)
    print("All demos complete!")
    print("=" * 70)

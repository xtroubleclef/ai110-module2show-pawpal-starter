"""
PawPal+ Demo Script
Testing the logic layer with sample Owner, Pets, Tasks, and Schedule
"""

from pawpal_system import Owner, Pet, Task, Schedule, Priority


def main():
    """Main demo function."""
    print("=" * 60)
    print("PawPal+ - Pet Care Planning System Demo")
    print("=" * 60)
    print()
    
    # Create an Owner
    print("Creating Owner...")
    owner = Owner(
        name="Jordan",
        contact_info="jordan@email.com",
        availability_minutes=480,  # 8 hours available per day
        preferences="Prefers morning walks"
    )
    print("Owner created: " + str(owner))
    print("Available time: " + str(owner.get_available_time()) + " minutes")
    print()
    
    # Create Pet 1: Dog (Mochi)
    print("Creating Pet 1: Dog...")
    dog = Pet(
        name="Mochi",
        species="dog",
        age=3,
        preferences="Loves fetch"
    )
    
    # Add tasks for the dog
    dog_task1 = Task(
        title="Morning walk",
        duration_minutes=30,
        priority=Priority.HIGH,
        description="Brisk walk around the park",
        frequency="daily"
    )
    dog_task2 = Task(
        title="Feeding",
        duration_minutes=10,
        priority=Priority.HIGH,
        description="Breakfast and water",
        frequency="daily"
    )
    dog_task3 = Task(
        title="Playtime with toys",
        duration_minutes=20,
        priority=Priority.MEDIUM,
        description="Interactive play session",
        frequency="daily"
    )
    
    dog.add_task(dog_task1)
    dog.add_task(dog_task2)
    dog.add_task(dog_task3)
    
    print("Pet created: " + str(dog))
    print("Tasks (" + str(len(dog.get_all_tasks())) + "): " + ", ".join([t.title for t in dog.get_all_tasks()]))
    print()
    
    # Create Pet 2: Cat (Whiskers)
    print("Creating Pet 2: Cat...")
    cat = Pet(
        name="Whiskers",
        species="cat",
        age=5,
        preferences="Indoor only"
    )
    
    # Add tasks for the cat
    cat_task1 = Task(
        title="Feeding",
        duration_minutes=10,
        priority=Priority.HIGH,
        description="Wet food and water",
        frequency="daily"
    )
    cat_task2 = Task(
        title="Litter box cleaning",
        duration_minutes=15,
        priority=Priority.HIGH,
        description="Clean and refill litter box",
        frequency="daily"
    )
    cat_task3 = Task(
        title="Grooming",
        duration_minutes=20,
        priority=Priority.MEDIUM,
        description="Brush coat and check nails",
        frequency="weekly"
    )
    
    cat.add_task(cat_task1)
    cat.add_task(cat_task2)
    cat.add_task(cat_task3)
    
    print("Pet created: " + str(cat))
    print("Tasks (" + str(len(cat.get_all_tasks())) + "): " + ", ".join([t.title for t in cat.get_all_tasks()]))
    print()
    
    # Add pets to owner
    owner.add_pet(dog)
    owner.add_pet(cat)
    print("Pets added to owner")
    print(owner.name + " now has " + str(len(owner.get_all_pets())) + " pet(s)")
    print()
    
    # Create and build schedule
    print("=" * 60)
    print("Building Schedule...")
    print("=" * 60)
    print()
    
    schedule = Schedule(owner)
    
    print("Schedule Analysis:")
    print("  Total tasks to schedule: " + str(len(schedule.tasks)))
    print("  Available time: " + str(owner.get_available_time()) + " minutes")
    print("  Is feasible (all urgent tasks fit): " + str(schedule.is_feasible()))
    print()
    
    # Build the schedule
    scheduled = schedule.build_schedule()
    print("Schedule built with " + str(len(scheduled)) + " tasks")
    print()
    
    # Display the detailed schedule explanation
    print("=" * 60)
    print("TODAY'S SCHEDULE")
    print("=" * 60)
    print()
    print(schedule.get_schedule_explanation())
    
    # Show any unscheduled tasks
    unscheduled = schedule.get_unscheduled_tasks()
    if unscheduled:
        print("Could not schedule the following tasks (insufficient time):")
        for task in unscheduled:
            print("  - " + task.title + " (" + str(task.duration_minutes) + " min, " + task.priority.name + " priority)")
        print()
    else:
        print("All tasks successfully scheduled!")
        print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("Owner: " + owner.name)
    print("Pets: " + ", ".join([p.name for p in owner.get_all_pets()]))
    print("Total tasks: " + str(len(schedule.tasks)))
    print("Scheduled tasks: " + str(len(schedule.scheduled_tasks)))
    print("Unscheduled tasks: " + str(len(unscheduled)))
    utilization = (schedule.total_time_used/owner.get_available_time()*100)
    print("Time utilization: " + str(schedule.total_time_used) + "/" + str(owner.get_available_time()) + " minutes (" + str(round(utilization, 1)) + "%)")
    print()
    print("Demo complete!")


if __name__ == "__main__":
    main()

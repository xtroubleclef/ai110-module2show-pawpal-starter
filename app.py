import streamlit as st
from pawpal_system import Owner, Pet, Task, Schedule, Priority
from datetime import datetime

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+ - Smart Pet Care Planning")

st.markdown(
    """
**PawPal+ intelligently organizes your pet care** using advanced scheduling algorithms:

- 🎯 **Smart Sorting**: Tasks automatically prioritized by importance, duration, and frequency
- ⚠️ **Conflict Detection**: Identifies overlapping tasks to prevent scheduling conflicts
- 📊 **Time Analysis**: Shows exactly how time is allocated across pets and priorities
- 🔄 **Recurring Tasks**: Automatically creates next instances for daily, weekly, and as-needed tasks
- ✅ **Feasibility Checking**: Ensures schedules fit within your available time
"""
)

# Initialize session state for owner and pets
if "owner" not in st.session_state:
    st.session_state.owner = None

if "tasks_list" not in st.session_state:
    st.session_state.tasks_list = []

# Create two columns for input
col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 Owner Information")
    owner_name = st.text_input("Owner name", value="Jordan", key="owner_name_input")
    owner_contact = st.text_input("Contact info (optional)", value="", key="owner_contact_input")
    availability = st.slider("Available time (hours per day)", 1, 12, 8, key="availability_slider")
    
    if st.button("✅ Create/Update Owner"):
        # Create or update owner in session state
        st.session_state.owner = Owner(
            name=owner_name,
            contact_info=owner_contact,
            availability_minutes=availability * 60
        )
        st.success(f"✓ Owner '{owner_name}' created! Available time: {availability} hours")

with col2:
    st.subheader("🐕 Add Pet")
    pet_name = st.text_input("Pet name", value="Mochi", key="pet_name_input")
    species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"], key="species_select")
    pet_age = st.number_input("Pet age (years)", min_value=0, max_value=30, value=3, key="pet_age_input")
    
    if st.button("✅ Add Pet"):
        if st.session_state.owner is None:
            st.error("❌ Please create an owner first!")
        else:
            new_pet = Pet(
                name=pet_name,
                species=species,
                age=pet_age
            )
            st.session_state.owner.add_pet(new_pet)
            st.success(f"✓ Pet '{pet_name}' added to {st.session_state.owner.name}'s collection!")



# Display current owner and pets
if st.session_state.owner:
    st.divider()
    st.subheader(f"📋 {st.session_state.owner.name}'s Pets")
    
    pets_data = []
    for pet in st.session_state.owner.get_all_pets():
        pets_data.append({
            "🐾 Name": pet.name,
            "🏠 Species": pet.species,
            "📅 Age": pet.age,
            "📝 Tasks": len(pet.get_all_tasks())
        })
    
    if pets_data:
        st.dataframe(pets_data, use_container_width=True)
    else:
        st.info("No pets added yet.")

st.divider()

# Task Management Section
if st.session_state.owner and st.session_state.owner.get_all_pets():
    st.subheader("➕ Add Tasks")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        task_pet = st.selectbox(
            "Pet",
            [pet.name for pet in st.session_state.owner.get_all_pets()],
            key="task_pet_select"
        )
    
    with col2:
        task_title = st.text_input("Task title", value="Walk", key="task_title_input")
    
    with col3:
        task_duration = st.number_input("Minutes", min_value=1, max_value=240, value=30, key="task_duration_input")
    
    with col4:
        task_priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=2, key="task_priority_select")
    
    with col5:
        task_frequency = st.selectbox("Frequency", ["daily", "weekly", "as-needed"], key="task_frequency_select")
    
    if st.button("✅ Add Task"):
        # Find the selected pet
        selected_pet = st.session_state.owner.get_pet_by_name(task_pet)
        
        if selected_pet:
            # Convert priority string to Priority enum
            priority_map = {"Low": Priority.LOW, "Medium": Priority.MEDIUM, "High": Priority.HIGH}
            
            new_task = Task(
                title=task_title,
                duration_minutes=task_duration,
                priority=priority_map[task_priority],
                frequency=task_frequency.lower()
            )
            selected_pet.add_task(new_task)
            st.success(f"✓ Task '{task_title}' ({task_frequency}) added to {task_pet}!")
    
    # Display all tasks with smart filtering
    st.subheader("📝 Current Tasks")
    all_tasks = st.session_state.owner.get_all_tasks()
    
    if all_tasks:
        # Create filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_pet = st.selectbox(
                "Filter by Pet",
                ["All Pets"] + [pet.name for pet in st.session_state.owner.get_all_pets()],
                key="filter_pet_select"
            )
        
        with col2:
            filter_priority = st.selectbox(
                "Filter by Priority",
                ["All Priorities", "High", "Medium", "Low"],
                key="filter_priority_select"
            )
        
        with col3:
            filter_status = st.selectbox(
                "Filter by Status",
                ["All", "Incomplete", "Completed"],
                key="filter_status_select"
            )
        
        # Apply filters
        filtered_tasks = all_tasks
        
        if filter_pet != "All Pets":
            filtered_tasks = st.session_state.owner.get_tasks_for_pet(filter_pet)
        
        if filter_priority != "All Priorities":
            priority_map = {"High": Priority.HIGH, "Medium": Priority.MEDIUM, "Low": Priority.LOW}
            filtered_tasks = [t for t in filtered_tasks if t.priority == priority_map[filter_priority]]
        
        if filter_status == "Incomplete":
            filtered_tasks = [t for t in filtered_tasks if not t.completed]
        elif filter_status == "Completed":
            filtered_tasks = [t for t in filtered_tasks if t.completed]
        
        # Display filtered tasks
        task_data = []
        for task in filtered_tasks:
            # Find which pet owns this task
            task_pet_name = None
            for pet in st.session_state.owner.get_all_pets():
                if task in pet.get_all_tasks():
                    task_pet_name = pet.name
                    break
            
            task_data.append({
                "🐾 Pet": task_pet_name,
                "📋 Task": task.title,
                "⏱️ Duration (min)": task.duration_minutes,
                "🎯 Priority": task.priority.name,
                "🔄 Frequency": task.frequency,
                "✅ Completed": "Yes" if task.completed else "No",
                "📅 Due": task.due_date.strftime("%Y-%m-%d") if task.due_date else "Today"
            })
        
        if task_data:
            st.dataframe(task_data, use_container_width=True)
        else:
            st.info("No tasks match the selected filters.")
    else:
        st.info("No tasks added yet. Add a task above.")
    
    st.divider()
    
    # Schedule Generation with Smart Algorithms
    st.subheader("🎯 Generate Smart Schedule")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("Build an optimized daily schedule using our smart algorithms:")
    
    with col2:
        if st.button("🚀 Build Schedule", use_container_width=True):
            if not all_tasks:
                st.warning("⚠️ Please add some tasks first!")
            else:
                # Create and build schedule
                schedule = Schedule(st.session_state.owner)
                
                # Check feasibility
                if not schedule.is_feasible():
                    st.warning("⚠️ Warning: Not all high-priority tasks fit in available time!")
                
                # Build the schedule
                scheduled = schedule.build_schedule()
                
                # Show success message
                st.success(f"✓ Optimal schedule generated with {len(scheduled)} tasks scheduled")
                
                # Display schedule in a nice format
                st.subheader("📅 Your Daily Schedule")
                
                if scheduled:
                    schedule_data = []
                    for task, start_time in sorted(scheduled, key=lambda x: x[1]):
                        hours = start_time // 60
                        minutes = start_time % 60
                        end_time = start_time + task.duration_minutes
                        end_hours = end_time // 60
                        end_minutes = end_time % 60
                        
                        # Find pet name
                        pet_name = None
                        for pet in st.session_state.owner.get_all_pets():
                            if task in pet.get_all_tasks():
                                pet_name = pet.name
                                break
                        
                        schedule_data.append({
                            "⏰ Time": f"{hours:02d}:{minutes:02d} - {end_hours:02d}:{end_minutes:02d}",
                            "🐾 Pet": pet_name,
                            "📋 Task": task.title,
                            "⏱️ Duration": f"{task.duration_minutes} min",
                            "🎯 Priority": task.priority.name
                        })
                    
                    st.dataframe(schedule_data, use_container_width=True)
                
                # Show conflict warnings (Phase 4.5 feature)
                st.subheader("⚠️ Conflict Analysis")
                warnings = schedule.get_conflict_warnings()
                
                if len(warnings) == 1 and "valid" in warnings[0].lower():
                    st.success("✓ " + warnings[0])
                else:
                    for warning in warnings:
                        if "valid" not in warning.lower():
                            st.warning(warning)
                        else:
                            st.success("✓ " + warning)
                
                # Time Analysis Section (Phase 4 feature)
                st.subheader("📊 Time Analysis")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    utilization = schedule.get_utilization_percentage()
                    st.metric("⏱️ Time Used", f"{schedule.total_time_used} min", 
                             f"{utilization:.1f}%")
                
                with col2:
                    free_time = schedule.get_free_time_remaining()
                    st.metric("😌 Free Time", f"{free_time} min")
                
                with col3:
                    st.metric("📈 Total Tasks", len(all_tasks))
                
                with col4:
                    unscheduled = schedule.get_unscheduled_tasks()
                    st.metric("⏭️ Unscheduled", len(unscheduled))
                
                # Breakdown by pet
                st.write("**Time per Pet:**")
                time_by_pet = schedule.get_time_by_pet()
                pet_data = []
                for pet_name, minutes in time_by_pet.items():
                    hours = minutes / 60
                    pet_data.append({
                        "🐾 Pet": pet_name,
                        "⏱️ Time (minutes)": minutes,
                        "⏱️ Time (hours)": f"{hours:.1f}"
                    })
                
                if pet_data:
                    st.dataframe(pet_data, use_container_width=True)
                
                # Breakdown by priority
                st.write("**Time per Priority:**")
                time_by_priority = schedule.get_time_by_priority()
                priority_data = []
                for priority_name, minutes in time_by_priority.items():
                    priority_data.append({
                        "🎯 Priority": priority_name,
                        "⏱️ Time (minutes)": minutes
                    })
                
                if priority_data:
                    st.dataframe(priority_data, use_container_width=True)
                
                # Show unscheduled tasks if any
                unscheduled = schedule.get_unscheduled_tasks()
                if unscheduled:
                    st.warning("⏭️ The following tasks could not be scheduled (insufficient time):")
                    unscheduled_data = []
                    for task in unscheduled:
                        unscheduled_data.append({
                            "📋 Task": task.title,
                            "⏱️ Duration": f"{task.duration_minutes} min",
                            "🎯 Priority": task.priority.name
                        })
                    st.dataframe(unscheduled_data, use_container_width=True)
                
                # Sorting and Filtering demonstration
                st.subheader("🔧 Smart Algorithm Features")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Tasks Sorted by Priority** (High → Medium → Low):")
                    sorted_by_priority = st.session_state.owner.get_sorted_tasks(sort_by="priority")
                    sorted_data = []
                    for task in sorted_by_priority:
                        sorted_data.append({
                            "📋 Task": task.title,
                            "🎯 Priority": task.priority.name,
                            "⏱️ Duration": f"{task.duration_minutes} min"
                        })
                    st.dataframe(sorted_data, use_container_width=True)
                
                with col2:
                    st.write("**Recurring Tasks** (Auto-repeat):")
                    recurring = st.session_state.owner.get_recurring_tasks()
                    recurring_data = []
                    for task in recurring:
                        recurring_data.append({
                            "📋 Task": task.title,
                            "🔄 Frequency": task.frequency,
                            "📅 Due": task.due_date.strftime("%Y-%m-%d") if task.due_date else "Today"
                        })
                    
                    if recurring_data:
                        st.dataframe(recurring_data, use_container_width=True)
                    else:
                        st.info("No recurring tasks yet.")

else:
    if st.session_state.owner:
        st.info("ℹ️ Add at least one pet and one task to generate a schedule.")
    else:
        st.info("ℹ️ Create an owner to get started!")


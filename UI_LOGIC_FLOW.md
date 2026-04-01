# How the UI Calls the Logic Layer

## Key Insight
**The UI (Streamlit) doesn't call methods directly. Instead, it creates objects and stores them in `st.session_state`, which keeps them in memory between page refreshes.**

---

## Example Flow: Adding a Pet

### What User Sees
```
User clicks on "Add Pet" tab
├─ Sees form with: Pet name, Species, Age
├─ Fills in: "Max", "dog", "3"
└─ Clicks button: "Add Pet"
```

### What Happens Behind the Scenes

**Step 1: Form Data Collection** (app.py lines 42-46)
```python
# User's input from Streamlit widgets
pet_name = st.text_input("Pet name", value="Mochi", key="pet_name_input")
species = st.selectbox("Species", ["dog", "cat", ...], key="species_select")
pet_age = st.number_input("Pet age (years)", min_value=0, max_value=30, value=3, key="pet_age_input")
```

**Step 2: Button Click Triggers Logic** (app.py lines 48-58)
```python
if st.button("Add Pet"):
    if st.session_state.owner is None:
        st.error("Please create an owner first!")
    else:
        # Create Pet object (calls Pet.__init__ from pawpal_system.py)
        new_pet = Pet(
            name=pet_name,                    # "Max"
            species=species,                  # "dog"
            age=pet_age                       # 3
        )
        
        # Call owner.add_pet() method (from pawpal_system.py)
        st.session_state.owner.add_pet(new_pet)  # ← KEY LINE
        
        # Show success message
        st.success(f"Pet '{pet_name}' added to {st.session_state.owner.name}'s collection!")
```

**Step 3: What Happens in `owner.add_pet()`** (pawpal_system.py lines 120-122)
```python
def add_pet(self, pet: Pet) -> None:
    """Add a pet to the owner's list."""
    self.pets.append(pet)  # ← Pet is added to owner's list
```

**Step 4: Data Persists** (Streamlit Magic)
```
┌─────────────────────────────────────────┐
│   st.session_state.owner = Owner(...)   │
│   ├─ name: "Jordan"                     │
│   ├─ availability_minutes: 480          │
│   └─ pets: [Pet(...)]  ← Max is stored! │
│       └─ Pet(name="Max", species="dog") │
│           └─ tasks: [] (empty for now)  │
└─────────────────────────────────────────┘

This entire object stays in memory!
Even if user refreshes the page, the pet is still there.
```

**Step 5: UI Displays the Result** (app.py lines 60-75)
```python
if st.session_state.owner:
    st.subheader(f"Current Owner: {st.session_state.owner.name}")
    
    pets_data = []
    for pet in st.session_state.owner.get_all_pets():  # ← Reads from Owner
        pets_data.append({
            "Name": pet.name,           # "Max"
            "Species": pet.species,     # "dog"
            "Age": pet.age,             # 3
            "Tasks": len(pet.get_all_tasks())  # 0
        })
    
    st.table(pets_data)  # Shows table with Max in it
```

---

## Example Flow: Adding a Task

### Similar Process
```
1. User selects pet → calls owner.get_pet_by_name()
2. User fills task form → collects inputs
3. User clicks "Add Task" → creates Task object
4. Calls selected_pet.add_task(new_task)
5. Task is stored in pet.tasks
6. Data persists in session state
7. UI displays updated task list
```

---

## Example Flow: Generating Schedule

### Most Complex Flow
```
1. User clicks "Build Optimal Schedule"
2. UI creates Schedule(st.session_state.owner)
   └─ Schedule retrieves owner.get_all_tasks()
      └─ Gets all tasks from all pets
3. schedule.build_schedule() runs algorithm
   └─ Sorts by priority
   └─ Fits tasks into available time
   └─ Returns optimized schedule
4. UI displays results:
   └─ Schedule explanation
   └─ Time utilization metrics
   └─ Unscheduled tasks (if any)
```

---

## The Critical Connection Points

### 1. **Pet Creation**
```
UI Form Input
    ↓
Pet.__init__() is called
    ↓
new_pet object created
    ↓
owner.add_pet(new_pet) is called
    ↓
Pet stored in owner.pets list
    ↓
Stored in st.session_state.owner
    ↓
Data persists! ✓
```

### 2. **Task Addition**
```
UI selects pet → calls owner.get_pet_by_name()
    ↓
UI creates Task object → Task.__init__()
    ↓
UI calls selected_pet.add_task(task)
    ↓
Task stored in pet.tasks list
    ↓
Persists in st.session_state.owner.pets[index].tasks
    ↓
Data persists! ✓
```

### 3. **Schedule Generation**
```
UI creates Schedule(owner) → Schedule.__init__()
    ↓
Schedule calls owner.get_all_tasks()
    ↓
Iterates through all pets, gets all tasks
    ↓
schedule.build_schedule() runs algorithm
    ↓
Returns list of (task, start_time) tuples
    ↓
UI displays results
```

---

## Why This Matters

**Without session state:**
```
User adds pet → Page refreshes → Pet is gone! ✗
```

**With session state:**
```
User adds pet → Stored in st.session_state.owner → Page refreshes → Pet still there! ✓
```

**The UI code flow:**
```python
# Initialize memory vault
if "owner" not in st.session_state:
    st.session_state.owner = None

# User creates owner
if st.button("Create Owner"):
    st.session_state.owner = Owner(...)  # ← Store in vault

# User adds pet
if st.button("Add Pet"):
    st.session_state.owner.add_pet(Pet(...))  # ← Update vault

# When page refreshes, the vault still has the same owner and pets!
```

---

## Summary

| Action | Logic Method Called | Data Stored | Persists? |
|--------|-------------------|-------------|-----------|
| Create Owner | `Owner.__init__()` | `st.session_state.owner` | ✓ |
| Add Pet | `owner.add_pet(pet)` | `st.session_state.owner.pets` | ✓ |
| Add Task | `pet.add_task(task)` | `st.session_state.owner.pets[i].tasks` | ✓ |
| Get Pet | `owner.get_pet_by_name()` | N/A (retrieval only) | N/A |
| Get Tasks | `owner.get_all_tasks()` | N/A (retrieval only) | N/A |
| Build Schedule | `Schedule.build_schedule()` | Local variable (displayed once) | ✓* |

*Schedule is regenerated each time user clicks "Build Schedule" button

---

**Bottom Line**: The UI uses method calls to create objects and store them. `st.session_state` ensures they stay in memory. When users interact with the app, they're actually manipulating Python objects from `pawpal_system.py`!

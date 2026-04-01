# Phase 4: Algorithmic Layer - Planning Document

## Current State Analysis

### What Works Well
✓ Basic scheduling with priority sorting
✓ Greedy algorithm fills available time efficiently
✓ Conflict detection in `add_task_to_schedule()`
✓ Time calculations and explanations

### What Feels Manual/Simple
1. **Sorting** - Only sorts by priority once, no flexibility
2. **Filtering** - No way to filter tasks by pet, status, priority
3. **Recurring Tasks** - Tasks marked as "daily" but never actually recur
4. **Conflict Detection** - Only detects when manually adding; not proactive
5. **Task Status** - Tasks have `completed` field but no management
6. **Time Analysis** - No breakdown by pet or task category

---

## Proposed Algorithmic Improvements

### 1. Task Sorting (Multiple Criteria)
**Current**: Sorts by priority then duration once
**Proposed**: Methods to sort by:
- Priority (HIGH → LOW)
- Duration (short first vs long first)
- Completion status (incomplete first)
- Frequency (daily → weekly → as-needed)
- Pet (group by pet)

**Use Case**: User wants to see "urgent tasks first" or "all tasks for Mochi"

**Simple Algorithm**:
```python
def get_sorted_tasks(self, sort_by="priority"):
    if sort_by == "priority":
        return sorted(self.tasks, key=lambda t: -t.get_priority_level())
    elif sort_by == "duration":
        return sorted(self.tasks, key=lambda t: t.duration_minutes)
    # etc.
```

---

### 2. Task Filtering (By Pet, Status, Priority)
**Current**: No filtering
**Proposed**: Methods to filter:
- By pet name: `get_tasks_for_pet(pet_name)`
- By completion: `get_incomplete_tasks()`, `get_completed_tasks()`
- By priority: `get_high_priority_tasks()`, `get_medium_priority_tasks()`
- By frequency: `get_recurring_tasks()`
- Combined: `get_urgent_incomplete_tasks_for_pet(pet_name)`

**Use Case**: "Show me all incomplete high-priority tasks for Max"

**Simple Algorithm**:
```python
def get_tasks_for_pet(self, pet_name: str) -> List[Task]:
    pet = self.get_pet_by_name(pet_name)
    return pet.get_all_tasks() if pet else []

def get_incomplete_tasks(self) -> List[Task]:
    return [t for t in self.get_all_tasks() if not t.completed]
```

---

### 3. Recurring Task Logic
**Current**: Tasks have `frequency: str` field but nothing happens with it
**Proposed**: 
- `expand_recurring_tasks()` - Convert one "daily" task into 7 instances for a week
- `is_recurring()` - Check if task should repeat
- `mark_completed()` - Already exists, no change needed
- Track which day of recurrence

**Use Case**: "Walking the dog daily" should appear in every day's schedule

**Algorithm Approach**:
```python
# Instead of storing one "Morning walk" task:
# Store 7 copies (or 30 for monthly):
def expand_recurring_tasks(self, num_days: int = 7) -> List[Task]:
    expanded = []
    for task in self.tasks:
        if task.frequency == "daily":
            for day in range(num_days):
                # Create copy with day identifier
                expanded.append(copy_task_for_day(task, day))
        elif task.frequency == "weekly":
            expanded.append(task)  # Just add once per week
    return expanded
```

---

### 4. Conflict Detection (Proactive)
**Current**: Only detects when manually adding a task to schedule
**Proposed**:
- `find_conflicts_in_schedule()` - Scan entire schedule for overlaps
- `suggest_conflict_resolution()` - Recommend which task to reschedule
- `validate_schedule()` - Check if current schedule is valid

**Use Case**: "I notice two of your pet's tasks overlap. Which should I reschedule?"

**Algorithm**:
```python
def find_conflicts_in_schedule(self) -> List[Tuple[Task, Task]]:
    conflicts = []
    for i, (task1, time1) in enumerate(self.scheduled_tasks):
        end1 = time1 + task1.duration_minutes
        for task2, time2 in self.scheduled_tasks[i+1:]:
            end2 = time2 + task2.duration_minutes
            if not (end1 <= time2 or time1 >= end2):
                conflicts.append((task1, task2))
    return conflicts
```

---

### 5. Time Breakdown Analysis
**Current**: Just shows total time used
**Proposed**:
- `get_time_by_pet()` - How much time each pet gets
- `get_time_by_priority()` - How much time for high/medium/low
- `get_free_time_slots()` - Which time blocks are unscheduled
- `get_utilization_percentage()` - % of time that's scheduled

**Use Case**: "I spend 2.5 hours on Max and 1.5 hours on Whiskers"

**Algorithm**:
```python
def get_time_by_pet(self) -> Dict[str, int]:
    time_map = {}
    for task, _ in self.scheduled_tasks:
        # Find which pet this task belongs to
        for pet in self.owner.get_all_pets():
            if task in pet.get_all_tasks():
                time_map[pet.name] = time_map.get(pet.name, 0) + task.duration_minutes
    return time_map
```

---

### 6. Task Status Management
**Current**: Tasks have `completed` field and `mark_completed()` method
**Proposed**:
- Add timestamp when task was completed
- `mark_completed(timestamp)` - Record when task finished
- `get_completion_rate()` - What % of tasks are done
- `get_overdue_tasks()` - Tasks that should have been done by now

**Algorithm**:
```python
@dataclass
class Task:
    # ... existing fields ...
    completed: bool = False
    completed_at: Optional[datetime] = None
    
    def mark_completed(self, completed_at: Optional[datetime] = None) -> None:
        self.completed = True
        self.completed_at = completed_at or datetime.now()
    
    def is_overdue(self, current_time: datetime) -> bool:
        # If scheduled for 9am and it's 11am, it's overdue
        pass
```

---

## Implementation Plan

### Phase 4.1: Task Sorting & Filtering (15 mins)
- Add `sort_tasks_by(criteria)` method to Owner
- Add `filter_tasks_by_pet()`, `get_incomplete_tasks()`, etc.
- Test with new test cases

### Phase 4.2: Recurring Task Logic (15 mins)
- Add `expand_recurring_tasks()` to Schedule
- Modify `build_schedule()` to handle recurring tasks
- Test with weekly/daily task scenarios

### Phase 4.3: Advanced Conflict Detection (10 mins)
- Add `find_conflicts_in_schedule()` method
- Add `validate_schedule()` method
- Test conflict scenarios

### Phase 4.4: Documentation & Testing (5 mins)
- Write tests for all new methods
- Update reflection.md with algorithm decisions
- Commit with clear messages

---

## Tradeoff Decisions

### Sorting vs Filtering
**Option A**: Add lots of specific methods (get_high_priority, get_for_pet, etc.)
**Option B**: Add one flexible filter method with parameters

**Choice**: Option A (specific methods)
**Why**: Clearer, easier to understand, better for Streamlit UI components

### Recurring Task Expansion
**Option A**: Store one task and generate copies dynamically
**Option B**: Pre-generate all recurring instances at schedule time

**Choice**: Option B (pre-generate at schedule time)
**Why**: Simpler to implement, user can see what's actually scheduled

### Conflict Detection
**Option A**: Prevent conflicts by not scheduling conflicts
**Option B**: Detect and report conflicts, let user resolve

**Choice**: Option B (detect and report)
**Why**: More user control, can be overridden if needed

---

## Expected Test Coverage

- [ ] Sort tasks by priority (HIGH should come first)
- [ ] Sort tasks by duration (shorter should come first)
- [ ] Filter by pet name (only that pet's tasks)
- [ ] Filter incomplete tasks (only not-completed)
- [ ] Filter urgent tasks (only HIGH priority)
- [ ] Expand daily task to 7 instances
- [ ] Expand weekly task to 1 instance
- [ ] Detect overlapping tasks in schedule
- [ ] Find no conflicts in clean schedule
- [ ] Calculate time per pet
- [ ] Calculate utilization percentage

---

## Success Criteria

✓ All new methods have tests
✓ Tests pass
✓ Sorting works on all criteria
✓ Filtering accurately identifies subsets
✓ Recurring tasks expand correctly
✓ Conflict detection finds overlaps
✓ No conflicts in properly scheduled tasks
✓ Time analysis adds up correctly
✓ Reflection.md documents tradeoffs
✓ Code is clear and well-commented


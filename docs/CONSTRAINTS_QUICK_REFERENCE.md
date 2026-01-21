# Database Constraints - Quick Reference Guide

## ✅ All Constraints Implemented and Verified

### 1. One Exam Per Module (UNIQUE)
- **Type**: UNIQUE constraint
- **Status**: ✅ Verified (already existed)
- **Constraint**: `examen_module_id_key`
- **Test**: Try to create 2 exams for same module → FAILS

### 2. Valid Room Type (CHECK)
- **Type**: CHECK constraint
- **Status**: ✅ Verified (already existed)
- **Constraint**: `salle_type_check`
- **Allowed Values**: 'amphi', 'salle'
- **Test**: Try to insert room with type 'invalid' → FAILS

### 3. Student No Overlapping Exams (TRIGGER)
- **Type**: Trigger function
- **Status**: ✅ FIXED (was incorrect, now correct)
- **Function**: `check_student_no_overlapping_exams()`
- **Trigger**: `trg_student_no_overlapping_exams`
- **Logic**: Prevents students in same formation from having overlapping exams
- **Test**: Two exams for same formation at 09:00 and 10:00 → FAILS

### 4. Professor No Simultaneous Exams (TRIGGER)
- **Type**: Trigger function
- **Status**: ✅ FIXED (was incorrect, now correct)
- **Function**: `check_professor_no_simultaneous_exams()`
- **Trigger**: `trg_professor_no_simultaneous_exams`
- **Logic**: Prevents professor from supervising overlapping exams
- **Test**: Same professor at 09:00 and 10:00 → FAILS

### 5. Room Capacity Sufficient (TRIGGER)
- **Type**: Trigger function
- **Status**: ✅ ADDED (was missing)
- **Function**: `check_room_capacity()`
- **Trigger**: `trg_room_capacity`
- **Logic**: Ensures room capacity >= number of students in formation
- **Test**: Room with capacity 10 for formation with 20 students → FAILS

## Quick Test Examples

### ❌ Example 1: Violate UNIQUE constraint
```sql
-- This will FAIL
INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
VALUES ('2026-02-01', '09:00:00', 120, 1, 1, 1);

-- This will also FAIL (same module_id)
INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
VALUES ('2026-02-02', '14:00:00', 120, 1, 1, 1);
-- Error: duplicate key value violates unique constraint examen_module_id_key
```

### ✅ Example 2: Valid exam creation
```sql
-- This will SUCCEED
INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
VALUES ('2026-02-01', '09:00:00', 120, 1, 1, 1);
```

### ❌ Example 3: Violate student overlapping constraint
```sql
-- Exam 1 for formation (module 1)
INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
VALUES ('2026-02-10', '09:00:00', 120, 1, 1, 1);

-- Exam 2 for same formation (module 2) - OVERLAPS
INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
VALUES ('2026-02-10', '10:00:00', 120, 2, 2, 2);
-- Error: Un étudiant ne peut pas avoir deux examens en même temps
```

### ✅ Example 4: Non-overlapping exams for same formation
```sql
-- Exam 1 at 09:00
INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
VALUES ('2026-02-10', '09:00:00', 120, 1, 1, 1);

-- Exam 2 at 14:00 - NO OVERLAP
INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
VALUES ('2026-02-10', '14:00:00', 120, 2, 2, 2);
-- SUCCESS: No overlap, both exams allowed
```

### ❌ Example 5: Violate professor simultaneous constraint
```sql
-- Professor 1 at 09:00
INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
VALUES ('2026-02-15', '09:00:00', 120, 1, 1, 1);

-- Same professor at 10:00 - OVERLAPS
INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
VALUES ('2026-02-15', '10:00:00', 120, 2, 1, 2);
-- Error: Un professeur ne peut pas surveiller deux examens simultanément
```

### ❌ Example 6: Violate room capacity constraint
```sql
-- Formation with 20 students, room with capacity 10
INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
VALUES ('2026-02-20', '09:00:00', 120, 1, 1, 5);
-- Error: La capacité de la salle (10) est insuffisante pour le nombre d'étudiants (20)
```

## Files Created

1. **`scripts/constraints_analysis_and_fix.sql`** - Main constraint implementation
2. **`scripts/constraints_test_cases.sql`** - Comprehensive test cases
3. **`scripts/apply_constraints.py`** - Python script to apply constraints
4. **`scripts/test_constraints.py`** - Python script to test constraints
5. **`docs/CONSTRAINTS_IMPLEMENTATION.md`** - Full documentation
6. **`docs/CONSTRAINTS_QUICK_REFERENCE.md`** - This file

## How to Use

### Apply Constraints
```bash
python scripts/apply_constraints.py
```

### Test Constraints
```bash
python scripts/test_constraints.py
```

### Manual SQL Execution
```bash
psql -U postgres -d your_database -f scripts/constraints_analysis_and_fix.sql
psql -U postgres -d your_database -f scripts/constraints_test_cases.sql
```

## Summary

All 5 required constraints are now properly implemented:
- ✅ One exam per module (UNIQUE)
- ✅ Valid room type (CHECK)
- ✅ Student no overlapping exams (TRIGGER - FIXED)
- ✅ Professor no simultaneous exams (TRIGGER - FIXED)
- ✅ Room capacity sufficient (TRIGGER - ADDED)

The system is ready for automatic exam timetable generation with proper constraint enforcement at the database level.

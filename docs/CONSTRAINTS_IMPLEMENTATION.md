# Database Constraints Implementation - Exam Scheduling System

## Overview

This document describes the complete implementation of database constraints for the Exam Scheduling System. All constraints are enforced at the database level using PostgreSQL triggers, CHECK constraints, and UNIQUE constraints.

## Constraint Analysis

### ✅ Constraint 1: One Exam Per Module (UNIQUE)
**Status**: ✅ EXISTS and CORRECT  
**Type**: UNIQUE constraint  
**Location**: `examen.examen_module_id_key`  
**Implementation**:
```sql
ALTER TABLE examen ADD CONSTRAINT examen_module_id_key UNIQUE (module_id);
```

**Purpose**: Ensures each module can only have one exam scheduled.

---

### ✅ Constraint 2: Valid Room Type (CHECK)
**Status**: ✅ EXISTS and CORRECT  
**Type**: CHECK constraint  
**Location**: `salle.salle_type_check`  
**Implementation**:
```sql
CONSTRAINT salle_type_check CHECK (
    (type)::text = ANY (
        (ARRAY['amphi'::character varying, 'salle'::character varying])::text[]
    )
)
```

**Purpose**: Ensures room type is either 'amphi' or 'salle'.

---

### ✅ Constraint 3: Student Cannot Have Two Exams at the Same Time
**Status**: ❌ EXISTED but INCORRECT → ✅ FIXED  
**Type**: TRIGGER (PL/pgSQL)  
**Function**: `check_student_no_overlapping_exams()`  
**Trigger**: `trg_student_no_overlapping_exams`

**Previous Implementation** (INCORRECT):
- Only checked if student had more than one exam per day
- Did not check for overlapping time slots

**New Implementation** (CORRECT):
```sql
CREATE OR REPLACE FUNCTION check_student_no_overlapping_exams()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_formation_id INTEGER;
BEGIN
    -- Get formation_id for the module
    SELECT formation_id INTO v_formation_id
    FROM module
    WHERE id = NEW.module_id;
    
    -- Check for overlapping exams in the same formation
    IF EXISTS (
        SELECT 1
        FROM examen e
        JOIN module m ON m.id = e.module_id
        WHERE m.formation_id = v_formation_id
          AND e.date = NEW.date
          AND e.id <> COALESCE(NEW.id, 0)
          AND (
              NEW.heure_debut < (e.heure_debut + (e.duree_minutes || ' minutes')::interval)
              AND
              e.heure_debut < (NEW.heure_debut + (NEW.duree_minutes || ' minutes')::interval)
          )
    ) THEN
        RAISE EXCEPTION 'Un étudiant ne peut pas avoir deux examens en même temps';
    END IF;
    
    RETURN NEW;
END;
$$;
```

**Purpose**: Prevents students in the same formation from having overlapping exams.

**Logic**:
- Two exams overlap if:
  1. Same date
  2. Time ranges overlap: `start1 < end2 AND start2 < end1`

---

### ✅ Constraint 4: Professor Cannot Supervise Two Exams Simultaneously
**Status**: ❌ EXISTED but INCORRECT → ✅ FIXED  
**Type**: TRIGGER (PL/pgSQL)  
**Function**: `check_professor_no_simultaneous_exams()`  
**Trigger**: `trg_professor_no_simultaneous_exams`

**Previous Implementation** (INCORRECT):
- Only checked if professor had more than 3 exams per day
- Did not check for overlapping time slots

**New Implementation** (CORRECT):
```sql
CREATE OR REPLACE FUNCTION check_professor_no_simultaneous_exams()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check for overlapping exams for the same professor
    IF EXISTS (
        SELECT 1
        FROM examen e
        WHERE e.professeur_id = NEW.professeur_id
          AND e.date = NEW.date
          AND e.id <> COALESCE(NEW.id, 0)
          AND (
              NEW.heure_debut < (e.heure_debut + (e.duree_minutes || ' minutes')::interval)
              AND
              e.heure_debut < (NEW.heure_debut + (NEW.duree_minutes || ' minutes')::interval)
          )
    ) THEN
        RAISE EXCEPTION 'Un professeur ne peut pas surveiller deux examens simultanément';
    END IF;
    
    RETURN NEW;
END;
$$;
```

**Purpose**: Prevents a professor from supervising two exams at the same time.

---

### ✅ Constraint 5: Room Capacity Must Be Sufficient
**Status**: ❌ MISSING → ✅ ADDED  
**Type**: TRIGGER (PL/pgSQL)  
**Function**: `check_room_capacity()`  
**Trigger**: `trg_room_capacity`

**Implementation**:
```sql
CREATE OR REPLACE FUNCTION check_room_capacity()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_formation_id INTEGER;
    v_student_count INTEGER;
    v_room_capacity INTEGER;
BEGIN
    -- Get formation_id for the module
    SELECT formation_id INTO v_formation_id
    FROM module
    WHERE id = NEW.module_id;
    
    -- Count students in this formation
    SELECT COUNT(*) INTO v_student_count
    FROM etudiant
    WHERE formation_id = v_formation_id;
    
    -- Get room capacity
    SELECT capacite INTO v_room_capacity
    FROM salle
    WHERE id = NEW.salle_id;
    
    -- Check if room capacity is sufficient
    IF v_student_count > v_room_capacity THEN
        RAISE EXCEPTION 'La capacité de la salle (%) est insuffisante pour le nombre d''étudiants (%)', 
            v_room_capacity, v_student_count;
    END IF;
    
    RETURN NEW;
END;
$$;
```

**Purpose**: Ensures the room capacity is sufficient for all students in the formation.

**Logic**:
- Counts students in the formation
- Compares with room capacity
- Raises error if `student_count > room_capacity`

---

## Files Created

1. **`scripts/constraints_analysis_and_fix.sql`**
   - Drops incorrect triggers
   - Creates corrected triggers
   - Verifies existing constraints

2. **`scripts/constraints_test_cases.sql`**
   - Test cases that SHOULD FAIL (violate constraints)
   - Test cases that SHOULD SUCCEED (valid data)
   - Comprehensive coverage of all constraints

3. **`scripts/apply_constraints.py`**
   - Python script to apply constraints
   - Executes the SQL file safely

4. **`scripts/test_constraints.py`**
   - Python script to test constraints
   - Executes test cases and reports results

## How to Apply Constraints

### Option 1: Using Python Script (Recommended)
```bash
python scripts/apply_constraints.py
```

### Option 2: Using psql
```bash
psql -U postgres -d your_database -f scripts/constraints_analysis_and_fix.sql
```

## How to Test Constraints

### Option 1: Using Python Script (Recommended)
```bash
python scripts/test_constraints.py
```

### Option 2: Using psql
```bash
psql -U postgres -d your_database -f scripts/constraints_test_cases.sql
```

## Test Cases Summary

### Test Case 1: One Exam Per Module
- ❌ **FAIL**: Second exam for same module → UNIQUE violation
- ✅ **SUCCEED**: Different modules → Allowed

### Test Case 2: Valid Room Type
- ❌ **FAIL**: Invalid type ('invalid_type') → CHECK violation
- ✅ **SUCCEED**: Valid types ('amphi', 'salle') → Allowed

### Test Case 3: Student No Overlapping Exams
- ❌ **FAIL**: Two exams for same formation at 09:00 and 10:00 (overlap) → Trigger error
- ✅ **SUCCEED**: Two exams for same formation at 09:00 and 14:00 (no overlap) → Allowed

### Test Case 4: Professor No Simultaneous Exams
- ❌ **FAIL**: Same professor at 09:00 and 10:00 (overlap) → Trigger error
- ✅ **SUCCEED**: Same professor at 09:00 and 14:00 (no overlap) → Allowed

### Test Case 5: Room Capacity Sufficient
- ❌ **FAIL**: Room capacity < student count → Trigger error
- ✅ **SUCCEED**: Room capacity >= student count → Allowed

## Constraint Enforcement Summary

| Constraint | Type | Status | Trigger/Constraint Name |
|------------|------|--------|-------------------------|
| One exam per module | UNIQUE | ✅ Verified | `examen_module_id_key` |
| Valid room type | CHECK | ✅ Verified | `salle_type_check` |
| Student no overlapping exams | TRIGGER | ✅ Fixed | `trg_student_no_overlapping_exams` |
| Professor no simultaneous exams | TRIGGER | ✅ Fixed | `trg_professor_no_simultaneous_exams` |
| Room capacity sufficient | TRIGGER | ✅ Added | `trg_room_capacity` |

## Important Notes

1. **All constraints are enforced at the database level** - No application-level checks needed
2. **Triggers fire BEFORE INSERT/UPDATE** - Invalid data is rejected before insertion
3. **Existing data is preserved** - Constraints only affect new/modified data
4. **Error messages are in French** - Matches the application language
5. **Time overlap detection** - Uses interval arithmetic for accurate time calculations

## Database Schema Impact

The constraints work with the existing schema:
- `examen` table: Main table with triggers
- `module` table: Linked to `formation` for student counting
- `etudiant` table: Used to count students per formation
- `salle` table: Used to get room capacity
- `professeur` table: Used to check professor assignments

## Performance Considerations

- All triggers use indexed columns (`formation_id`, `professeur_id`, `salle_id`, `date`)
- EXISTS queries are optimized by PostgreSQL
- Triggers execute BEFORE INSERT/UPDATE, so invalid data never enters the database

## Conclusion

All required constraints are now properly implemented and tested:
- ✅ One exam per module (UNIQUE)
- ✅ Valid room type (CHECK)
- ✅ Student no overlapping exams (TRIGGER - FIXED)
- ✅ Professor no simultaneous exams (TRIGGER - FIXED)
- ✅ Room capacity sufficient (TRIGGER - ADDED)

The system is now ready for automatic exam timetable generation with proper constraint enforcement.

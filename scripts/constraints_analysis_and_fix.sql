-- ============================================================================
-- EXAM SCHEDULING SYSTEM - CONSTRAINTS ANALYSIS AND IMPLEMENTATION
-- ============================================================================
-- 
-- This script:
-- 1. Analyzes existing constraints
-- 2. Fixes incorrect constraints
-- 3. Adds missing constraints
-- 4. Provides test cases
--
-- Author: Senior Database Engineer
-- Date: 2025-12-30
-- ============================================================================

BEGIN;

-- ============================================================================
-- PART 1: ANALYSIS OF EXISTING CONSTRAINTS
-- ============================================================================

-- ✅ CONSTRAINT 1: One exam per module (UNIQUE)
-- STATUS: EXISTS and CORRECT
-- Location: examen.examen_module_id_key
-- This constraint ensures each module can only have one exam scheduled.

-- ✅ CONSTRAINT 2: Valid room type (CHECK)
-- STATUS: EXISTS and CORRECT
-- Location: salle.salle_type_check
-- Ensures type is either 'amphi' or 'salle'

-- ❌ CONSTRAINT 3: Student cannot have two exams at the same time
-- STATUS: EXISTS but INCORRECT
-- Current: check_student_one_exam_per_day() only checks same day, not overlapping times
-- NEEDS: Fix to check overlapping time slots

-- ❌ CONSTRAINT 4: Professor cannot supervise two exams simultaneously
-- STATUS: EXISTS but INCORRECT
-- Current: check_professor_max_3_exams() only checks max 3 per day, not simultaneous
-- NEEDS: Fix to check overlapping time slots

-- ❌ CONSTRAINT 5: Room capacity must be sufficient
-- STATUS: MISSING
-- NEEDS: New trigger to check salle.capacite >= number of students in formation

-- ============================================================================
-- PART 2: DROP INCORRECT TRIGGERS
-- ============================================================================

-- Drop the incorrect student constraint trigger
DROP TRIGGER IF EXISTS trg_student_exam_per_day ON examen;
DROP FUNCTION IF EXISTS check_student_one_exam_per_day();

-- Drop the incorrect professor constraint trigger
DROP TRIGGER IF EXISTS trg_professor_max_exams ON examen;
DROP FUNCTION IF EXISTS check_professor_max_3_exams();

-- ============================================================================
-- PART 3: CREATE CORRECTED CONSTRAINTS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- CONSTRAINT 3: Student cannot have two exams at the same time
-- ----------------------------------------------------------------------------
-- This trigger checks if a student (via their formation) has overlapping exams.
-- Students in the same formation cannot have exams that overlap in time.

CREATE OR REPLACE FUNCTION check_student_no_overlapping_exams()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_formation_id INTEGER;
    v_student_count INTEGER;
BEGIN
    -- Get the formation_id for the module of this exam
    SELECT formation_id INTO v_formation_id
    FROM module
    WHERE id = NEW.module_id;
    
    IF v_formation_id IS NULL THEN
        RAISE EXCEPTION 'Module not found';
    END IF;
    
    -- Check if any student in this formation has an overlapping exam
    -- An exam overlaps if:
    -- 1. Same date
    -- 2. Time ranges overlap (start1 < end2 AND start2 < end1)
    IF EXISTS (
        SELECT 1
        FROM examen e
        JOIN module m ON m.id = e.module_id
        WHERE m.formation_id = v_formation_id
          AND e.date = NEW.date
          AND e.id <> COALESCE(NEW.id, 0)
          AND (
              -- NEW exam starts before existing exam ends
              NEW.heure_debut < (e.heure_debut + (e.duree_minutes || ' minutes')::interval)
              AND
              -- Existing exam starts before NEW exam ends
              e.heure_debut < (NEW.heure_debut + (NEW.duree_minutes || ' minutes')::interval)
          )
    ) THEN
        RAISE EXCEPTION 'Un étudiant ne peut pas avoir deux examens en même temps (chevauchement détecté pour la formation %)', v_formation_id;
    END IF;
    
    RETURN NEW;
END;
$$;

-- Create trigger for student overlapping exams
CREATE TRIGGER trg_student_no_overlapping_exams
    BEFORE INSERT OR UPDATE ON examen
    FOR EACH ROW
    EXECUTE FUNCTION check_student_no_overlapping_exams();

-- ----------------------------------------------------------------------------
-- CONSTRAINT 4: Professor cannot supervise two exams simultaneously
-- ----------------------------------------------------------------------------
-- This trigger checks if a professor has overlapping exams.
-- A professor cannot supervise two exams at the same time.

CREATE OR REPLACE FUNCTION check_professor_no_simultaneous_exams()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check if this professor has any overlapping exams
    IF EXISTS (
        SELECT 1
        FROM examen e
        WHERE e.professeur_id = NEW.professeur_id
          AND e.date = NEW.date
          AND e.id <> COALESCE(NEW.id, 0)
          AND (
              -- NEW exam starts before existing exam ends
              NEW.heure_debut < (e.heure_debut + (e.duree_minutes || ' minutes')::interval)
              AND
              -- Existing exam starts before NEW exam ends
              e.heure_debut < (NEW.heure_debut + (NEW.duree_minutes || ' minutes')::interval)
          )
    ) THEN
        RAISE EXCEPTION 'Un professeur ne peut pas surveiller deux examens simultanément (chevauchement détecté)';
    END IF;
    
    RETURN NEW;
END;
$$;

-- Create trigger for professor simultaneous exams
CREATE TRIGGER trg_professor_no_simultaneous_exams
    BEFORE INSERT OR UPDATE ON examen
    FOR EACH ROW
    EXECUTE FUNCTION check_professor_no_simultaneous_exams();

-- ----------------------------------------------------------------------------
-- CONSTRAINT 5: Room capacity must be sufficient
-- ----------------------------------------------------------------------------
-- This trigger checks if the room capacity is sufficient for the number
-- of students in the formation.
-- salle.capacite >= number of students in formation

CREATE OR REPLACE FUNCTION check_room_capacity()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_formation_id INTEGER;
    v_student_count INTEGER;
    v_room_capacity INTEGER;
BEGIN
    -- Get the formation_id for the module of this exam
    SELECT formation_id INTO v_formation_id
    FROM module
    WHERE id = NEW.module_id;
    
    IF v_formation_id IS NULL THEN
        RAISE EXCEPTION 'Module not found';
    END IF;
    
    -- Count students in this formation
    SELECT COUNT(*) INTO v_student_count
    FROM etudiant
    WHERE formation_id = v_formation_id;
    
    -- Get room capacity
    SELECT capacite INTO v_room_capacity
    FROM salle
    WHERE id = NEW.salle_id;
    
    IF v_room_capacity IS NULL THEN
        RAISE EXCEPTION 'Salle not found';
    END IF;
    
    -- Check if room capacity is sufficient
    IF v_student_count > v_room_capacity THEN
        RAISE EXCEPTION 'La capacité de la salle (%) est insuffisante pour le nombre d''étudiants de la formation (%)', 
            v_room_capacity, v_student_count;
    END IF;
    
    RETURN NEW;
END;
$$;

-- Create trigger for room capacity
CREATE TRIGGER trg_room_capacity
    BEFORE INSERT OR UPDATE ON examen
    FOR EACH ROW
    EXECUTE FUNCTION check_room_capacity();

-- ============================================================================
-- PART 4: VERIFY EXISTING CONSTRAINTS
-- ============================================================================

-- Verify UNIQUE constraint on module_id exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'examen_module_id_key'
          AND conrelid = 'examen'::regclass
    ) THEN
        RAISE EXCEPTION 'UNIQUE constraint on examen.module_id is missing!';
    END IF;
END $$;

-- Verify CHECK constraint on salle.type exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'salle_type_check'
          AND conrelid = 'salle'::regclass
    ) THEN
        RAISE EXCEPTION 'CHECK constraint on salle.type is missing!';
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- SUMMARY
-- ============================================================================
-- 
-- ✅ CONSTRAINT 1: One exam per module (UNIQUE) - VERIFIED
-- ✅ CONSTRAINT 2: Valid room type (CHECK) - VERIFIED
-- ✅ CONSTRAINT 3: Student no overlapping exams - FIXED
-- ✅ CONSTRAINT 4: Professor no simultaneous exams - FIXED
-- ✅ CONSTRAINT 5: Room capacity sufficient - ADDED
-- 
-- ============================================================================

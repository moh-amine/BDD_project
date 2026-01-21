-- ============================================================================
-- EXAM SCHEDULING SYSTEM - CONSTRAINT TEST CASES
-- ============================================================================
-- 
-- This script provides test cases to verify all constraints work correctly.
-- It includes:
-- 1. Test cases that SHOULD FAIL (violate constraints)
-- 2. Test cases that SHOULD SUCCEED (valid data)
--
-- IMPORTANT: Run constraints_analysis_and_fix.sql FIRST before running these tests.
--
-- Author: Senior Database Engineer
-- Date: 2025-12-30
-- ============================================================================

-- ============================================================================
-- SETUP: Get sample IDs for testing
-- ============================================================================

-- We'll use variables to make tests clearer
-- In practice, you would replace these with actual IDs from your database

-- ============================================================================
-- TEST CASE 1: One Exam Per Module (UNIQUE CONSTRAINT)
-- ============================================================================

-- ❌ THIS SHOULD FAIL: Trying to create a second exam for the same module
-- Expected Error: "duplicate key value violates unique constraint examen_module_id_key"

DO $$
DECLARE
    v_module_id INTEGER;
    v_prof_id INTEGER;
    v_salle_id INTEGER;
BEGIN
    -- Get first module, professor, and salle
    SELECT id INTO v_module_id FROM module LIMIT 1;
    SELECT id INTO v_prof_id FROM professeur LIMIT 1;
    SELECT id INTO v_salle_id FROM salle LIMIT 1;
    
    -- First exam (should succeed)
    INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
    VALUES ('2026-02-01', '09:00:00', 120, v_module_id, v_prof_id, v_salle_id);
    
    -- Second exam for same module (SHOULD FAIL)
    BEGIN
        INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
        VALUES ('2026-02-02', '14:00:00', 120, v_module_id, v_prof_id, v_salle_id);
        
        RAISE EXCEPTION 'TEST FAILED: Second exam for same module was allowed (should have failed)';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE '✅ TEST PASSED: UNIQUE constraint on module_id works correctly';
    END;
    
    -- Cleanup
    DELETE FROM examen WHERE module_id = v_module_id;
END $$;

-- ============================================================================
-- TEST CASE 2: Valid Room Type (CHECK CONSTRAINT)
-- ============================================================================

-- ❌ THIS SHOULD FAIL: Invalid room type
-- Expected Error: "new row for relation salle violates check constraint salle_type_check"

DO $$
BEGIN
    BEGIN
        INSERT INTO salle (nom, capacite, type, batiment)
        VALUES ('Test Salle', 50, 'invalid_type', 'Bloc Test');
        
        RAISE EXCEPTION 'TEST FAILED: Invalid room type was allowed (should have failed)';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE '✅ TEST PASSED: CHECK constraint on salle.type works correctly';
    END;
END $$;

-- ✅ THIS SHOULD SUCCEED: Valid room types
DO $$
BEGIN
    INSERT INTO salle (nom, capacite, type, batiment)
    VALUES ('Test Amphi', 200, 'amphi', 'Bloc Test');
    
    INSERT INTO salle (nom, capacite, type, batiment)
    VALUES ('Test Salle', 50, 'salle', 'Bloc Test');
    
    RAISE NOTICE '✅ TEST PASSED: Valid room types accepted';
    
    -- Cleanup
    DELETE FROM salle WHERE nom IN ('Test Amphi', 'Test Salle');
END $$;

-- ============================================================================
-- TEST CASE 3: Student No Overlapping Exams
-- ============================================================================

-- ❌ THIS SHOULD FAIL: Two exams for same formation at overlapping times
-- Expected Error: "Un étudiant ne peut pas avoir deux examens en même temps"

DO $$
DECLARE
    v_formation_id INTEGER;
    v_module1_id INTEGER;
    v_module2_id INTEGER;
    v_prof1_id INTEGER;
    v_prof2_id INTEGER;
    v_salle1_id INTEGER;
    v_salle2_id INTEGER;
BEGIN
    -- Get a formation with at least 2 modules
    SELECT f.id INTO v_formation_id
    FROM formation f
    WHERE EXISTS (
        SELECT 1 FROM module m WHERE m.formation_id = f.id
    )
    AND (
        SELECT COUNT(*) FROM module m WHERE m.formation_id = f.id
    ) >= 2
    LIMIT 1;
    
    -- Get 2 modules from this formation
    SELECT id INTO v_module1_id FROM module WHERE formation_id = v_formation_id LIMIT 1;
    SELECT id INTO v_module2_id FROM module WHERE formation_id = v_formation_id OFFSET 1 LIMIT 1;
    
    -- Get professors and salles
    SELECT id INTO v_prof1_id FROM professeur LIMIT 1;
    SELECT id INTO v_prof2_id FROM professeur OFFSET 1 LIMIT 1;
    SELECT id INTO v_salle1_id FROM salle LIMIT 1;
    SELECT id INTO v_salle2_id FROM salle OFFSET 1 LIMIT 1;
    
    -- First exam (should succeed)
    INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
    VALUES ('2026-02-10', '09:00:00', 120, v_module1_id, v_prof1_id, v_salle1_id);
    
    -- Second exam overlapping (SHOULD FAIL)
    BEGIN
        INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
        VALUES ('2026-02-10', '10:00:00', 120, v_module2_id, v_prof2_id, v_salle2_id);
        
        RAISE EXCEPTION 'TEST FAILED: Overlapping exams for same formation were allowed';
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM LIKE '%chevauchement%' OR SQLERRM LIKE '%même temps%' THEN
                RAISE NOTICE '✅ TEST PASSED: Student overlapping exam constraint works correctly';
            ELSE
                RAISE;
            END IF;
    END;
    
    -- Cleanup
    DELETE FROM examen WHERE module_id IN (v_module1_id, v_module2_id);
END $$;

-- ✅ THIS SHOULD SUCCEED: Two exams for same formation at different times
DO $$
DECLARE
    v_formation_id INTEGER;
    v_module1_id INTEGER;
    v_module2_id INTEGER;
    v_prof1_id INTEGER;
    v_prof2_id INTEGER;
    v_salle1_id INTEGER;
    v_salle2_id INTEGER;
BEGIN
    -- Get a formation with at least 2 modules
    SELECT f.id INTO v_formation_id
    FROM formation f
    WHERE (
        SELECT COUNT(*) FROM module m WHERE m.formation_id = f.id
    ) >= 2
    LIMIT 1;
    
    -- Get 2 modules from this formation
    SELECT id INTO v_module1_id FROM module WHERE formation_id = v_formation_id LIMIT 1;
    SELECT id INTO v_module2_id FROM module WHERE formation_id = v_formation_id OFFSET 1 LIMIT 1;
    
    -- Get professors and salles
    SELECT id INTO v_prof1_id FROM professeur LIMIT 1;
    SELECT id INTO v_prof2_id FROM professeur OFFSET 1 LIMIT 1;
    SELECT id INTO v_salle1_id FROM salle LIMIT 1;
    SELECT id INTO v_salle2_id FROM salle OFFSET 1 LIMIT 1;
    
    -- First exam at 09:00
    INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
    VALUES ('2026-02-11', '09:00:00', 120, v_module1_id, v_prof1_id, v_salle1_id);
    
    -- Second exam at 14:00 (no overlap)
    INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
    VALUES ('2026-02-11', '14:00:00', 120, v_module2_id, v_prof2_id, v_salle2_id);
    
    RAISE NOTICE '✅ TEST PASSED: Non-overlapping exams for same formation accepted';
    
    -- Cleanup
    DELETE FROM examen WHERE module_id IN (v_module1_id, v_module2_id);
END $$;

-- ============================================================================
-- TEST CASE 4: Professor No Simultaneous Exams
-- ============================================================================

-- ❌ THIS SHOULD FAIL: Same professor supervising two overlapping exams
-- Expected Error: "Un professeur ne peut pas surveiller deux examens simultanément"

DO $$
DECLARE
    v_prof_id INTEGER;
    v_module1_id INTEGER;
    v_module2_id INTEGER;
    v_salle1_id INTEGER;
    v_salle2_id INTEGER;
BEGIN
    -- Get a professor
    SELECT id INTO v_prof_id FROM professeur LIMIT 1;
    
    -- Get 2 different modules
    SELECT id INTO v_module1_id FROM module LIMIT 1;
    SELECT id INTO v_module2_id FROM module OFFSET 1 LIMIT 1;
    
    -- Get 2 different salles
    SELECT id INTO v_salle1_id FROM salle LIMIT 1;
    SELECT id INTO v_salle2_id FROM salle OFFSET 1 LIMIT 1;
    
    -- First exam (should succeed)
    INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
    VALUES ('2026-02-15', '09:00:00', 120, v_module1_id, v_prof_id, v_salle1_id);
    
    -- Second exam with same professor overlapping (SHOULD FAIL)
    BEGIN
        INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
        VALUES ('2026-02-15', '10:00:00', 120, v_module2_id, v_prof_id, v_salle2_id);
        
        RAISE EXCEPTION 'TEST FAILED: Overlapping exams for same professor were allowed';
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM LIKE '%simultanément%' OR SQLERRM LIKE '%chevauchement%' THEN
                RAISE NOTICE '✅ TEST PASSED: Professor simultaneous exam constraint works correctly';
            ELSE
                RAISE;
            END IF;
    END;
    
    -- Cleanup
    DELETE FROM examen WHERE professeur_id = v_prof_id AND date = '2026-02-15';
END $$;

-- ✅ THIS SHOULD SUCCEED: Same professor supervising two non-overlapping exams
DO $$
DECLARE
    v_prof_id INTEGER;
    v_module1_id INTEGER;
    v_module2_id INTEGER;
    v_salle1_id INTEGER;
    v_salle2_id INTEGER;
BEGIN
    -- Get a professor
    SELECT id INTO v_prof_id FROM professeur LIMIT 1;
    
    -- Get 2 different modules
    SELECT id INTO v_module1_id FROM module LIMIT 1;
    SELECT id INTO v_module2_id FROM module OFFSET 1 LIMIT 1;
    
    -- Get 2 different salles
    SELECT id INTO v_salle1_id FROM salle LIMIT 1;
    SELECT id INTO v_salle2_id FROM salle OFFSET 1 LIMIT 1;
    
    -- First exam at 09:00
    INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
    VALUES ('2026-02-16', '09:00:00', 120, v_module1_id, v_prof_id, v_salle1_id);
    
    -- Second exam at 14:00 (no overlap)
    INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
    VALUES ('2026-02-16', '14:00:00', 120, v_module2_id, v_prof_id, v_salle2_id);
    
    RAISE NOTICE '✅ TEST PASSED: Non-overlapping exams for same professor accepted';
    
    -- Cleanup
    DELETE FROM examen WHERE professeur_id = v_prof_id AND date = '2026-02-16';
END $$;

-- ============================================================================
-- TEST CASE 5: Room Capacity Sufficient
-- ============================================================================

-- ❌ THIS SHOULD FAIL: Room capacity too small for formation
-- Expected Error: "La capacité de la salle ... est insuffisante"

DO $$
DECLARE
    v_formation_id INTEGER;
    v_student_count INTEGER;
    v_module_id INTEGER;
    v_prof_id INTEGER;
    v_small_salle_id INTEGER;
BEGIN
    -- Find a formation with many students
    SELECT f.id, COUNT(e.id) INTO v_formation_id, v_student_count
    FROM formation f
    JOIN etudiant e ON e.formation_id = f.id
    GROUP BY f.id
    HAVING COUNT(e.id) > 0
    ORDER BY COUNT(e.id) DESC
    LIMIT 1;
    
    -- Get a module from this formation
    SELECT id INTO v_module_id FROM module WHERE formation_id = v_formation_id LIMIT 1;
    
    -- Get a professor
    SELECT id INTO v_prof_id FROM professeur LIMIT 1;
    
    -- Create a small room (capacity less than student count)
    INSERT INTO salle (nom, capacite, type, batiment)
    VALUES ('Small Test Room', v_student_count - 1, 'salle', 'Bloc Test')
    RETURNING id INTO v_small_salle_id;
    
    -- Try to create exam (SHOULD FAIL)
    BEGIN
        INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
        VALUES ('2026-02-20', '09:00:00', 120, v_module_id, v_prof_id, v_small_salle_id);
        
        RAISE EXCEPTION 'TEST FAILED: Exam with insufficient room capacity was allowed';
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM LIKE '%capacité%' OR SQLERRM LIKE '%insuffisante%' THEN
                RAISE NOTICE '✅ TEST PASSED: Room capacity constraint works correctly';
            ELSE
                RAISE;
            END IF;
    END;
    
    -- Cleanup
    DELETE FROM salle WHERE id = v_small_salle_id;
END $$;

-- ✅ THIS SHOULD SUCCEED: Room capacity sufficient for formation
DO $$
DECLARE
    v_formation_id INTEGER;
    v_student_count INTEGER;
    v_module_id INTEGER;
    v_prof_id INTEGER;
    v_large_salle_id INTEGER;
BEGIN
    -- Find a formation
    SELECT f.id, COUNT(e.id) INTO v_formation_id, v_student_count
    FROM formation f
    JOIN etudiant e ON e.formation_id = f.id
    GROUP BY f.id
    HAVING COUNT(e.id) > 0
    LIMIT 1;
    
    -- Get a module from this formation
    SELECT id INTO v_module_id FROM module WHERE formation_id = v_formation_id LIMIT 1;
    
    -- Get a professor
    SELECT id INTO v_prof_id FROM professeur LIMIT 1;
    
    -- Create a large room (capacity >= student count)
    INSERT INTO salle (nom, capacite, type, batiment)
    VALUES ('Large Test Room', v_student_count + 10, 'amphi', 'Bloc Test')
    RETURNING id INTO v_large_salle_id;
    
    -- Create exam (should succeed)
    INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
    VALUES ('2026-02-21', '09:00:00', 120, v_module_id, v_prof_id, v_large_salle_id);
    
    RAISE NOTICE '✅ TEST PASSED: Exam with sufficient room capacity accepted';
    
    -- Cleanup
    DELETE FROM examen WHERE salle_id = v_large_salle_id;
    DELETE FROM salle WHERE id = v_large_salle_id;
END $$;

-- ============================================================================
-- SUMMARY
-- ============================================================================
-- 
-- All test cases completed. Review the output to verify:
-- ✅ UNIQUE constraint on module_id works
-- ✅ CHECK constraint on salle.type works
-- ✅ Student overlapping exam constraint works
-- ✅ Professor simultaneous exam constraint works
-- ✅ Room capacity constraint works
-- 
-- ============================================================================

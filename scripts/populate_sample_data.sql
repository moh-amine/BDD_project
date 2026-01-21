BEGIN;

-- ===============================
-- 1️⃣ DEPARTEMENTS
-- ===============================
INSERT INTO departement (nom)
VALUES
('Informatique'),
('Physique'),
('Mathématiques')
ON CONFLICT (nom) DO NOTHING;

-- ===============================
-- 2️⃣ FORMATIONS (ALL REQUIRED COLUMNS)
-- ===============================

-- Informatique
INSERT INTO formation (nom, niveau, nb_modules, departement_id)
SELECT 'Licence Informatique', 'Licence', 6, id
FROM departement WHERE nom = 'Informatique';

INSERT INTO formation (nom, niveau, nb_modules, departement_id)
SELECT 'Master Informatique', 'Master', 4, id
FROM departement WHERE nom = 'Informatique';

-- Physique
INSERT INTO formation (nom, niveau, nb_modules, departement_id)
SELECT 'Licence Physique', 'Licence', 6, id
FROM departement WHERE nom = 'Physique';

INSERT INTO formation (nom, niveau, nb_modules, departement_id)
SELECT 'Master Physique', 'Master', 4, id
FROM departement WHERE nom = 'Physique';

-- Mathématiques
INSERT INTO formation (nom, niveau, nb_modules, departement_id)
SELECT 'Licence Mathématiques', 'Licence', 6, id
FROM departement WHERE nom = 'Mathématiques';

INSERT INTO formation (nom, niveau, nb_modules, departement_id)
SELECT 'Master Mathématiques', 'Master', 4, id
FROM departement WHERE nom = 'Mathématiques';

-- ===============================
-- 3️⃣ MODULES
-- ===============================

-- Informatique
INSERT INTO module (nom, credits, formation_id)
SELECT 'Bases de Données', 6, id FROM formation WHERE nom = 'Licence Informatique';

INSERT INTO module (nom, credits, formation_id)
SELECT 'Programmation Python', 6, id FROM formation WHERE nom = 'Licence Informatique';

INSERT INTO module (nom, credits, formation_id)
SELECT 'Systèmes d''exploitation', 6, id FROM formation WHERE nom = 'Master Informatique';

-- Physique
INSERT INTO module (nom, credits, formation_id)
SELECT 'Mécanique Générale', 6, id FROM formation WHERE nom = 'Licence Physique';

INSERT INTO module (nom, credits, formation_id)
SELECT 'Électromagnétisme', 6, id FROM formation WHERE nom = 'Licence Physique';

INSERT INTO module (nom, credits, formation_id)
SELECT 'Physique Quantique', 6, id FROM formation WHERE nom = 'Master Physique';

-- Mathématiques
INSERT INTO module (nom, credits, formation_id)
SELECT 'Analyse Mathématique', 6, id FROM formation WHERE nom = 'Licence Mathématiques';

INSERT INTO module (nom, credits, formation_id)
SELECT 'Algèbre Linéaire', 6, id FROM formation WHERE nom = 'Licence Mathématiques';

INSERT INTO module (nom, credits, formation_id)
SELECT 'Probabilités', 6, id FROM formation WHERE nom = 'Master Mathématiques';

COMMIT;

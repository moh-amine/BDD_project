import streamlit as st

# ======================
# IMPORTS BACKEND
# ======================
from backend.database.queries import (
    get_all_examens,
    get_examens_simple,
    get_modules,
    get_professeurs,
    get_salles,
    get_departements,
    get_formations_by_departement,
    get_examens_filtered,
    kpi_occupation_salles,
    kpi_examens_par_prof
)

from backend.services.examen_service import (
    create_examen,
    delete_examen,
    update_examen
)

from backend.optimization.scheduler import generate_schedule


# ======================
# CONFIG STREAMLIT
# ======================
st.set_page_config(page_title="Exam Scheduler", layout="wide")

st.title("📅 Exam Scheduler")
st.write("Interface de gestion et d’optimisation des examens")

# ======================
# CHARGEMENT GLOBAL DES DONNÉES
# ======================
modules = get_modules()
professeurs = get_professeurs()
salles = get_salles()
departements = get_departements()
examens_simple = get_examens_simple()

# ======================
# 🔍 FILTRES ANALYTIQUES
# ======================
st.subheader("🔍 Filtres analytiques")

dept = st.selectbox(
    "Département",
    departements,
    format_func=lambda x: x["nom"],
    key="filter_dept"
)

formations = get_formations_by_departement(dept["id"])
formation = st.selectbox(
    "Formation",
    formations,
    format_func=lambda x: x["nom"],
    key="filter_form"
)

prof_filter = st.selectbox(
    "Professeur",
    professeurs,
    format_func=lambda x: x["nom"],
    key="filter_prof"
)

filtered_examens = get_examens_filtered(
    dept_id=dept["id"],
    formation_id=formation["id"],
    professeur_id=prof_filter["id"]
)

st.dataframe(filtered_examens)

# ======================
# 📊 DASHBOARD KPI
# ======================
st.subheader("📊 Dashboard KPI")

col1, col2 = st.columns(2)

with col1:
    st.write("📌 Occupation des salles")
    st.dataframe(kpi_occupation_salles())

with col2:
    st.write("👨‍🏫 Examens par professeur")
    st.dataframe(kpi_examens_par_prof())

# ======================
# ⚙️ OPTIMISATION AUTO
# ======================
st.subheader("⚙️ Génération automatique")

if st.button("Générer emploi du temps automatiquement", key="btn_generate"):
    generate_schedule()
    st.success("Emploi du temps généré automatiquement")
    st.experimental_rerun()

# ======================
# ➕ AJOUT EXAMEN
# ======================
st.subheader("➕ Ajouter un examen")

col1, col2, col3 = st.columns(3)

with col1:
    date = st.date_input("Date", key="add_date")
    heure = st.time_input("Heure de début", key="add_time")

with col2:
    duree = st.number_input(
        "Durée (minutes)",
        min_value=30,
        step=30,
        key="add_duree"
    )
    module = st.selectbox(
        "Module",
        modules,
        format_func=lambda x: x["nom"],
        key="add_module"
    )

with col3:
    professeur = st.selectbox(
        "Professeur",
        professeurs,
        format_func=lambda x: x["nom"],
        key="add_prof"
    )
    salle = st.selectbox(
        "Salle",
        salles,
        format_func=lambda x: x["nom"],
        key="add_salle"
    )

if st.button("Créer l'examen", key="btn_add"):
    success, message = create_examen(
        date,
        heure,
        duree,
        module["id"],
        professeur["id"],
        salle["id"]
    )

    if success:
        st.success(message)
        st.experimental_rerun()
    else:
        st.error(message)

# ======================
# 📋 LISTE DES EXAMENS
# ======================
st.subheader("📋 Liste des examens")

examens = get_all_examens()
if examens:
    st.dataframe(examens)
else:
    st.info("Aucun examen enregistré")

# ======================
# 🗑 SUPPRESSION
# ======================
st.subheader("🗑 Supprimer un examen")

if examens_simple:
    exam_to_delete = st.selectbox(
        "Choisir un examen à supprimer",
        examens_simple,
        format_func=lambda x: x["label"],
        key="delete_exam"
    )

    if st.button("Supprimer l'examen", key="btn_delete"):
        success, message = delete_examen(exam_to_delete["id"])

        if success:
            st.success(message)
            st.experimental_rerun()
        else:
            st.error(message)
else:
    st.info("Aucun examen à supprimer")

# ======================
# ✏️ MODIFICATION
# ======================
st.subheader("✏️ Modifier un examen")

if examens_simple:
    exam_to_edit = st.selectbox(
        "Choisir un examen à modifier",
        examens_simple,
        format_func=lambda x: x["label"],
        key="edit_exam"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        new_date = st.date_input("Nouvelle date", key="edit_date")
        new_time = st.time_input("Nouvelle heure", key="edit_time")

    with col2:
        new_duree = st.number_input(
            "Nouvelle durée (minutes)",
            min_value=30,
            step=30,
            key="edit_duree"
        )
        new_module = st.selectbox(
            "Nouveau module",
            modules,
            format_func=lambda x: x["nom"],
            key="edit_module"
        )

    with col3:
        new_prof = st.selectbox(
            "Nouveau professeur",
            professeurs,
            format_func=lambda x: x["nom"],
            key="edit_prof"
        )
        new_salle = st.selectbox(
            "Nouvelle salle",
            salles,
            format_func=lambda x: x["nom"],
            key="edit_salle"
        )

    if st.button("Modifier l'examen", key="btn_edit"):
        success, message = update_examen(
            exam_to_edit["id"],
            new_date,
            new_time,
            new_duree,
            new_module["id"],
            new_prof["id"],
            new_salle["id"]
        )

        if success:
            st.success(message)
            st.experimental_rerun()
        else:
            st.error(message)

"""
Streamlit Frontend Application
===============================
Main UI for the Exam Scheduling and Management System.
Implements role-based access control with three user types:
- ADMIN: Full access to all features
- PROFESSEUR: Read-only access to own exams
- ETUDIANT: Read-only access to exams for their formation

Author: Exam Scheduling System
"""

import sys
import os

# Add project root to Python path to enable backend imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Try to load .env file for local development (optional)
# This helps with local development but is not required for cloud deployment
try:
    from dotenv import load_dotenv
    env_path = os.path.join(project_root, ".env")
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path, override=False)
except ImportError:
    # python-dotenv not installed - that's OK, will use environment variables only
    pass
except Exception:
    # Silently fail - environment variables will be used instead
    pass

import streamlit as st
from datetime import date, time, timedelta

# ======================
# IMPORTS BACKEND
# ======================
from backend.database.queries import (
    get_all_examens,
    get_examens_simple,
    get_examen_details,
    get_modules,
    get_professeurs,
    get_salles,
    get_departements,
    get_formations_by_departement,
    get_modules_by_formation,
    get_examens_filtered,
    kpi_occupation_salles,
    kpi_examens_par_prof,
    get_examens_by_professeur,
    get_examens_by_etudiant_formation,
    get_etudiant_info
)

from backend.services.examen_service import (
    create_examen,
    delete_examen,
    update_examen
)

from backend.services.auth_service import (
    login,
    is_admin,
    is_professeur,
    is_etudiant
)

# Import scheduler - will be reloaded in admin_scheduling if needed
from backend.optimization.scheduler import generate_schedule


# ======================
# CONFIG STREAMLIT
# ======================
st.set_page_config(
    page_title="Exam Scheduler",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================
# SESSION STATE INITIALIZATION
# ======================
# Initialize session state variables for authentication
# Store user data in separate fields for easier access and validation
# Initialize each key individually to prevent AttributeError on reruns
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'linked_id' not in st.session_state:
    st.session_state.linked_id = None
if 'user' not in st.session_state:
    st.session_state.user = None  # Keep full user dict for compatibility

# Initialize page navigation state
if 'current_page' not in st.session_state:
    st.session_state.current_page = None


# ======================
# AUTHENTICATION FUNCTIONS
# ======================
def logout():
    """Clear session state and log out user."""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.linked_id = None
    st.session_state.user = None
    st.session_state.current_page = None
    st.rerun()


def show_login_page():
    """
    Display login page.
    Users must authenticate before accessing the system.
    """
    st.title("🔐 Connexion - Exam Scheduler")
    st.markdown("---")
    st.write("Veuillez vous connecter pour accéder au système")
    
    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("Nom d'utilisateur", key="login_username")
        password = st.text_input("Mot de passe", type="password", key="login_password")
        submit_button = st.form_submit_button("Se connecter", use_container_width=True)
        
        if submit_button:
            if username and password:
                # DEBUG: Log login attempt
                import sys
                print(f"[DEBUG FRONTEND] Login attempt - Username: '{username}', Password length: {len(password)}", file=sys.stderr)
                
                success, user_data, message = login(username, password)
                
                # DEBUG: Log login result
                print(f"[DEBUG FRONTEND] Login result - Success: {success}, Message: {message}", file=sys.stderr)
                if user_data:
                    print(f"[DEBUG FRONTEND] User data - ID: {user_data.get('id')}, Role: {user_data.get('role')}, Linked ID: {user_data.get('linked_id')}", file=sys.stderr)
                
                if success and user_data:
                    # Store session state properly
                    st.session_state.authenticated = True
                    st.session_state.user_id = user_data.get('id')
                    st.session_state.username = user_data.get('username')
                    st.session_state.role = user_data.get('role')
                    st.session_state.linked_id = user_data.get('linked_id')
                    st.session_state.user = user_data  # Keep for compatibility
                    
                    # Validate role and linked_id based on role
                    role = st.session_state.role
                    linked_id = st.session_state.linked_id
                    
                    # Defensive checks
                    if role == 'admin':
                        # Admin doesn't need linked_id
                        st.success(message)
                        st.rerun()
                    elif role in ['professeur', 'etudiant']:
                        # Professeur and Etudiant MUST have linked_id
                        if linked_id is None:
                            st.error(f"Erreur: Aucun {role} associé à ce compte. Veuillez contacter l'administrateur.")
                            logout()
                        else:
                            st.success(message)
                            st.rerun()
                    else:
                        st.error("Rôle utilisateur invalide")
                        logout()
                else:
                    st.error(message)
            else:
                st.warning("Veuillez remplir tous les champs")


# ======================
# SIDEBAR NAVIGATION
# ======================
def render_sidebar():
    """
    Render sidebar with user info and navigation based on role.
    This function handles all sidebar content including logout.
    """
    with st.sidebar:
        st.title("📅 Exam Scheduler")
        st.markdown("---")
        
        # User information (with defensive checks)
        username = st.session_state.get('username', 'N/A')
        role = st.session_state.get('role', 'unknown')
        st.write(f"**Utilisateur:** {username}")
        st.write(f"**Rôle:** {role.capitalize()}")
        st.markdown("---")
        
        # Navigation based on role
        
        if role == 'admin':
            pages = {
                "📊 Dashboard": "dashboard",
                "📋 Gérer les examens": "manage_exams",
                "⚙️ Planification": "scheduling",
                "📈 Analytiques": "analytics"
            }
        elif role == 'professeur':
            pages = {
                "📋 Mes examens": "my_exams",
                "📅 Mon emploi du temps": "schedule"
            }
        elif role == 'etudiant':
            pages = {
                "📅 Mon emploi du temps": "my_schedule",
                "📆 Vue calendrier": "calendar"
            }
        else:
            pages = {}
        
        # Page selection
        if pages:
            selected = st.radio(
                "Navigation",
                options=list(pages.keys()),
                key="nav_radio"
            )
            st.session_state.current_page = pages[selected]
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Déconnexion", use_container_width=True, type="primary"):
            logout()


# ======================
# ADMIN PAGES
# ======================
def admin_dashboard():
    """Admin dashboard with KPIs and overview."""
    st.header("📊 Tableau de bord")
    st.markdown("---")
    
    # Load KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        examens = get_all_examens()
        st.metric("Total Examens", len(examens) if examens else 0)
    
    with col2:
        modules = get_modules()
        st.metric("Total Modules", len(modules) if modules else 0)
    
    with col3:
        professeurs = get_professeurs()
        st.metric("Total Professeurs", len(professeurs) if professeurs else 0)
    
    with col4:
        salles = get_salles()
        st.metric("Total Salles", len(salles) if salles else 0)
    
    st.markdown("---")
    
    # KPI Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📌 Occupation des salles")
        occupation = kpi_occupation_salles()
        if occupation:
            st.dataframe(occupation, use_container_width=True)
        else:
            st.info("Aucune donnée disponible")
    
    with col2:
        st.subheader("👨‍🏫 Examens par professeur")
        exams_per_prof = kpi_examens_par_prof()
        if exams_per_prof:
            st.dataframe(exams_per_prof, use_container_width=True)
        else:
            st.info("Aucune donnée disponible")


def admin_manage_exams():
    """Admin page for managing exams (CRUD operations)."""
    st.header("📋 Gérer les examens")
    st.markdown("---")
    
    # Tabs for different operations
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Liste", "➕ Ajouter", "✏️ Modifier", "🗑 Supprimer"])
    
    with tab1:
        st.subheader("Liste de tous les examens")
        examens = get_all_examens()
        if examens:
            st.dataframe(examens, use_container_width=True)
            st.info(f"Total: {len(examens)} examen(s)")
        else:
            st.info("Aucun examen enregistré")
    
    with tab2:
        st.subheader("Ajouter un nouvel examen")
        
        # Load base data
        departements = get_departements()
        professeurs = get_professeurs()
        salles = get_salles()
        
        if not departements:
            st.warning("Aucun département disponible. Veuillez d'abord créer des départements.")
            return
        
        if not professeurs:
            st.warning("Aucun professeur disponible. Veuillez d'abord créer des professeurs.")
            return
        
        if not salles:
            st.warning("Aucune salle disponible. Veuillez d'abord créer des salles.")
            return
        
        # ======================
        # ACADEMIC STRUCTURE (Department → Formation → Module)
        # ======================
        st.markdown("#### 📚 Structure académique")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Step 1: Select Department
            dept = st.selectbox(
                "Département *",
                departements,
                format_func=lambda x: x["nom"],
                key="add_dept"
            )
        
        with col2:
            # Step 2: Load formations based on selected department
            formations = get_formations_by_departement(dept["id"])
            if formations:
                formation = st.selectbox(
                    "Formation *",
                    formations,
                    format_func=lambda x: x["nom"],
                    key="add_formation"
                )
                formation_id = formation.get("id") if formation else None
            else:
                st.warning("Aucune formation disponible pour ce département")
                formation_id = None
                formation = None
        
        with col3:
            # Step 3: Load modules based on selected formation
            if formation_id:
                modules = get_modules_by_formation(formation_id)
                if modules:
                    module = st.selectbox(
                        "Module *",
                        modules,
                        format_func=lambda x: x["nom"],
                        key="add_module"
                    )
                    module_id = module.get("id") if module else None
                else:
                    st.warning("Aucun module disponible pour cette formation")
                    module_id = None
                    module = None
            else:
                st.info("Sélectionnez d'abord une formation")
                module_id = None
                module = None
        
        st.markdown("---")
        
        # ======================
        # EXAM DETAILS (Date / Time / Duration)
        # ======================
        st.markdown("#### 📅 Détails de l'examen")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date = st.date_input("Date *", key="add_date")
        
        with col2:
            heure = st.time_input("Heure de début *", key="add_time")
        
        with col3:
            duree = st.number_input(
                "Durée (minutes) *",
                min_value=30,
                step=30,
                value=120,
                key="add_duree"
            )
        
        st.markdown("---")
        
        # ======================
        # RESOURCES (Professor / Room)
        # ======================
        st.markdown("#### 👥 Ressources")
        
        col1, col2 = st.columns(2)
        
        with col1:
            professeur = st.selectbox(
                "Professeur *",
                professeurs,
                format_func=lambda x: x["nom"],
                key="add_prof"
            )
        
        with col2:
            salle = st.selectbox(
                "Salle *",
                salles,
                format_func=lambda x: x["nom"],
                key="add_salle"
            )
        
        st.markdown("---")
        
        # ======================
        # SUBMIT BUTTON
        # ======================
        # Validate that all required fields are selected
        can_submit = (
            module_id is not None and
            professeur and professeur.get("id") and
            salle and salle.get("id")
        )
        
        if can_submit:
            if st.button("Créer l'examen", type="primary", use_container_width=True):
                success, message = create_examen(
                    date,
                    heure,
                    duree,
                    module_id,
                    professeur["id"],
                    salle["id"]
                )
                
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        else:
            st.info("⚠️ Veuillez sélectionner un département, une formation et un module pour créer l'examen")
            st.button("Créer l'examen", disabled=True, use_container_width=True)
    
    with tab3:
        st.subheader("Modifier un examen")
        examens_simple = get_examens_simple()
        departements = get_departements()
        professeurs = get_professeurs()
        salles = get_salles()
        
        if not examens_simple:
            st.info("Aucun examen à modifier")
            return
        
        if not departements or not professeurs or not salles:
            st.warning("Données incomplètes. Veuillez vérifier les départements, professeurs et salles.")
            return
        
        exam_to_edit = st.selectbox(
            "Choisir un examen à modifier",
            examens_simple,
            format_func=lambda x: x["label"],
            key="edit_exam"
        )
        
        # Get current exam details to pre-populate form
        exam_details = get_examen_details(exam_to_edit["id"])
        
        if not exam_details:
            st.error("Impossible de charger les détails de l'examen")
            return
        
        # ======================
        # ACADEMIC STRUCTURE (Department → Formation → Module)
        # ======================
        st.markdown("#### 📚 Structure académique")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Pre-select current department
            current_dept_id = exam_details.get('departement_id')
            dept_index = 0
            if current_dept_id:
                for idx, dept in enumerate(departements):
                    if dept['id'] == current_dept_id:
                        dept_index = idx
                        break
            
            dept = st.selectbox(
                "Département *",
                departements,
                index=dept_index,
                format_func=lambda x: x["nom"],
                key="edit_dept"
            )
        
        with col2:
            # Load formations based on selected department
            formations = get_formations_by_departement(dept["id"])
            if formations:
                # Pre-select current formation
                current_formation_id = exam_details.get('formation_id')
                formation_index = 0
                if current_formation_id:
                    for idx, form in enumerate(formations):
                        if form['id'] == current_formation_id:
                            formation_index = idx
                            break
                
                formation = st.selectbox(
                    "Formation *",
                    formations,
                    index=formation_index,
                    format_func=lambda x: x["nom"],
                    key="edit_formation"
                )
                formation_id = formation.get("id") if formation else None
            else:
                st.warning("Aucune formation disponible pour ce département")
                formation_id = None
                formation = None
        
        with col3:
            # Load modules based on selected formation
            if formation_id:
                modules = get_modules_by_formation(formation_id)
                if modules:
                    # Pre-select current module
                    current_module_id = exam_details.get('module_id')
                    module_index = 0
                    if current_module_id:
                        for idx, mod in enumerate(modules):
                            if mod['id'] == current_module_id:
                                module_index = idx
                                break
                    
                    new_module = st.selectbox(
                        "Module *",
                        modules,
                        index=module_index,
                        format_func=lambda x: x["nom"],
                        key="edit_module"
                    )
                    module_id = new_module.get("id") if new_module else None
                else:
                    st.warning("Aucun module disponible pour cette formation")
                    module_id = None
                    new_module = None
            else:
                st.info("Sélectionnez d'abord une formation")
                module_id = None
                new_module = None
        
        st.markdown("---")
        
        # ======================
        # EXAM DETAILS (Date / Time / Duration)
        # ======================
        st.markdown("#### 📅 Détails de l'examen")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_date = st.date_input(
                "Nouvelle date *",
                value=exam_details.get('date'),
                key="edit_date"
            )
        
        with col2:
            new_time = st.time_input(
                "Nouvelle heure *",
                value=exam_details.get('heure_debut'),
                key="edit_time"
            )
        
        with col3:
            new_duree = st.number_input(
                "Nouvelle durée (minutes) *",
                min_value=30,
                step=30,
                value=exam_details.get('duree_minutes', 120),
                key="edit_duree"
            )
        
        st.markdown("---")
        
        # ======================
        # RESOURCES (Professor / Room)
        # ======================
        st.markdown("#### 👥 Ressources")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pre-select current professor
            current_prof_id = exam_details.get('professeur_id')
            prof_index = 0
            if current_prof_id:
                for idx, prof in enumerate(professeurs):
                    if prof['id'] == current_prof_id:
                        prof_index = idx
                        break
            
            new_prof = st.selectbox(
                "Nouveau professeur *",
                professeurs,
                index=prof_index,
                format_func=lambda x: x["nom"],
                key="edit_prof"
            )
        
        with col2:
            # Pre-select current room
            current_salle_id = exam_details.get('salle_id')
            salle_index = 0
            if current_salle_id:
                for idx, sal in enumerate(salles):
                    if sal['id'] == current_salle_id:
                        salle_index = idx
                        break
            
            new_salle = st.selectbox(
                "Nouvelle salle *",
                salles,
                index=salle_index,
                format_func=lambda x: x["nom"],
                key="edit_salle"
            )
        
        st.markdown("---")
        
        # ======================
        # SUBMIT BUTTON
        # ======================
        can_submit = (
            module_id is not None and
            new_prof and new_prof.get("id") and
            new_salle and new_salle.get("id")
        )
        
        if can_submit:
            if st.button("Modifier l'examen", type="primary", use_container_width=True):
                success, message = update_examen(
                    exam_to_edit["id"],
                    new_date,
                    new_time,
                    new_duree,
                    module_id,
                    new_prof["id"],
                    new_salle["id"]
                )
                
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        else:
            st.info("⚠️ Veuillez sélectionner un département, une formation et un module")
            st.button("Modifier l'examen", disabled=True, use_container_width=True)
    
    with tab4:
        st.subheader("Supprimer un examen")
        examens_simple = get_examens_simple()
        
        if examens_simple:
            exam_to_delete = st.selectbox(
                "Choisir un examen à supprimer",
                examens_simple,
                format_func=lambda x: x["label"],
                key="delete_exam"
            )
            
            st.warning("⚠️ Cette action est irréversible")
            
            if st.button("Supprimer l'examen", type="primary", use_container_width=True):
                success, message = delete_examen(exam_to_delete["id"])
                
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        else:
            st.info("Aucun examen à supprimer")


def admin_scheduling():
    """Admin page for automatic scheduling."""
    st.header("⚙️ Planification automatique")
    st.markdown("---")
    
    st.info("Cette fonctionnalité génère automatiquement un emploi du temps pour les modules sans examen programmé.")
    
    # Configuration options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input(
            "Date de début",
            value=None,
            min_value=date.today() + timedelta(days=1),
            help="Date à partir de laquelle commencer la planification"
        )
    
    with col2:
        start_time = st.time_input(
            "Heure de début",
            value=time(9, 0),
            help="Heure de début du premier examen"
        )
    
    with col3:
        duration = st.number_input(
            "Durée (minutes)",
            min_value=60,
            max_value=300,
            value=120,
            step=30,
            help="Durée de chaque examen en minutes"
        )
    
    max_per_day = st.slider(
        "Maximum d'examens par jour",
        min_value=2,
        max_value=8,
        value=4,
        help="Nombre maximum d'examens à programmer par jour"
    )
    
    st.markdown("---")
    
    if st.button("🚀 Générer emploi du temps automatiquement", type="primary", use_container_width=True):
        if start_date is None:
            st.warning("⚠️ Veuillez sélectionner une date de début")
            return
        
        with st.spinner("Génération en cours... Veuillez patienter."):
            try:
                # Force reload module to avoid cache issues
                import importlib
                from backend.optimization import scheduler
                importlib.reload(scheduler)
                from backend.optimization.scheduler import generate_schedule
                
                results = generate_schedule(
                    start_date=start_date,
                    start_time=start_time,
                    duration_minutes=duration,
                    time_slots_per_day=max_per_day
                )
                
                # Display results
                st.markdown("### 📊 Résultats de la génération")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✅ Réussis", results['success'])
                with col2:
                    st.metric("❌ Échoués", results['failed'])
                with col3:
                    st.metric("📋 Total", results['total'])
                
                # Show details
                if results['details']:
                    st.markdown("---")
                    st.markdown("#### 📝 Détails")
                    
                    # Group by status
                    success_details = [d for d in results['details'] if d[1] == 'success']
                    failed_details = [d for d in results['details'] if d[1] == 'failed']
                    
                    if success_details:
                        with st.expander(f"✅ Examens programmés ({len(success_details)})", expanded=True):
                            for module_id, status, message in success_details:
                                st.success(f"• {message}")
                    
                    if failed_details:
                        with st.expander(f"❌ Modules non programmés ({len(failed_details)})", expanded=False):
                            for module_id, status, message in failed_details:
                                st.error(f"• {message}")
                
                if results['success'] > 0:
                    st.success(f"✅ {results['success']} examen(s) programmé(s) avec succès!")
                    st.balloons()
                    st.rerun()
                elif results['total'] == 0:
                    st.info("ℹ️ Tous les modules ont déjà un examen programmé.")
                else:
                    st.warning("⚠️ Aucun examen n'a pu être programmé. Vérifiez les contraintes (professeurs, salles, capacités).")
                    
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération: {str(e)}")
                import traceback
                with st.expander("Détails de l'erreur"):
                    st.code(traceback.format_exc())


def admin_analytics():
    """Admin page for analytics and filtering."""
    st.header("📈 Analytiques et filtres")
    st.markdown("---")
    
    st.subheader("🔍 Filtres analytiques")
    
    departements = get_departements()
    professeurs = get_professeurs()
    
    if departements:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            dept = st.selectbox(
                "Département",
                departements,
                format_func=lambda x: x["nom"],
                key="filter_dept"
            )
        
        with col2:
            formations = get_formations_by_departement(dept["id"])
            if formations:
                formation = st.selectbox(
                    "Formation",
                    formations,
                    format_func=lambda x: x["nom"],
                    key="filter_form"
                )
                # Defensive check: ensure formation is not None and has 'id' key
                formation_id = formation.get("id") if formation and isinstance(formation, dict) else None
            else:
                st.warning("Aucune formation disponible pour ce département")
                formation_id = None
        
        with col3:
            if professeurs:
                prof_filter = st.selectbox(
                    "Professeur",
                    professeurs,
                    format_func=lambda x: x["nom"],
                    key="filter_prof"
                )
                # Defensive check: ensure prof_filter is not None and has 'id' key
                prof_id = prof_filter.get("id") if prof_filter and isinstance(prof_filter, dict) else None
            else:
                st.warning("Aucun professeur disponible")
                prof_id = None
        
        # Only filter if we have valid selections
        if formation_id is not None and prof_id is not None:
            filtered_examens = get_examens_filtered(
                dept_id=dept["id"],
                formation_id=formation_id,
                professeur_id=prof_id
            )
        else:
            filtered_examens = []
            if formation_id is None or prof_id is None:
                st.info("Veuillez sélectionner une formation et un professeur pour voir les résultats filtrés")
        
        st.markdown("---")
        st.subheader("Résultats filtrés")
        
        if filtered_examens:
            st.dataframe(filtered_examens, use_container_width=True)
            st.info(f"Total: {len(filtered_examens)} examen(s) trouvé(s)")
        else:
            st.info("Aucun examen ne correspond aux critères sélectionnés")
    else:
        st.warning("Aucun département disponible")


# ======================
# PROFESSEUR PAGES
# ======================
def professeur_my_exams():
    """Professeur page showing their assigned exams."""
    st.header("📋 Mes examens")
    st.markdown("---")
    
    # Defensive check: ensure linked_id exists
    professeur_id = st.session_state.get('linked_id')
    
    if professeur_id is None:
        st.error("❌ Erreur: Aucun professeur associé à ce compte. Veuillez contacter l'administrateur.")
        return
    
    st.info("Vous pouvez consulter uniquement les examens qui vous sont assignés.")
    
    examens = get_examens_by_professeur(professeur_id)
    
    if examens:
        # Ensure department column exists
        for exam in examens:
            if 'departement' not in exam:
                exam['departement'] = 'N/A'
        
        st.dataframe(examens, use_container_width=True)
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total examens", len(examens))
        with col2:
            # Count unique dates
            dates = set(exam['date'] for exam in examens)
            st.metric("Jours d'examens", len(dates))
        with col3:
            # Count unique modules
            modules = set(exam['module'] for exam in examens)
            st.metric("Modules", len(modules))
    else:
        st.info("📭 Aucun examen assigné pour le moment")


def professeur_schedule():
    """Professeur page showing their exam schedule."""
    st.header("📅 Mon emploi du temps")
    st.markdown("---")
    
    professeur_id = st.session_state.get('linked_id')
    
    if professeur_id is None:
        st.error("❌ Erreur: Aucun professeur associé à ce compte.")
        return
    
    examens = get_examens_by_professeur(professeur_id)
    
    if examens:
        # Group by date
        from collections import defaultdict
        exams_by_date = defaultdict(list)
        for exam in examens:
            exams_by_date[exam['date']].append(exam)
        
        # Display schedule
        for date in sorted(exams_by_date.keys()):
            with st.expander(f"📅 {date} ({len(exams_by_date[date])} examen(s))"):
                for exam in sorted(exams_by_date[date], key=lambda x: x['heure_debut']):
                    departement = exam.get('departement', 'N/A')
                    st.write(f"**{exam['heure_debut']}** - {exam['module']} | Département: {departement} | Salle: {exam['salle']} | Durée: {exam['duree_minutes']} min")
    else:
        st.info("📭 Aucun examen programmé")


# ======================
# ETUDIANT PAGES
# ======================
def etudiant_my_schedule():
    """Etudiant page showing their exam schedule."""
    st.header("📅 Mon emploi du temps des examens")
    st.markdown("---")
    
    # Defensive check: ensure linked_id exists
    etudiant_id = st.session_state.get('linked_id')
    
    if etudiant_id is None:
        st.error("❌ Erreur: Aucun étudiant associé à ce compte. Veuillez contacter l'administrateur.")
        return
    
    # Get student information
    etudiant_info = get_etudiant_info(etudiant_id)
    
    if etudiant_info:
        # Display student information
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Nom complet:** {etudiant_info.get('full_name', 'N/A')}")
        with col2:
            st.write(f"**Formation:** {etudiant_info.get('formation', 'N/A')}")
        with col3:
            st.write(f"**Département:** {etudiant_info.get('departement', 'N/A')}")
        st.markdown("---")
    
    st.info("Vous pouvez consulter les examens de votre formation.")
    
    examens = get_examens_by_etudiant_formation(etudiant_id)
    
    if examens:
        # Reorder columns to show department prominently
        if examens:
            # Ensure all columns exist
            for exam in examens:
                if 'departement' not in exam:
                    exam['departement'] = 'N/A'
                if 'formation' not in exam:
                    exam['formation'] = 'N/A'
        
        st.dataframe(examens, use_container_width=True)
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total examens", len(examens))
        with col2:
            dates = set(exam['date'] for exam in examens)
            st.metric("Jours d'examens", len(dates))
        with col3:
            modules = set(exam['module'] for exam in examens)
            st.metric("Modules", len(modules))
    else:
        st.info("📭 Aucun examen programmé pour votre formation")


def etudiant_calendar():
    """Etudiant calendar view of exams."""
    st.header("📆 Vue calendrier")
    st.markdown("---")
    
    etudiant_id = st.session_state.get('linked_id')
    
    if etudiant_id is None:
        st.error("❌ Erreur: Aucun étudiant associé à ce compte.")
        return
    
    examens = get_examens_by_etudiant_formation(etudiant_id)
    
    if examens:
        # Group by date
        from collections import defaultdict
        exams_by_date = defaultdict(list)
        for exam in examens:
            exams_by_date[exam['date']].append(exam)
        
        # Display calendar view
        for date in sorted(exams_by_date.keys()):
            with st.expander(f"📅 {date} ({len(exams_by_date[date])} examen(s))"):
                for exam in sorted(exams_by_date[date], key=lambda x: x['heure_debut']):
                    formation_name = exam.get('formation', 'N/A')
                    departement_name = exam.get('departement', 'N/A')
                    st.write(f"""
                    **🕐 {exam['heure_debut']}**  
                    **Module:** {exam['module']}  
                    **Formation:** {formation_name}  
                    **Département:** {departement_name}  
                    **Salle:** {exam['salle']}  
                    **Professeur:** {exam['professeur']}  
                    **Durée:** {exam['duree_minutes']} minutes
                    """)
                    st.markdown("---")
    else:
        st.info("📭 Aucun examen programmé")


# ======================
# MAIN APPLICATION LOGIC
# ======================
def main():
    """
    Main application entry point.
    Routes users to appropriate interface based on authentication status and role.
    """
    # Check authentication
    if not st.session_state.authenticated:
        show_login_page()
        return
    
    # Defensive check: ensure role exists and is valid
    role = st.session_state.get('role')
    
    if role is None or role not in ['admin', 'professeur', 'etudiant']:
        st.error("❌ Rôle utilisateur invalide ou manquant. Veuillez vous reconnecter.")
        if st.button("Déconnexion"):
            logout()
        return
    
    # Render sidebar (always visible when authenticated)
    render_sidebar()
    
    # Route to role-based pages (with defensive check)
    current_page = st.session_state.get('current_page')
    
    # Set default page if not set
    if current_page is None:
        if role == 'admin':
            st.session_state.current_page = 'dashboard'
        elif role == 'professeur':
            st.session_state.current_page = 'my_exams'
        elif role == 'etudiant':
            st.session_state.current_page = 'my_schedule'
        current_page = st.session_state.current_page
    
    # Display appropriate page based on role and selection
    if role == 'admin':
        if current_page == 'dashboard':
            admin_dashboard()
        elif current_page == 'manage_exams':
            admin_manage_exams()
        elif current_page == 'scheduling':
            admin_scheduling()
        elif current_page == 'analytics':
            admin_analytics()
        else:
            admin_dashboard()  # Default fallback
    
    elif role == 'professeur':
        if current_page == 'my_exams':
            professeur_my_exams()
        elif current_page == 'schedule':
            professeur_schedule()
        else:
            professeur_my_exams()  # Default fallback
    
    elif role == 'etudiant':
        if current_page == 'my_schedule':
            etudiant_my_schedule()
        elif current_page == 'calendar':
            etudiant_calendar()
        else:
            etudiant_my_schedule()  # Default fallback


# Run main application
if __name__ == "__main__":
    main()

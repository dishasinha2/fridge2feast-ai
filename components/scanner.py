"""Scanner Component with Gemini Vision & Review Workflow."""
import logging
import time
import streamlit as st
from services.vision_service import analyze_fridge_image
from services.kitchen_service import batch_add_ingredients
from utils.validation import VALID_CATEGORIES, VALID_UNITS, validate_detected_ingredient

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def confirm_scan_items(user_id: int, reviewed_items: list[dict]) -> tuple[list, list[dict]]:
    """Persist only validated, user-reviewed scan items and build recipe handoff data."""
    validated_items = []
    for item in reviewed_items:
        is_valid, normalized, _ = validate_detected_ingredient(item)
        if not is_valid:
            return [], []
        validated_items.append(normalized)

    added = batch_add_ingredients(user_id, validated_items)
    handoff = [
        {"id": item.id, "name": item.name, "quantity": item.quantity,
         "unit": item.unit, "freshness_status": item.freshness_status,
         "days_remaining": item.days_remaining, "expiry_date": item.expiry_date}
        for item in added
    ]
    return added, handoff

def render_scanner():
    """Render the Refrigerator & Pantry Scanner with Gemini Vision and User Review."""
    user = st.session_state.authenticated_user
    if not user:
        st.session_state.current_page = "landing"
        st.rerun()

    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="font-family: 'Playfair Display', Georgia, serif; font-size: 2.4rem; color: #2D3425; margin-bottom: 0.2rem; font-style: italic;">
                📷 Refrigerator & Pantry Scanner
            </h1>
            <p style="font-size: 1.05rem; color: #5A644D; margin: 0;">
                Snap or upload a photo of your fridge or pantry. Gemini AI will identify food items and estimate freshness shelf-life.
            </p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Back to dashboard", icon=":material/home:", width="content"):
        st.session_state.current_page = "dashboard"
        st.rerun()

    # If pending items exist, show Review & Confirmation Screen
    if st.session_state.pending_scan_items is not None:
        render_review_screen(user.id)
        return

    # Scanner input tabs
    tab_upload, tab_camera = st.tabs(["📁 Upload Photo", "📷 Take Photo with Camera"])

    image_bytes = None
    filename = ""
    mime_type = ""

    with tab_upload:
        uploaded_file = st.file_uploader(
            "Choose a refrigerator or pantry photo (JPG, PNG, WEBP — Max 10MB)",
            type=["jpg", "jpeg", "png", "webp"],
            help="Upload a clear photo of your fridge shelves, crisper drawer, or pantry."
        )
        if uploaded_file is not None:
            extraction_started = time.perf_counter()
            logger.info("Scanner received upload mime_type=%s", uploaded_file.type or "unknown")
            image_bytes = uploaded_file.getvalue()
            filename = uploaded_file.name
            mime_type = uploaded_file.type
            logger.info(
                "Scanner image byte extraction completed duration_ms=%d byte_count=%d mime_type=%s",
                (time.perf_counter() - extraction_started) * 1000,
                len(image_bytes),
                mime_type or "unknown",
            )
            st.image(image_bytes, caption="Uploaded Photo Preview", width="stretch")

    with tab_camera:
        camera_file = st.camera_input("Take a photo of your fridge")
        if camera_file is not None:
            extraction_started = time.perf_counter()
            logger.info("Scanner received camera image mime_type=image/jpeg")
            image_bytes = camera_file.getvalue()
            filename = "camera_snapshot.jpg"
            mime_type = "image/jpeg"
            logger.info(
                "Scanner image byte extraction completed duration_ms=%d byte_count=%d mime_type=%s",
                (time.perf_counter() - extraction_started) * 1000,
                len(image_bytes),
                mime_type,
            )

    if image_bytes:
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        if st.button("✨ Analyze with Gemini Vision", type="primary", width="stretch"):
            with st.spinner("Preparing photo and identifying ingredients..."):
                scan_started = time.perf_counter()
                success, items, err_msg = analyze_fridge_image(image_bytes, filename, mime_type)
                logger.info(
                    "Scanner vision result returned duration_ms=%d success=%s item_count=%d",
                    (time.perf_counter() - scan_started) * 1000,
                    success,
                    len(items),
                )
                if not success:
                    st.error(err_msg)
                else:
                    st.session_state.latest_scan = items
                    st.session_state.scan_confirmed = False
                    st.session_state.pending_scan_items = items
                    st.success(f"Detected {len(items)} ingredients! Please review before saving.")
                    st.rerun()

def render_review_screen(user_id: int):
    """Render the user review and batch confirmation screen."""
    items = st.session_state.pending_scan_items or []

    st.markdown("""
        <div style="background: #FFFFFF; border: 1px solid #EAE4D5; border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem;">
            <h3 style="font-family: 'Playfair Display', serif; color: #2D3425; margin: 0 0 0.5rem 0;">
                📝 Review Detected Ingredients
            </h3>
            <p style="color: #68735A; font-size: 0.95rem; margin: 0;">
                Review each recognized item below. You can adjust quantities, categories, or shelf-life before confirming.
            </p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Back to dashboard", icon=":material/home:", width="content", key="review_back_dashboard"):
        st.session_state.pending_scan_items = None
        st.session_state.current_page = "dashboard"
        st.rerun()

    if not items:
        st.info("No items in review batch.")
        if st.button("Return to Scanner"):
            st.session_state.pending_scan_items = None
            st.rerun()
        return

    updated_items = []
    items_to_remove = []

    for idx, item in enumerate(items):
        with st.container():
            c1, c2, c3, c4, c5, c6 = st.columns([2.2, 1.5, 1.0, 1.2, 1.5, 0.6])
            
            with c1:
                name = st.text_input(f"Item #{idx+1}", value=item.get("name", ""), key=f"rev_name_{idx}")
            with c2:
                cat = st.selectbox("Category", VALID_CATEGORIES, index=VALID_CATEGORIES.index(item.get("category", "Produce")) if item.get("category") in VALID_CATEGORIES else 0, key=f"rev_cat_{idx}")
            with c3:
                qty = st.number_input("Qty", min_value=0.1, value=float(item.get("quantity", item.get("estimated_quantity", 1))), step=0.5, key=f"rev_qty_{idx}")
            with c4:
                unit = st.selectbox("Unit", VALID_UNITS, index=VALID_UNITS.index(item.get("unit", "pcs")) if item.get("unit") in VALID_UNITS else 0, key=f"rev_unit_{idx}")
            with c5:
                shelf = st.number_input("Days Left", min_value=0, max_value=365, value=int(item.get("estimated_shelf_life_days", 5)), key=f"rev_shelf_{idx}")
            with c6:
                st.markdown("<div style='height: 1.75rem;'></div>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_rev_{idx}", help="Remove this item"):
                    items_to_remove.append(idx)

            updated_items.append({
                "name": name,
                "category": cat,
                "quantity": qty,
                "unit": unit,
                "estimated_shelf_life_days": shelf,
                "storage_advice": item.get("storage_advice", "Store properly in refrigerator."),
                "confidence": item.get("confidence", 0.95)
            })

    # Filter removed items
    if items_to_remove:
        st.session_state.pending_scan_items = [item for i, item in enumerate(updated_items) if i not in items_to_remove]
        st.rerun()

    # Option to add a missing ingredient to this batch
    with st.expander("➕ Add an ingredient missed in the scan"):
        ac1, ac2, ac3, ac4 = st.columns(4)
        with ac1:
            m_name = st.text_input("Ingredient Name", key="m_add_name")
        with ac2:
            m_cat = st.selectbox("Category", VALID_CATEGORIES, key="m_add_cat")
        with ac3:
            m_qty = st.number_input("Quantity", min_value=0.5, value=1.0, step=0.5, key="m_add_qty")
        with ac4:
            m_unit = st.selectbox("Unit", VALID_UNITS, key="m_add_unit")
        
        if st.button("Add to Review Batch"):
            if m_name.strip():
                updated_items.append({
                    "name": m_name.strip(),
                    "category": m_cat,
                    "quantity": m_qty,
                    "unit": m_unit,
                    "estimated_shelf_life_days": 5,
                    "storage_advice": "Store in refrigerator.",
                    "confidence": 1.0
                })
                st.session_state.pending_scan_items = updated_items
                st.rerun()

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    col_save, col_cancel = st.columns([2, 1])
    with col_save:
        if st.button("✅ Confirm & Save All to My Kitchen", type="primary", width="stretch"):
            added, handoff = confirm_scan_items(user_id, updated_items)
            st.session_state.pending_scan_items = None
            if not added:
                st.error("No ingredients could be saved. Please review the scan and try again.")
                return
            st.session_state.last_scan_ingredients = handoff
            st.session_state.latest_scan = st.session_state.last_scan_ingredients
            st.session_state.scan_confirmed = True
            st.session_state.generated_recipe = None
            st.session_state.recipe_flow_stage = "scan_complete"
            st.session_state.current_page = "recipes"
            st.rerun()

    with col_cancel:
        if st.button("❌ Cancel Scan", width="stretch"):
            st.session_state.pending_scan_items = None
            st.rerun()

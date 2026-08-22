import io
import streamlit as st
from PIL import Image
from services.vision_service import analyze_fridge_image
from services.gemini_client import GeminiServiceException

def render_scanner_component():
    """
    Renders the private fridge scanner with live camera and image upload.
    All images are processed strictly in-memory (never written to disk).
    Keeps uploaded images in memory and shows only friendly consumer messages.
    """
    st.markdown("<h2 style='color: #ffffff; font-weight: 900;'>What's in your fridge?</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color: #94a3b8; font-size: 14px; margin-bottom: 20px;'>"
        "Take a photo and we'll identify the ingredients you can cook with."
        "</p>",
        unsafe_allow_html=True
    )

    # Food safety disclosure
    st.markdown(
        """
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid #334155; border-radius: 12px; padding: 12px 16px; margin-bottom: 20px;">
            <span style="font-size: 12px; color: #fbbf24; font-weight: 800;">⚠️ Food Safety & AI Estimation Notice:</span>
            <p style="font-size: 12px; color: #94a3b8; margin: 4px 0 0 0; line-height: 1.4;">
                Visual AI cannot reliably determine food microbiological safety, bacterial presence, or exact expiry. Always check physical aroma, storage conditions, packaging use-by dates, and official food safety guidelines.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Upload or capture your fridge image")

    # Load in-memory cached image if present
    cached_image_bytes = st.session_state.get("scanner_in_memory_image")
    cached_image_mime = st.session_state.get("scanner_in_memory_mime", "image/jpeg")

    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Fridge Photo",
            type=["jpg", "jpeg", "png", "webp"],
            help="Select an image file of your open fridge or food items."
        )
        if uploaded_file is not None:
            new_bytes = uploaded_file.getvalue()
            if new_bytes != cached_image_bytes:
                st.session_state.scanner_in_memory_image = new_bytes
                st.session_state.scanner_in_memory_mime = uploaded_file.type or "image/jpeg"
                st.session_state.scanner_status = "idle"
                st.session_state.scanner_error_message = None

    with col2:
        camera_file = st.camera_input("Take Photo of Fridge")
        if camera_file is not None:
            new_bytes = camera_file.getvalue()
            if new_bytes != cached_image_bytes:
                st.session_state.scanner_in_memory_image = new_bytes
                st.session_state.scanner_in_memory_mime = "image/jpeg"
                st.session_state.scanner_status = "idle"
                st.session_state.scanner_error_message = None

    current_bytes = st.session_state.get("scanner_in_memory_image")
    current_mime = st.session_state.get("scanner_in_memory_mime", "image/jpeg")

    if current_bytes is not None:
        try:
            image_preview = Image.open(io.BytesIO(current_bytes))
        except Exception:
            image_preview = None

        if image_preview is not None:
            st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)
            pcol1, pcol2 = st.columns([1, 2])
            with pcol1:
                st.image(image_preview, caption="Ready to review", width="stretch")
            with pcol2:
                st.markdown("#### Image ready for analysis")
                st.write("We’ll identify food items, categories, and estimated quantities for you to confirm.")

                # If previous scan failed, show the error card
                if st.session_state.get("scanner_status") == "failed":
                    error_msg = st.session_state.get("scanner_error_message") or "The AI service is experiencing high demand.\nYour image was not processed."
                    
                    st.markdown(
                        f"""
                        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.35); border-radius: 14px; padding: 18px 20px; margin-bottom: 16px;">
                            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                                <span style="font-size: 20px;">✨</span>
                                <span style="color: #f87171; font-weight: 800; font-size: 15px;">We couldn't analyse that image</span>
                            </div>
                            <p style="color: #cbd5e1; font-size: 13px; margin: 0; line-height: 1.5; white-space: pre-line;">
                                {error_msg}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    if st.button("Try again", key="scanner_retry_btn", type="primary", width="stretch"):
                        _run_fridge_analysis(current_bytes, current_mime)

                else:
                    if st.button("Analyse my fridge", key="scanner_scan_btn", type="primary", width="stretch"):
                        _run_fridge_analysis(current_bytes, current_mime)
        else:
            st.error("This image could not be decoded. Please upload another photo.")

def _run_fridge_analysis(image_bytes: bytes, mime_type: str):
    """
    Executes in-memory Gemini analysis with spinner and error capture.
    """
    with st.spinner("Analysing your ingredients…"):
        try:
            results = analyze_fridge_image(image_bytes, mime_type=mime_type)
            detected = results.get("ingredients", [])
            st.session_state.detected_ingredients = detected
            st.session_state.uncertain_items = results.get("uncertain_items", [])
            st.session_state.non_food_items = results.get("non_food_items_detected", [])
            st.session_state.vision_summary = results.get("summary", "")
            st.session_state.is_food_image = results.get("is_food_image", False)
            st.session_state.scanner_status = "success"
            st.session_state.scanner_error_message = None
            
            # Record initial detected count for HITL audit
            st.session_state.hitl_vision_audit = {
                "initial_detected_count": len(detected),
                "confirmed_count": len(detected),
                "edited_count": 0,
                "removed_count": 0,
                "added_count": 0,
                "raw_detected_names": [i["name"] for i in detected],
            }
            
            if not results.get("is_food_image", False):
                st.session_state.scanner_status = "success"
                st.warning("Please upload a clear photo of your fridge or food ingredients.")
            else:
                st.success(f"Analysis complete. Detected {len(detected)} food items.")
            st.session_state.active_tab = "Inventory"
            st.rerun()

        except GeminiServiceException as gse:
            st.session_state.scanner_status = "failed"
            st.session_state.scanner_error_message = gse.user_message
            st.session_state.scanner_is_transient_error = gse.is_transient
            st.rerun()

        except Exception as err:
            st.session_state.scanner_status = "failed"
            st.session_state.scanner_error_message = "The AI service is experiencing high demand.\nYour image was not processed."
            st.session_state.scanner_is_transient_error = True
            st.rerun()

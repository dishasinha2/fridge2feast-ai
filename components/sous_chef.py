import streamlit as st
from services.sous_chef_service import ask_sous_chef

def render_sous_chef_component():
    """
    Renders the Contextual AI Sous-Chef chat assistant.
    """
    recipe = st.session_state.get("selected_recipe")
    preferences = st.session_state.get("preferences", {})

    st.markdown("<h2 style='color: #ffffff; font-weight: 900;'>👨‍🍳 Contextual AI Sous-Chef</h2>", unsafe_allow_html=True)
    
    if recipe:
        st.markdown(f"<p style='color: #94a3b8;'>Active Recipe Context: <strong style='color: #10b981;'>{recipe.get('title')}</strong></p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color: #94a3b8;'>Ask any culinary, substitution, or technique question!</p>", unsafe_allow_html=True)

    # Initialize chat history
    if "sous_chef_messages" not in st.session_state:
        st.session_state.sous_chef_messages = [
            {
                "role": "assistant",
                "content": "Hello Chef! I am your AI Sous-Chef. Ask me for substitutions, dietary adjustments, cooking techniques, or wine pairings!"
            }
        ]

    # Quick Action Prompt Chips
    st.markdown("<p style='color: #94a3b8; font-size: 13px; font-weight: 700; margin-bottom: 8px;'>QUICK SUGGESTED QUESTIONS:</p>", unsafe_allow_html=True)
    qcol1, qcol2, qcol3, qcol4 = st.columns(4)

    prompt_to_send = None

    with qcol1:
        if st.button("🔄 Ingredient Substitutions", key="sc_chip_sub", width="stretch"):
            prompt_to_send = "What ingredient substitutions can I use if I am missing some items in this recipe?"
    with qcol2:
        if st.button("🌱 Make It Vegan", key="sc_chip_vegan", width="stretch"):
            prompt_to_send = "How can I easily adapt this recipe to be 100% vegan?"
    with qcol3:
        if st.button("⚡ Reduce Cooking Time", key="sc_chip_time", width="stretch"):
            prompt_to_send = "What shortcuts can I take to cut 10 minutes off the cooking time?"
    with qcol4:
        if st.button("🌶️ Adjust Spice Level", key="sc_chip_spice", width="stretch"):
            prompt_to_send = "How do I tone down or increase the spice level without ruining the balance?"

    st.markdown("<hr style='border-color: #334155; margin: 15px 0;'>", unsafe_allow_html=True)

    # Render Chat History
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.sous_chef_messages:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="👨‍🍳"):
                    st.write(msg["content"])

    # Chat Input
    user_input = st.chat_input("Ask your AI Sous-Chef a question...")

    if user_input or prompt_to_send:
        question = user_input or prompt_to_send
        
        # Append User Message
        st.session_state.sous_chef_messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        # Call Gemini AI Sous-Chef
        with st.chat_message("assistant", avatar="👨‍🍳"):
            with st.spinner("AI Sous-Chef is thinking..."):
                try:
                    answer = ask_sous_chef(recipe, preferences, question)
                    st.write(answer)
                    st.session_state.sous_chef_messages.append({"role": "assistant", "content": answer})
                except Exception as err:
                    error_msg = f"Sorry, I encountered an issue: {str(err)}"
                    st.error(error_msg)
                    st.session_state.sous_chef_messages.append({"role": "assistant", "content": error_msg})

        st.rerun()

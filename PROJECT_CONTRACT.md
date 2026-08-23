# PROJECT CONTRACT: FRIDGE2FEAST AI
**"Turn What's Left Into What's Next"**

Treat this document as an immutable contract for all future changes.

## 1. Immutable Rules
1. **Python + Streamlit only**: The application frontend AND backend must be implemented purely in Python.
2. **No React**: Zero React libraries, components, or JSX.
3. **No TypeScript**: Zero TypeScript configuration, declarations, or files.
4. **No Vite**: Zero Vite build tooling or bundling configurations.
5. **No Node.js frontend**: Zero Node.js servers, npm scripts, or package managers.
6. **No hardcoded production data**: Never hardcode demo counts, fake testimonials, or placeholder ingredients.
7. **All user data must come from authenticated user records**: Calculated dynamically from the database.
8. **All user-owned data must be isolated by user_id**: Zero cross-user data leakage.
9. **Gemini handles AI tasks; Python handles deterministic business logic**: Deterministic rules govern shelf life, freshness calculations, and database mutations.
10. **No secrets in source code**: All API credentials and salts must be stored in environment variables or handled securely without UI exposure.
11. **No fake/demo users**: No pre-seeded accounts in production UI.
12. **No fake dashboard metrics**: Zero-waste scores and counts must reflect actual pantry state.
13. **No fake ingredients or recipes**: Ingredients in recipes must explicitly differentiate available items from staples needed.
14. **Landing → Login/Signup → Dashboard is mandatory**: Unauthenticated users cannot view private sections.
15. **Production UI must remain minimal and user-centric**: Premium, warm, kitchen-focused editorial aesthetic without clutter.

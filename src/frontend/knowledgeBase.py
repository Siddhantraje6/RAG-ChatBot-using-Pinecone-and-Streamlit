import streamlit as st
import requests

# --- Page Configuration ---
st.set_page_config(page_title="Knowledge Base", page_icon="💬")
st.title("View Knowledge Base (Uploaded Files) of :blue[Diploma AI]")

BASE_URL = "http://localhost:8000"


# -----------------------------
# Fetch knowledge base list
# -----------------------------
def fetch_knowledge_base():
    try:
        res = requests.get(f"{BASE_URL}/knowledge_base")
        if res.status_code == 200:
            return res.json().get("knowledge_base_list", [])
        return []
    except Exception:
        st.error("❌ Error fetching knowledge base.")
        return []


# -----------------------------
# Delete knowledge base entry
# -----------------------------
def delete_knowledge_item(item_id):
    try:
        res = requests.delete(f"{BASE_URL}/knowledge_base/{item_id}")
        if res.status_code == 200:
            return True, res.json().get("message", "Deleted")
        return False, "Failed to delete"
    except Exception as e:
        return False, str(e)


# -----------------------------
# Main UI
# -----------------------------
knowledge_list = fetch_knowledge_base()

if not knowledge_list:
    st.info("No knowledge base uploaded yet.")
else:
    st.subheader("📚 Uploaded Knowledge Base")

    # Track which card's delete popup is open
    if "confirm_delete" not in st.session_state:
        st.session_state.confirm_delete = None

    for item in knowledge_list:
        kb_id = item["knowledge_base_id"]
        kb_name = item["knowledge_base_name"]
        kb_content = item["content"]
        created_at = item.get("created_at", "")

        with st.container(border=True):
            cols = st.columns([5, 1])

            # Left block: Title + timestamp
            with cols[0]:
                st.markdown(f"### {kb_name}")
                st.caption(f"Created at: {created_at}")

            # Right block: Delete button
            with cols[1]:
                if st.button("🗑️ Delete", key=f"delete_btn_{kb_id}"):
                    st.session_state.confirm_delete = kb_id

            # Inline delete confirmation UI (Option 1)
            if st.session_state.confirm_delete == kb_id:
                st.warning(f"Are you sure you want to delete **{kb_name}**?")
                c1, c2 = st.columns(2)

                with c1:
                    if st.button("✔️ Yes, Delete", key=f"confirm_yes_{kb_id}"):
                        success, msg = delete_knowledge_item(kb_id)
                        if success:
                            st.success(msg)
                            st.session_state.confirm_delete = None
                            st.rerun()
                        else:
                            st.error(msg)

                with c2:
                    if st.button("❌ Cancel", key=f"confirm_no_{kb_id}"):
                        st.session_state.confirm_delete = None

            # Content expander
            with st.expander("📄 View Content"):
                st.text_area(
                    label="Extracted Content",
                    value=kb_content,
                    height=200,
                    disabled=True
                )

            st.divider()

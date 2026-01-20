import streamlit as st
import fitz  # PyMuPDF
import io

# --- ⚙️ PRECISE ALIGNMENT SETTINGS ---
# We use 'TnC Engg' as the anchor.

# 1. Signature Settings
# We move it slightly down from 'TnC Engg' to land in the SIGNATURE row.
SIGN_OFFSET_X = -5        # Slight shift to the right
SIGN_OFFSET_Y = 4       # Reduced to move it UP into the cell
SIGN_WIDTH = 35          # Smaller size as requested
SIGN_HEIGHT = 18         # Smaller size as requested

# 2. Stamp Settings
# We want the stamp to sit higher up, overlapping the text and sign.
STAMP_OFFSET_X = 28     # Move LEFT to center it more on the column
STAMP_OFFSET_Y = -25     # Move UP significantly to bring it onto the table
STAMP_WIDTH = 60         # Slightly smaller to fit the table better
STAMP_HEIGHT = 60

def add_sign_and_stamp(input_pdf_bytes, sign_img_path, stamp_img_path):
    doc = fitz.open(stream=input_pdf_bytes, filetype="pdf")
    search_term = ["TnC Engg", "TnC Engineer"]
    found_locations = 0

    for page in doc:
        text_instances = page.search_for(search_term)
        for rect in text_instances:
            found_locations += 1
            
            # --- Signature Logic ---
            # rect.x0 is left of text, rect.y1 is bottom of text
            s_x = rect.x0 + SIGN_OFFSET_X
            s_y = rect.y1 + SIGN_OFFSET_Y
            sign_rect = fitz.Rect(s_x, s_y, s_x + SIGN_WIDTH, s_y + SIGN_HEIGHT)
            
            # --- Stamp Logic ---
            # We position the stamp relative to the same anchor
            m_x = rect.x0 + STAMP_OFFSET_X
            m_y = rect.y1 + STAMP_OFFSET_Y
            stamp_rect = fitz.Rect(m_x, m_y, m_x + STAMP_WIDTH, m_y + STAMP_HEIGHT)
            
            # Insert Signature First
            page.insert_image(sign_rect, filename=sign_img_path)
            
            # Insert Stamp Second (so it overlaps on top)
            page.insert_image(stamp_rect, filename=stamp_img_path)

    output_buffer = io.BytesIO()
    doc.save(output_buffer)
    doc.close()
    return output_buffer.getvalue(), found_locations

# --- WEB PAGE ---
st.set_page_config(page_title="PDF Auto-Stamp", page_icon="📝")
st.title("🚀 Company PDF Stamper")

uploaded_file = st.file_uploader("Upload the Report (PDF)", type="pdf")

if uploaded_file:
    if st.button("Apply Seal & Sign"):
        with st.spinner("Processing..."):
            try:
                pdf_data, count = add_sign_and_stamp(uploaded_file.read(), "sign.png", "stamp.png")
                
                if count > 0:
                    st.success(f"Aligned and stamped {count} location(s).")
                    st.download_button("⬇️ Download Result", pdf_data, "Stamped_Report.pdf", "application/pdf")
                else:
                    st.error(f"Search text 'TnC Engg' not found.")
            except Exception as e:

                st.error(f"Error: {e}")

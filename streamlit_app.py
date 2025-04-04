import streamlit as st
import pdfplumber
import pandas as pd
import base64

# Set page config
st.set_page_config(page_title="PDF Text & Table Extractor", layout="wide")

# Sidebar - File upload
st.sidebar.title("Upload PDF")
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type=["pdf"])

# Sidebar - PDF Page selection option
page_selection = st.sidebar.radio("Select pages to process:", ["All Pages", "Specific Page"])

selected_page = None
if page_selection == "Specific Page":
    selected_page = st.sidebar.number_input("Enter page number (starting from 1):", min_value=1, step=1)

# Main App Title
st.title("PDF Text & Table Extractor")

if uploaded_file is not None:
    # Display uploaded PDF
    st.header("PDF Viewer")
    pdf_bytes = uploaded_file.read()
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

    # Reset file pointer after read()
    uploaded_file.seek(0)

    # Extract content using pdfplumber
    extracted_text = ""
    tables = []

    with pdfplumber.open(uploaded_file) as pdf:
        if selected_page and page_selection == "Specific Page":
            pages = [pdf.pages[selected_page - 1]] if selected_page <= len(pdf.pages) else []
        else:
            pages = pdf.pages

        for page in pages:
            # Extract text
            text = page.extract_text()
            if text:
                extracted_text += text + "\n\n"

            # Extract tables
            page_tables = page.extract_tables()
            for table in page_tables:
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0]) if len(table) > 1 else pd.DataFrame(table)
                    tables.append(df)

    # Display extracted text in Markdown format
    st.header("Extracted Text")
    if extracted_text.strip():
        with st.expander("Click to view extracted text"):
            st.markdown(extracted_text.replace('\n', '  \n')) # proper markdown line breaks
    else:
        st.warning("No text could be extracted from this PDF.")

    # Export extracted text as markdown file
    st.download_button(
        label="Download Text as Markdown",
        data=extracted_text,
        file_name='extracted_text.md',
        mime='text/markdown'
    )

    # Display tables if available
    st.header("Extracted Tables")
    if tables:
        for idx, table_df in enumerate(tables):
            st.subheader(f"Table {idx + 1}")
            st.dataframe(table_df)

            # Show markdown representation of the table
            with st.expander(f"View Markdown for Table {idx + 1}"):
                st.markdown(table_df.to_markdown(index=False))
    else:
        st.warning("No tables found in this PDF.")

else:
    st.info("👈 Please upload a PDF file using the sidebar.")

# Additional useful functionality (suggestions):
# - Add OCR support using pytesseract for scanned PDFs.
# - Include options to extract images from PDFs.
# - Allow users to specify table extraction parameters (e.g., vertical/horizontal lines).

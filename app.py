import streamlit as st
from markitdown import MarkItDown
import tempfile
import os

# 1. Configuração da página
st.set_page_config(
    page_title="Conversor Markdown",
    page_icon="📝",
    layout="centered"
)

# 2. Injeção de CSS personalizado (Tema Escuro no Estilo GitHub)
st.markdown("""
    <style>
    /* Fundo da aplicação */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Fontes e Títulos */
    h1, h2, h3, h4, label {
        color: #f0f6fc !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Estilização dos blocos expansíveis e cards */
    .stDetails {
        background-color: #161b22;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }

    /* Área de Upload */
    div[data-testid="stFileUploader"] {
        background-color: #161b22;
        border: 1px dashed #30363d;
        border-radius: 8px;
        padding: 15px;
    }

    /* Botão Primário (Estilo GitHub Green) */
    .stButton>button {
        background-color: #238636 !important;
        color: #ffffff !important;
        border: 1px solid rgba(240,246,252,0.1) !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    .stButton>button:hover {
        background-color: #2ea043 !important;
    }

    /* Badges para extensões de arquivo */
    .badge {
        background-color: #21262d;
        border: 1px solid #30363d;
        color: #79c0ff;
        font-size: 0.8rem;
        padding: 2px 8px;
        border-radius: 12px;
        font-family: monospace;
        margin-right: 4px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📝 Conversor para Markdown (.md)")
st.caption("Powered by Microsoft MarkItDown")

# Seção de formatos suportados com Badges estilizadas
with st.expander("📂 Formatos de arquivos suportados"):
    st.markdown("""
    * **Documentos:** <span class="badge">.pdf</span> <span class="badge">.docx</span> <span class="badge">.pptx</span>
    * **Planilhas & Dados:** <span class="badge">.xlsx</span> <span class="badge">.xls</span> <span class="badge">.csv</span> <span class="badge">.json</span> <span class="badge">.xml</span>
    * **Web & Texto:** <span class="badge">.html</span> <span class="badge">.txt</span>
    * **Mídias:** <span class="badge">.png</span> <span class="badge">.jpg</span> <span class="badge">.mp3</span> <span class="badge">.wav</span>
    * **Compactados:** <span class="badge">.zip</span>
    """, unsafe_allow_html=True)

# Upload de arquivo
uploaded_file = st.file_uploader(
    "Arraste e solte seu arquivo aqui ou clique para selecionar", 
    type=["pdf", "docx", "pptx", "xlsx", "xls", "csv", "json", "xml", "html", "txt", "zip", "png", "jpg", "mp3", "wav"]
)

if uploaded_file is not None:
    ext = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    with st.spinner("Convertendo arquivo para Markdown..."):
        try:
            md = MarkItDown()
            result = md.convert(tmp_path)
            
            st.success("Conversão concluída!")
            st.text_area("Resultado em Markdown:", value=result.text_content, height=350)
            
            nome_original = os.path.splitext(uploaded_file.name)[0]
            st.download_button(
                label="📥 Baixar arquivo .md",
                data=result.text_content,
                file_name=f"{nome_original}.md",
                mime="text/markdown"
            )
        except Exception as e:
            st.error(f"Erro ao converter o arquivo: {e}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
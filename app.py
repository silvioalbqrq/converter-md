import streamlit as st
import tempfile
import os

# Importação segura do MarkItDown
try:
    from markitdown import MarkItDown
    MARKITDOWN_DISPONIVEL = True
except ImportError:
    MARKITDOWN_DISPONIVEL = False

# 1. Configuração da página
st.set_page_config(
    page_title="Conversor Markdown",
    page_icon="📝",
    layout="centered"
)

# 2. Estilização CSS em Tema Escuro (Estilo GitHub)
st.markdown("""
    <style>
    /* Fundo principal */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Fontes e Títulos */
    h1, h2, h3, h4, label {
        color: #f0f6fc !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Expander / Bloco de Informações */
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
        padding: 10px;
    }

    /* Botões Primários (Verde GitHub) */
    .stButton>button, .stDownloadButton>button {
        background-color: #238636 !important;
        color: #ffffff !important;
        border: 1px solid rgba(240,246,252,0.1) !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        width: 100%;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background-color: #2ea043 !important;
    }

    /* Badges de extensões */
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

# Exibe aviso caso a biblioteca tenha falhado na instalação
if not MARKITDOWN_DISPONIVEL:
    st.error("⚠️ A biblioteca 'markitdown' não foi encontrada. Verifique se o arquivo requirements.txt contém 'markitdown' e 'streamlit'.")

# Seção de formatos suportados
with st.expander("📂 Formatos de arquivos suportados"):
    st.markdown("""
    * **Documentos:** <span class="badge">.pdf</span> <span class="badge">.docx</span> <span class="badge">.pptx</span>
    * **Planilhas & Dados:** <span class="badge">.xlsx</span> <span class="badge">.xls</span> <span class="badge">.csv</span> <span class="badge">.json</span> <span class="badge">.xml</span>
    * **Web & Texto:** <span class="badge">.html</span> <span class="badge">.txt</span>
    * **Mídias:** <span class="badge">.png</span> <span class="badge">.jpg</span> <span class="badge">.mp3</span> <span class="badge">.wav</span>
    * **Compactados:** <span class="badge">.zip</span>
    """, unsafe_allow_html=True)

# Componente de Upload (extensões sempre em minúsculo para evitar erro no Streamlit)
extensoes_permitidas = [
    "pdf", "docx", "pptx", "xlsx", "xls", "csv", 
    "json", "xml", "html", "htm", "txt", "zip", 
    "png", "jpg", "jpeg", "mp3", "wav"
]

uploaded_file = st.file_uploader(
    "Arraste e solte seu arquivo aqui ou clique para selecionar", 
    type=extensoes_permitidas
)

if uploaded_file is not None and MARKITDOWN_DISPONIVEL:
    extensao = os.path.splitext(uploaded_file.name)[1].lower()
    
    # Criação segura do arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix=extensao) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    with st.spinner("Convertendo arquivo via Microsoft MarkItDown..."):
        try:
            md = MarkItDown()
            result = md.convert(tmp_path)
            
            st.success("Conversão concluída com sucesso!")
            
            # Exibe o resultado do texto
            st.text_area("Resultado em Markdown:", value=result.text_content, height=350)
            
            # Botão para baixar o arquivo gerado
            nome_base = os.path.splitext(uploaded_file.name)[0]
            st.download_button(
                label="📥 Baixar arquivo .md",
                data=result.text_content,
                file_name=f"{nome_base}.md",
                mime="text/markdown"
            )
        except Exception as e:
            st.error(f"Erro ao converter o arquivo: {str(e)}")
        finally:
            # Remoção do arquivo temporário do servidor
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
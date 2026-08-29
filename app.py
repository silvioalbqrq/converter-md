import streamlit as st
import tempfile
import os

try:
    from markitdown import MarkItDown
    MARKITDOWN_DISPONIVEL = True
except ImportError:
    MARKITDOWN_DISPONIVEL = False

# 1. Configuração da página e tema
st.set_page_config(
    page_title="MarkItDown Web - Conversor para Markdown",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. CSS Customizado para Dark Mode Profissional
st.markdown("""
    <style>
    /* Fundo da Aplicação */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Fontes e Títulos */
    h1, h2, h3, h4, label {
        color: #f0f6fc !important;
        font-weight: 700 !important;
    }

    /* Container de Categorias e Cards */
    .cat-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 20px;
    }

    /* Badges de extensões */
    .badge-doc { background-color: #1f6beb22; border: 1px solid #1f6beb; color: #58a6ff; font-size: 0.8rem; padding: 2px 8px; border-radius: 6px; font-family: monospace; }
    .badge-data { background-color: #23863622; border: 1px solid #238636; color: #3fb950; font-size: 0.8rem; padding: 2px 8px; border-radius: 6px; font-family: monospace; }
    .badge-web { background-color: #8957e522; border: 1px solid #8957e5; color: #bc8cff; font-size: 0.8rem; padding: 2px 8px; border-radius: 6px; font-family: monospace; }
    .badge-zip { background-color: #d2992222; border: 1px solid #d29922; color: #e3b341; font-size: 0.8rem; padding: 2px 8px; border-radius: 6px; font-family: monospace; }

    /* Área de Upload */
    div[data-testid="stFileUploader"] {
        background-color: #161b22;
        border: 1px dashed #30363d;
        border-radius: 10px;
        padding: 10px;
    }

    /* Botão Principal */
    .stButton>button, .stDownloadButton>button {
        background-color: #238636 !important;
        color: #ffffff !important;
        border: 1px solid rgba(240,246,252,0.1) !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        width: 100%;
        transition: all 0.2s ease;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background-color: #2ea043 !important;
        transform: translateY(-1px);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Cabeçalho e contexto
st.title("📝 Conversor para Markdown (.md)")
st.caption("⚡ Powered by **Microsoft MarkItDown Engine**")

st.info("Este conversor transforma documentos, planilhas e arquivos web em código Markdown (.md) limpo e estruturado.")

# 4. Formatos suportados (Sem mídias)
with st.expander("📂 Categorias e Formatos Aceitos", expanded=True):
    st.markdown("""
    * 📄 **Documentos:** <span class="badge-doc">.pdf</span> <span class="badge-doc">.docx</span> <span class="badge-doc">.pptx</span>
    * 📊 **Planilhas & Dados:** <span class="badge-data">.xlsx</span> <span class="badge-data">.xls</span> <span class="badge-data">.csv</span> <span class="badge-data">.json</span> <span class="badge-data">.xml</span>
    * 🌐 **Web & Texto:** <span class="badge-web">.html</span> <span class="badge-web">.txt</span>
    * 📦 **Compactados:** <span class="badge-zip">.zip</span>
    """, unsafe_allow_html=True)

# 5. Sidebar com "Como Funciona" e Histórico
with st.sidebar:
    st.header("⚙️ Como Funciona")
    st.markdown("""
    1. **Upload:** Envie um ou mais arquivos.
    2. **Conversão:** A engine extrai o texto e preserva tabelas/listas.
    3. **Download/Cópia:** Baixe o arquivo `.md` ou copie o código direto.
    """)
    st.divider()
    st.markdown("🔗 **Links Úteis**")
    st.markdown("[Repositório no GitHub](https://github.com/silvioalbqrq/converter-md)")

# 6. Inicialização do Histórico de Conversões na Sessão
if "historico" not in st.session_state:
    st.session_state.historico = []

# 7. Componente de Upload com suporte a MÚLTIPLOS arquivos
extensoes_permitidas = [
    "pdf", "docx", "pptx", "xlsx", "xls", "csv", 
    "json", "xml", "html", "htm", "txt", "zip"
]

uploaded_files = st.file_uploader(
    "Arraste e solte seus arquivos aqui (Suporta múltiplos de uma vez)", 
    type=extensoes_permitidas,
    accept_multiple_files=True
)

if uploaded_files and MARKITDOWN_DISPONIVEL:
    md = MarkItDown()
    
    for file in uploaded_files:
        st.divider()
        st.subheader(f"📄 Arquivo: {file.name}")
        
        extensao = os.path.splitext(file.name)[1].lower()
        
        # Salvamento temporário do arquivo
        with tempfile.NamedTemporaryFile(delete=False, suffix=extensao) as tmp:
            tmp.write(file.getvalue())
            tmp_path = tmp.name

        # Feedback visual com progresso/spinner
        with st.spinner(f"Convertendo {file.name}..."):
            try:
                result = md.convert(tmp_path)
                conteudo_md = result.text_content
                
                st.success("Conversão concluída com sucesso!")
                
                # Preview do resultado
                st.text_area("Preview do Markdown gerado:", value=conteudo_md, height=250, key=f"preview_{file.name}")
                
                col1, col2 = st.columns(2)
                
                # Botão de Download
                nome_base = os.path.splitext(file.name)[0]
                with col1:
                    st.download_button(
                        label="📥 Baixar .md",
                        data=conteudo_md,
                        file_name=f"{nome_base}.md",
                        mime="text/markdown",
                        key=f"dl_{file.name}"
                    )
                
                # Armazena no Histórico da Sessão
                if file.name not in [h['nome'] for h in st.session_state.historico]:
                    st.session_state.historico.append({'nome': file.name, 'conteudo': conteudo_md})

            except Exception as e:
                st.error(f"Erro ao converter {file.name}: {str(e)}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

# Display do Histórico na Sidebar
if st.session_state.historico:
    st.sidebar.divider()
    st.sidebar.subheader("📜 Histórico da Sessão")
    for item in st.session_state.historico:
        st.sidebar.text(f"• {item['nome']}")
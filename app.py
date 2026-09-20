import streamlit as st
import tempfile
import os
import io
import zipfile
import hashlib

try:
    from markitdown import MarkItDown
    MARKITDOWN_DISPONIVEL = True
    MARKITDOWN_ERRO = ""
except ImportError as e:
    MARKITDOWN_DISPONIVEL = False
    MARKITDOWN_ERRO = str(e)

# 1. Configuração da página e tema
st.set_page_config(
    page_title="MarkItDown Web - Conversor para Markdown",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="expanded"
)

MAX_MB_POR_ARQUIVO = 50
MAX_BYTES = MAX_MB_POR_ARQUIVO * 1024 * 1024

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

    /* Texto base: garante contraste #c9d1d9 sobre #0d1117 */
    .stApp p, .stApp li, .stApp span, .stApp div,
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] li,
    div[data-testid="stMarkdownContainer"] span {
        color: #c9d1d9;
    }
    div[data-testid="stMarkdownContainer"] strong {
        color: #f0f6fc !important;
    }
    a, div[data-testid="stMarkdownContainer"] a {
        color: #58a6ff !important;
    }

    /* Sidebar: texto apagado ficava ilegível */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
        color: #c9d1d9 !important;
    }
    section[data-testid="stSidebar"] strong {
        color: #f0f6fc !important;
    }

    /* Alertas (st.info/warning/success/error): texto azul-escuro sobre fundo escuro = ilegível */
    div[data-testid="stAlert"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] span,
    div[data-testid="stAlert"] div {
        color: #f0f6fc !important;
    }
    /* Mantém a faixinha lateral colorida de cada tipo via borda esquerda */
    div[data-testid="stInfo"] { border-left: 4px solid #1f6beb !important; }
    div[data-testid="stSuccess"] { border-left: 4px solid #238636 !important; }
    div[data-testid="stWarning"] { border-left: 4px solid #d29922 !important; }
    div[data-testid="stError"] { border-left: 4px solid #f85149 !important; }

    /* Expander: header branco com texto claro = ilegível */
    details[data-testid="stExpander"],
    div[data-testid="stExpander"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary span {
        color: #f0f6fc !important;
    }
    div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background-color: #0d1117 !important;
    }

    /* Caption "Powered by...": cinza legível, não apagado */
    div[data-testid="stCaptionContainer"],
    div[data-testid="stCaptionContainer"] p,
    div[data-testid="stCaptionContainer"] span {
        color: #8b949e !important;
    }

    /* Uploader: texto auxiliar cinza-claro sobre fundo escuro */
    div[data-testid="stFileUploader"] small,
    div[data-testid="stFileUploader"] span,
    div[data-testid="stFileUploaderDropzone"] small,
    div[data-testid="stFileUploaderDropzone"] span,
    div[data-testid="stFileUploaderDropzoneInstructions"] {
        color: #8b949e !important;
    }
    div[data-testid="stFileUploaderDropzone"] button {
        color: #f0f6fc !important;
        border-color: #30363d !important;
    }

    /* Code inline (.md etc): fundo preto, texto claro */
    code {
        background-color: #010409 !important;
        color: #f0f6fc !important;
        border: 1px solid #30363d !important;
        border-radius: 4px !important;
        padding: 1px 5px !important;
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

st.info(
    "Este conversor transforma documentos, planilhas e arquivos web em código Markdown (.md) limpo e estruturado. "
    f"Limite de **{MAX_MB_POR_ARQUIVO} MB por arquivo**. Na primeira abertura o Streamlit Cloud gratuito pode levar ~1 min (cold start)."
)

# 4. Formatos suportados (sincronizado com o uploader + landing page)
with st.expander("📂 Categorias e Formatos Aceitos", expanded=True):
    st.markdown("""
    * 📄 **Documentos:** <span class="badge-doc">.pdf</span> <span class="badge-doc">.docx</span> <span class="badge-doc">.pptx</span>
    * 📊 **Planilhas & Dados:** <span class="badge-data">.xlsx</span> <span class="badge-data">.xls</span> <span class="badge-data">.csv</span> <span class="badge-data">.json</span> <span class="badge-data">.xml</span>
    * 🌐 **Web & Texto:** <span class="badge-web">.html</span> <span class="badge-web">.htm</span> <span class="badge-web">.txt</span>
    * 📦 **Compactados:** <span class="badge-zip">.zip</span>
    """, unsafe_allow_html=True)

# 5. Sidebar com "Como Funciona" e Histórico
with st.sidebar:
    st.header("⚙️ Como Funciona")
    st.markdown("""
    1. **Upload:** Envie um ou mais arquivos (até 50 MB cada).
    2. **Conversão:** A engine extrai o texto e preserva tabelas/listas.
    3. **Download/Cópia:** Baixe o arquivo `.md` ou copie o código direto.
    """)
    st.divider()
    st.markdown("🔗 **Links Úteis**")
    st.markdown("[Repositório no GitHub](https://github.com/silvioalbqrq/converter-md)")
    st.markdown("[Landing Page](https://silvioalbqrq.github.io/converter-md/)")

# 6. Inicialização do Histórico de Conversões na Sessão
if "historico" not in st.session_state:
    st.session_state.historico = []

# Aviso crítico se a engine não instalou (antes falhava em silêncio)
if not MARKITDOWN_DISPONIVEL:
    st.error(
        "❌ Engine `markitdown` não instalada no servidor. "
        "Verifique o `requirements.txt` e faça redeploy no Streamlit Cloud."
    )
    if MARKITDOWN_ERRO:
        st.code(MARKITDOWN_ERRO)
    st.stop()


def _file_uid(file) -> str:
    """Gera chave única estável por upload (evita colisão de arquivos com mesmo nome)."""
    fid = getattr(file, "file_id", None) or getattr(file, "id", None)
    base = f"{getattr(file, 'name', 'file')}-{getattr(file, 'size', 0)}-{fid or id(file)}"
    return hashlib.md5(base.encode("utf-8")).hexdigest()[:10]


def _build_zip(historico: list) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        usados = set()
        for item in historico:
            nome_base = os.path.splitext(item["nome"])[0] or "arquivo"
            nome_md = f"{nome_base}.md"
            # Evita sobrescrever dentro do zip se houver nomes repetidos
            i = 1
            while nome_md in usados:
                i += 1
                nome_md = f"{nome_base}-{i}.md"
            usados.add(nome_md)
            zf.writestr(nome_md, item.get("conteudo", ""))
    buf.seek(0)
    return buf.getvalue()


# 7. Componente de Upload com suporte a MÚLTIPLOS arquivos
extensoes_permitidas = [
    "pdf", "docx", "pptx", "xlsx", "xls", "csv",
    "json", "xml", "html", "htm", "txt", "zip"
]

uploaded_files = st.file_uploader(
    f"Arraste e solte seus arquivos aqui (múltiplos, até {MAX_MB_POR_ARQUIVO} MB cada)",
    type=extensoes_permitidas,
    accept_multiple_files=True
)

if uploaded_files:
    md = MarkItDown()

    for file in uploaded_files:
        uid = _file_uid(file)
        tamanho = getattr(file, "size", 0) or len(file.getvalue())

        st.divider()
        st.subheader(f"📄 Arquivo: {file.name}")

        # Validação de tamanho (evita estouro de RAM no Cloud gratuito)
        if tamanho > MAX_BYTES:
            st.warning(
                f"⚠️ `{file.name}` tem {tamanho / 1024 / 1024:.1f} MB e excede o limite de "
                f"{MAX_MB_POR_ARQUIVO} MB. Divida o arquivo ou comprima antes de enviar."
            )
            continue

        extensao = os.path.splitext(file.name)[1].lower()

        # Salvamento temporário do arquivo
        with tempfile.NamedTemporaryFile(delete=False, suffix=extensao) as tmp:
            tmp.write(file.getvalue())
            tmp_path = tmp.name

        # Feedback visual com progresso/spinner
        with st.spinner(f"Convertendo {file.name}..."):
            try:
                result = md.convert(tmp_path)
                conteudo_md = result.text_content or ""

                if not conteudo_md.strip():
                    st.warning(
                        f"Nenhum texto extraído de `{file.name}`. "
                        "PDFs escaneados (só imagem, sem OCR) retornam vazio."
                    )
                    continue

                st.success("Conversão concluída com sucesso!")
                st.caption(f"{len(conteudo_md):,} caracteres · {len(conteudo_md.encode('utf-8')) / 1024:.1f} KB em Markdown")

                # Preview do resultado (key única por upload)
                st.text_area(
                    "Preview do Markdown gerado (selecione e Ctrl+C para copiar):",
                    value=conteudo_md,
                    height=250,
                    key=f"preview_{uid}",
                )

                col1, col2 = st.columns(2)

                # Botão de Download individual
                nome_base = os.path.splitext(file.name)[0]
                with col1:
                    st.download_button(
                        label="📥 Baixar .md",
                        data=conteudo_md,
                        file_name=f"{nome_base}.md",
                        mime="text/markdown",
                        key=f"dl_{uid}",
                    )
                with col2:
                    st.download_button(
                        label="📋 Baixar .txt",
                        data=conteudo_md,
                        file_name=f"{nome_base}.txt",
                        mime="text/plain",
                        key=f"txt_{uid}",
                    )

                # Armazena no Histórico da Sessão (deduplica por uid, não só por nome)
                if uid not in [h.get("uid") for h in st.session_state.historico]:
                    st.session_state.historico.append(
                        {"uid": uid, "nome": file.name, "conteudo": conteudo_md}
                    )

            except Exception as e:
                st.error(f"Erro ao converter {file.name}: {str(e)}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

# Display do Histórico na Sidebar + ações globais
if st.session_state.historico:
    st.sidebar.divider()
    st.sidebar.subheader("📜 Histórico da Sessão")
    for item in st.session_state.historico:
        kb = len(item.get("conteudo", "").encode("utf-8")) / 1024
        st.sidebar.text(f"• {item['nome']} ({kb:.0f} KB)")

    col_h1, col_h2 = st.sidebar.columns(2)
    with col_h1:
        if st.sidebar.button("🗑️ Limpar", key="btn_limpar_hist"):
            st.session_state.historico = []
            st.rerun()
    with col_h2:
        zip_bytes = _build_zip(st.session_state.historico)
        st.sidebar.download_button(
            label="📦 Tudo .zip",
            data=zip_bytes,
            file_name="conversoes_markdown.zip",
            mime="application/zip",
            key="btn_baixar_tudo",
        )

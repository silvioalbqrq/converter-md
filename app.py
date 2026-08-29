import streamlit as st
from markitdown import MarkItDown
import tempfile
import os

# Configuração da página em tema escuro
st.set_page_config(
    page_title="Conversor Markdown",
    page_icon="📝",
    layout="centered"
)

st.title("📝 Conversor para Markdown (.md)")
st.caption("Powered by Microsoft MarkItDown")

# Seção de informações dos formatos aceitos
with st.expander("📂 Formatos de arquivos suportados"):
    st.markdown("""
    * **Documentos:** PDF, Word (`.docx`), PowerPoint (`.pptx`)
    * **Planilhas & Dados:** Excel (`.xlsx`, `.xls`), CSV, JSON, XML
    * **Web & Texto:** HTML, TXT
    * **Mídias:** Imagens (PNG, JPG) e Áudio (MP3, WAV)
    * **Compactados:** Arquivos ZIP
    """)

# Campo de upload do arquivo
uploaded_file = st.file_uploader(
    "Arraste e solte o arquivo aqui ou clique para selecionar", 
    type=["pdf", "docx", "pptx", "xlsx", "xls", "csv", "json", "xml", "html", "txt", "zip", "png", "jpg", "mp3", "wav"]
)

if uploaded_file is not None:
    # Salva o arquivo temporariamente para processamento
    ext = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    with st.spinner("Convertendo arquivo para Markdown..."):
        try:
            md = MarkItDown()
            result = md.convert(tmp_path)
            
            st.success("Conversão concluída com sucesso!")
            
            # Exibe o resultado em Markdown na tela
            st.subheader("Resultado:")
            st.text_area("Texto em Markdown", value=result.text_content, height=350)
            
            # Botão para baixar o arquivo .md
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
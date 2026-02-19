import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import time
import io

# Configuração da Página
st.set_page_config(page_title="Athalaia Enriquecimento", layout="wide")

st.title("🚀 Enriquecedor Athalaia Gráfica")
st.markdown("### Inteligência Comercial para Impressão Offset")

# Sidebar - Configurações que você pode mudar na hora
with st.sidebar:
    st.header("Configurações")
    api_key = st.text_input("Sua Gemini API Key:", type="password")
    st.info("O ICP abaixo será usado para filtrar e gerar insights para esta lista específica.")
    icp_atual = st.text_area("Defina o ICP desta lista:", 
                             placeholder="Ex: Gerentes de Marketing de indústrias farmacêuticas...")

if not api_key:
    st.warning("👈 Insira sua API Key na barra lateral para começar.")
else:
    genai.configure(api_key=api_key)
    # Usando o modelo Pro para maior assertividade e menos erros
    model = genai.GenerativeModel('gemini-1.5-pro')

    # Upload do arquivo
    uploaded_file = st.file_uploader("Importar planilha (CSV ou XLSX)", type=['csv', 'xlsx'])

    if uploaded_file:
        # Carregar os dados
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        
        st.write(f"Carregados {len(df)} leads. Veja os primeiros:")
        st.dataframe(df.head(3))

        if st.button("🚀 Iniciar Enriquecimento"):
            resultados_finais = []
            progresso = st.progress(0)
            status = st.empty()
            
            for i, row in df.iterrows():
                status.text(f"Buscando dados do lead {i+1} de {len(df)}...")
                
                # O prompt que o código envia para o Gemini
                prompt_chamada = f"""
                LEAD ATUAL: {row.to_dict()}
                ICP SOLICITADO: {icp_atual}
                
                Instrução: Enriqueça este lead conforme as regras do sistema (Especialista Athalaia).
                Seja assertivo, procure dados reais e crie o insight para venda de OFFSET.
                Responda APENAS o objeto JSON puro.
                """
                
                try:
                    response = model.generate_content(prompt_chamada)
                    # Limpa o texto da resposta para evitar erro de JSON
                    limpo = response.text.replace('```json', '').replace('```', '').strip()
                    dados_json = json.loads(limpo)
                    resultados_finais.append(dados_json)
                except Exception as e:
                    resultados_finais.append({"erro": "Não processado", "detalhe": str(e)})
                
                progresso.progress((i + 1) / len(df))
                # Pausa pequena para não ser bloqueado pela API (Rate Limit)
                time.sleep(2) 

            # Gerar tabela final
            df_enriquecido = pd.concat([df, pd.DataFrame(resultados_finais)], axis=1)
            st.success("✅ Enriquecimento concluído com sucesso!")
            st.dataframe(df_enriquecido)

            # Botão de Exportar para Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_enriquecido.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 Baixar Lista Enriquecida (XLSX)",
                data=output.getvalue(),
                file_name="leads_athalaia_final.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
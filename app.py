import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import time
import io

st.set_page_config(page_title="Athalaia Universal ICP", layout="wide")

st.title("🚀 Athalaia: Inteligência Comercial Universal")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Painel de Controle")
    api_key = st.text_input("Sua Gemini API Key:", type="password")
    st.divider()
    st.info("💡 O robô agora analisa automaticamente se o lead se encaixa no padrão de luxo da Athalaia.")

if not api_key:
    st.warning("👈 Por favor, insira sua API Key para ativar o Investigador.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')

    file = st.file_uploader("📂 Importar Planilha de Prospecção", type=['csv', 'xlsx'])

    if file:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        
        if st.button("🚀 Iniciar Varredura e Qualificação"):
            final_data = []
            bar = st.progress(0)
            status_update = st.empty()
            
            for i, row in df.iterrows():
                empresa_nome = row.get('RAZÃO SOCIAL', row.get('Empresa', row.get('NOME DA EMPRESA', 'Empresa')))
                status_update.text(f"🕵️ Analisando Potencial: {empresa_nome}...")
                
                # O prompt agora é focado na Qualificação Universal
                prompt = f"Realize a investigação profunda e qualificação de ICP para este lead: {row.to_dict()}. Siga estritamente o formato JSON das System Instructions."
                
                try:
                    response = model.generate_content(prompt)
                    res_text = response.text.replace('```json', '').replace('```', '').strip()
                    final_data.append(json.loads(res_text))
                except Exception as e:
                    final_data.append({"Empresa": empresa_nome, "status_icp": "Erro no Processamento"})
                
                time.sleep(4) # Pausa para busca multicanal exaustiva
                bar.progress((i + 1) / len(df))

            df_final = pd.DataFrame(final_data)
            st.success("✅ Varredura Concluída!")
            st.dataframe(df_final)
            
            # Exportar sem colunas de sistema, apenas os dados de elite
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_final.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 Baixar Planilha Qualificada Athalaia",
                data=output.getvalue(),
                file_name="leads_enriquecidos_athalaia.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

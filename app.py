import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import time
import io

st.set_page_config(page_title="Athalaia Inteligência V2", layout="wide")

st.title("🚀 Enriquecedor Athalaia: Validação e Expansão")

with st.sidebar:
    st.header("Configurações")
    api_key = st.text_input("Sua Gemini API Key:", type="password")
    icp_segmento = st.selectbox("Selecione o Segmento do Briefing:", 
                                ["Segmento 1 - Editoras", 
                                 "Segmento 2 - ONGs (Norte)", 
                                 "Segmento 3 - Escolas (CO/Acre)", 
                                 "Segmento 4 - Marketing (DF)"])
    st.info("O robô validará seus dados atuais e buscará os faltantes (2 Fixos + 2 Celulares).")

if not api_key:
    st.warning("👈 Insira sua API Key para começar.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')

    file = st.file_uploader("Importar Lista de Prospecção", type=['csv', 'xlsx'])

    if file:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        st.write("Dados Originais:", df.head(3))

        if st.button("🚀 Iniciar Processamento Inteligente"):
            final_data = []
            prog = st.progress(0)
            
            for i, row in df.iterrows():
                # Enviamos os dados que você já tem para o robô validar
                prompt = f"""
                DADOS ATUAIS: {row.to_dict()}
                SEGMENTO BRIEFING: {icp_segmento}
                
                TAREFA:
                1. Valide se os telefones e e-mails atuais estão corretos para o decisor.
                2. Se corretos, mantenha-os. Se errados, substitua.
                3. Complete até ter: 2 Telefones Fixos e 2 Celulares (WhatsApp).
                4. Verifique se a empresa segue o CNAE/Regra do Segmento.
                
                Retorne APENAS JSON:
                {{
                  "status_validacao": "Mantido / Enriquecido / Substituído",
                  "nome_decisor": "",
                  "cargo_confirmado": "",
                  "email_1": "",
                  "fixo_1": "",
                  "fixo_2": "",
                  "celular_1": "",
                  "celular_2": "",
                  "faturamento_estimado": "",
                  "linkedin": "",
                  "insight_venda_offset": ""
                }}
                """
                
                try:
                    response = model.generate_content(prompt)
                    limpo = response.text.replace('```json', '').replace('```', '').strip()
                    final_data.append(json.loads(limpo))
                except:
                    final_data.append({"status_validacao": "Erro"})
                
                prog.progress((i + 1) / len(df))
                time.sleep(2)

            df_final = pd.concat([df, pd.DataFrame(final_data)], axis=1)
            
            # Aplicando cores para facilitar sua leitura
            def color_status(val):
                color = 'white'
                if val == 'Enriquecido': color = '#C6F6D5' # Verde claro
                if val == 'Substituído': color = '#FEEBC8' # Laranja claro
                return f'background-color: {color}'

            st.success("✅ Processamento concluído!")
            st.dataframe(df_final.style.applymap(color_status, subset=['status_validacao']))

            # Exportação
            output = io.BytesIO()
            df_final.to_excel(output, index=False)
            st.download_button("📥 Baixar Planilha Athalaia Qualificada", output.getvalue(), "leads_qualificados.xlsx")

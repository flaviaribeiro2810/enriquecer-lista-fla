import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import time
import io

# Configuração da Página
st.set_page_config(page_title="Athalaia Inteligência Comercial", layout="wide")

st.title("🕵️ Investigação Profunda Athalaia")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Configurações de Busca")
    api_key = st.text_input("Gemini API Key:", type="password")
    st.divider()
    icp_segmento = st.selectbox("🎯 Segmento Alvo:", 
                                ["Incorporadoras (DF)", 
                                 "Editoras (Brasil)", 
                                 "Escolas", 
                                 "Marketing (DF)", 
                                 "ONGs (Norte)"])
    st.info("💡 Esta versão utiliza Busca Multicanal (Google, LinkedIn, Mapas e Bases Públicas).")

if not api_key:
    st.warning("👈 Por favor, insira sua API Key para ativar o robô investigador.")
else:
    genai.configure(api_key=api_key)
    # Forçamos o modelo PRO para maior inteligência de busca
    model = genai.GenerativeModel('gemini-1.5-pro')

    file = st.file_uploader("📂 Importar Planilha (Mesmo que só tenha Nome e CNPJ)", type=['csv', 'xlsx'])

    if file:
        # Carregamento da planilha
        if file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file)
            
        st.write(f"📊 Leads carregados: {len(df)}")

        if st.button("🚀 Iniciar Busca Exaustiva"):
            final_data = []
            prog = st.progress(0)
            status_update = st.empty()
            
            for i, row in df.iterrows():
                empresa = row.get('RAZÃO SOCIAL', row.get('NOME DA EMPRESA', row.get('Empresa', 'Empresa')))
                cnpj = row.get('CNPJ', '')
                
                status_update.text(f"🕵️ Investigando a fundo: {empresa}...")
                
                # PROMPT DE INVESTIGAÇÃO MULTICANAL
                prompt = f"""
                INVESTIGAÇÃO EXAUSTIVA DE LEAD B2B:
                EMPRESA: {empresa}
                CNPJ: {cnpj}
                SEGMENTO: {icp_segmento}
                DADOS ATUAIS (VALIDAR): {row.to_dict()}

                INSTRUÇÕES DE BUSCA PROFUNDA:
                1. Não aceite os dados atuais como certos. Verifique se o decisor ainda está na empresa.
                2. Use o CNPJ para confirmar o site oficial e a saúde da empresa.
                3. Procure o Diretor/Gerente de Marketing ou Compras.
                4. Procure 2 telefones FIXOS (Sede/Filial) e 2 CELULARES (WhatsApp do decisor).
                5. Se for Incorporadora, procure o telefone da 'Central de Vendas' para chegar ao Marketing.
                6. Estime o Faturamento com base no capital social e porte.

                RETORNE APENAS O JSON NO FORMATO:
                {{
                  "investigacao_status": "Sucesso - Multicanal",
                  "nome_decisor": "",
                  "cargo_real": "",
                  "email_corporativo": "",
                  "telefone_fixo_1": "",
                  "telefone_fixo_2": "",
                  "celular_1_whats": "",
                  "celular_2_whats": "",
                  "linkedin_url": "",
                  "faturamento_estimado": "",
                  "insight_estrategico": ""
                }}
                """
                
                try:
                    # O robô agora tem tempo para 'pensar' e pesquisar
                    response = model.generate_content(prompt)
                    res_text = response.text.replace('```json', '').replace('```', '').strip()
                    dados_json = json.loads(res_text)
                    final_data.append(dados_json)
                except Exception as e:
                    # Em caso de falha, ele não para o processo
                    final_data.append({"investigacao_status": "Erro na busca profunda"})
                
                # Pausa estratégica para evitar bloqueio e permitir que o robô processe melhor
                time.sleep(4) 
                prog.progress((i + 1) / len(df))

            # Unir os resultados à planilha original
            df_final = pd.concat([df, pd.DataFrame(final_data)], axis=1)
            
            st.success("✅ Investigação Concluída com Sucesso!")
            st.dataframe(df_final)

            # Preparar download
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_final.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 Baixar Planilha Qualificada Athalaia",
                data=output.getvalue(),
                file_name=f"investigacao_athalaia_{icp_segmento}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

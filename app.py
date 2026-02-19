# Trecho alterado dentro do loop de processamento
for i, row in df.iterrows():
    status_update.text(f"🕵️ Investigação Profunda: {empresa_nome} (Lead {i+1} de {len(df)})")
    
    prompt = f"""
    INVESTIGAÇÃO EXAUSTIVA DE LEAD:
    DADOS: {row.to_dict()}
    
    PASSO A PASSO OBRIGATÓRIO:
    1. Verifique o CNPJ em bases de dados públicas para confirmar a Razão Social.
    2. Acesse o site oficial (se houver) para identificar o padrão de e-mail nominal.
    3. Busque no LinkedIn e diretórios corporativos o Decisor de Marketing/Compras.
    4. Encontre o telefone da sede (FIXO) e o WhatsApp direto do decisor.
    5. Cruze dados de faturamento estimado para validar se é Médio/Grande porte.

    RETORNE JSON APENAS:
    {{
      "status": "Validação Multicanal Concluída",
      "nome_decisor": "",
      "cargo_real": "",
      "email_corporativo": "",
      "telefone_fixo_1": "",
      "telefone_fixo_2": "",
      "celular_1_whats": "",
      "celular_2_whats": "",
      "faturamento_estimado": "",
      "linkedin_url": "",
      "insight_estrategico": ""
    }}
    """
    
    try:
        # Usamos o modelo PRO com maior temperatura para criatividade na busca
        response = model.generate_content(prompt)
        # Pausa maior (4 segundos) para evitar bloqueio e garantir profundidade
        time.sleep(4) 
        # ... (resto do código de tratamento de JSON)

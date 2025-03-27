import streamlit as st
from datetime import datetime

# Inicialização das estruturas de dados
if "demandas" not in st.session_state:
    st.session_state.demandas = []
if "historico" not in st.session_state:
    st.session_state.historico = []

# Simulação de usuários
usuarios = {
    "1": "Líder João",
    "2": "Colaborador Maria",
    "3": "Colaborador Pedro"
}

# Função para registrar atividade no histórico
def registrar_atividade(demanda, acao, usuario):
    st.session_state.historico.append({
        "data_hora": datetime.now(),
        "demanda_id": demanda["id"],
        "titulo_demanda": demanda["titulo"],
        "acao": acao,
        "usuario": usuarios[usuario],
        "status": demanda["status"]
    })

# Configuração da página
st.set_page_config(
    page_title="Sistema de Gestão de Demandas",
    page_icon="📋",
    layout="wide"
)

# Sidebar para criar demanda (apenas líder)
st.sidebar.header("🆕 Criar Nova Demanda")
with st.sidebar:
    titulo = st.text_input("Título da Demanda")
    descricao = st.text_area("Descrição")
    colaborador_id = st.selectbox(
        "Atribuir a:",
        list(usuarios.keys()),
        format_func=lambda x: usuarios[x]
    )
    prioridade = st.select_slider(
        "Prioridade",
        options=["Baixa", "Média", "Alta"],
        value="Média"
    )
    data_limite = st.date_input("Data Limite")

    if st.button("📝 Criar Demanda"):
        nova_demanda = {
            "id": len(st.session_state.demandas) + 1,
            "titulo": titulo,
            "descricao": descricao,
            "status": "pendente",
            "lider_id": "1",
            "colaborador_id": colaborador_id,
            "confirmacao_lider": False,
            "prioridade": prioridade,
            "data_criacao": datetime.now(),
            "data_limite": data_limite,
            "data_conclusao": None
        }
        st.session_state.demandas.append(nova_demanda)
        registrar_atividade(nova_demanda, "criação", "1")
        st.success("✅ Demanda criada com sucesso!")

# Corpo principal
st.title("📋 Sistema de Gestão de Demandas")

# Abas principais
aba = st.tabs(["📝 Minhas Demandas", "✅ Confirmar Conclusão", "📊 Histórico", "📈 Dashboard"])

# Aba 1: Minhas Demandas
with aba[0]:
    usuario_atual = st.selectbox(
        "👤 Selecione seu usuário:",
        list(usuarios.keys()),
        format_func=lambda x: usuarios[x]
    )
    
    demandas_usuario = [d for d in st.session_state.demandas if d["colaborador_id"] == usuario_atual]
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        filtro_status = st.multiselect(
            "Status:",
            ["pendente", "concluído", "confirmado"],
            default=["pendente"]
        )
    with col2:
        filtro_prioridade = st.multiselect(
            "Prioridade:",
            ["Baixa", "Média", "Alta"],
            default=["Alta", "Média", "Baixa"]
        )
    
    demandas_filtradas = [
        d for d in demandas_usuario
        if d["status"] in filtro_status
        and d["prioridade"] in filtro_prioridade
    ]
    
    for demanda in demandas_filtradas:
        with st.expander(f"📌 {demanda['titulo']} - {demanda['status'].upper()}"):
            st.write(f"📝 Descrição: {demanda['descricao']}")
            st.write(f"⚡ Prioridade: {demanda['prioridade']}")
            st.write(f"📅 Data Limite: {demanda['data_limite'].strftime('%d/%m/%Y')}")
            
            if demanda["status"] == "pendente":
                if st.button("✅ Concluir", key=f"done_{demanda['id']}"):
                    demanda["status"] = "concluído"
                    demanda["data_conclusao"] = datetime.now()
                    registrar_atividade(demanda, "conclusão", usuario_atual)
                    st.success("Demanda concluída!")

# Aba 2: Confirmar Conclusão
with aba[1]:
    if usuario_atual == "1":  # Apenas líder
        demandas_concluidas = [
            d for d in st.session_state.demandas
            if d["status"] == "concluído" and not d["confirmacao_lider"]
        ]
        
        for demanda in demandas_concluidas:
            with st.expander(f"✅ {demanda['titulo']} - Aguardando Confirmação"):
                st.write(f"📝 Descrição: {demanda['descricao']}")
                st.write(f"👤 Responsável: {usuarios[demanda['colaborador_id']]}")
                st.write(f"📅 Concluído em: {demanda['data_conclusao'].strftime('%d/%m/%Y %H:%M')}")
                
                if st.button("✔️ Confirmar", key=f"confirm_{demanda['id']}"):
                    demanda["confirmacao_lider"] = True
                    registrar_atividade(demanda, "confirmação", "1")
                    st.success("Confirmado com sucesso!")
    else:
        st.warning("⚠️ Acesso restrito ao líder")

# Aba 3: Histórico
with aba[2]:
    st.subheader("📊 Histórico de Atividades")
    
    historico_ordenado = sorted(
        st.session_state.historico,
        key=lambda x: x["data_hora"],
        reverse=True
    )
    
    for registro in historico_ordenado:
        with st.expander(
            f"🕒 {registro['data_hora'].strftime('%d/%m/%Y %H:%M')} - {registro['titulo_demanda']}"
        ):
            st.write(f"👤 Usuário: {registro['usuario']}")
            st.write(f"🔄 Ação: {registro['acao']}")
            st.write(f"📌 Status: {registro['status']}")

# Aba 4: Dashboard
with aba[3]:
    st.subheader("📈 Métricas Gerais")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_demandas = len(st.session_state.demandas)
        st.metric("Total de Demandas", total_demandas)
    
    with col2:
        demandas_concluidas = len([d for d in st.session_state.demandas if d["status"] == "concluído"])
        st.metric("Concluídas", demandas_concluidas)
    
    with col3:
        taxa_conclusao = (demandas_concluidas / total_demandas * 100) if total_demandas > 0 else 0
        st.metric("Taxa de Conclusão", f"{taxa_conclusao:.1f}%")
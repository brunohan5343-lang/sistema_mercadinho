import io
import pandas as pd
import qrcode
import requests
import streamlit as st

st.set_page_config(page_title="Sistema Mercadinho", page_icon="🛒", layout="wide")

# COLE A SUA URL DO WEB APP DO APPS SCRIPT ABAIXO ENTRE AS ASPAS:
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyeSMe78SNPOQdFlLVoIlIRSUqPdXs5kmY92XZfuCupx-Vxrkf_JouXZs883lNngcRdog/exec"

# Funções de comunicação com a planilha via Apps Script
def carregar_dados(aba):
    try:
        resposta = requests.get(f"{WEB_APP_URL}?aba={aba}")
        return resposta.json()
    except Exception as e:
        return [{"erro": f"Falha de conexão: {e}"}]

def enviar_dados(acao, aba, dados):
    payload = {"acao": acao, "aba": aba, "dados": dados}
    try:
        resposta = requests.post(WEB_APP_URL, json=payload)
        return resposta.json()
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

st.title("🛒 Gestão do Mercadinho - Painel Administrativo")
menu = st.sidebar.selectbox("Menu Principal", ["📦 Produtos", "👥 Clientes", "📱 Gerador de QR Code"])

# ==================== ABA PRODUTOS ====================
if menu == "📦 Produtos":
    st.subheader("Gerenciamento de Produtos e Estoque")
    
    tab_lista, tab_add, tab_edit, tab_del = st.tabs(["📋 Lista de Produtos", "➕ Adicionar", "✏️ Editar", "🗑️ Excluir"])
    
    with tab_lista:
        dados_prod = carregar_dados("Produtos")
        if dados_prod and "erro" not in dados_prod[0]:
            st.dataframe(pd.DataFrame(dados_prod), use_container_width=True)
        else:
            st.warning("Nenhum produto cadastrado ou falha ao carregar.")

    with tab_add:
        with st.form("form_add_prod", clear_on_submit=True):
            col1, col2 = st.columns(2)
            id_prod = col1.text_input("ID do Produto")
            nome_prod = col2.text_input("Nome do Produto")
            descricao = col1.text_input("Descrição")
            preco_custo = col2.number_input("Preço de Custo (R$)", min_value=0.0, step=0.1)
            preco_venda = col1.number_input("Preço de Venda (R$)", min_value=0.0, step=0.1)
            preco_atacado = col2.number_input("Preço Atacado (R$)", min_value=0.0, step=0.1)
            qtd_minima = col1.number_input("Qtd. Mínima Atacado", min_value=0, step=1)
            estoque = col2.number_input("Estoque", min_value=0, step=1)
            url_imagem = st.text_input("URL da Imagem (Opcional)")
            
            if st.form_submit_button("Salvar Novo Produto", type="primary"):
                dados = {
                    "ID_Produto": id_prod, 
                    "Nome": nome_prod, 
                    "Descricao": descricao,
                    "Preco_Custo": preco_custo,
                    "Preco_Venda": preco_venda, 
                    "Preco_Atacado": preco_atacado, 
                    "Qtd_Minima_Atacad": qtd_minima,
                    "Estoque": estoque,
                    "URL_Imagem": url_imagem
                }
                res = enviar_dados("adicionar", "Produtos", dados)
                if res.get("sucesso"): st.success(res["mensagem"])
                else: st.error(f"Erro: {res.get('erro')}")

    with tab_edit:
        st.info("Digite o ID do Produto que deseja editar. Preencha apenas os campos que quiser alterar.")
        with st.form("form_edit_prod"):
            id_edit = st.text_input("ID do Produto (Obrigatório)")
            novo_nome = st.text_input("Novo Nome")
            novo_preco_venda = st.text_input("Novo Preço de Venda")
            novo_estoque = st.text_input("Novo Estoque")
            
            if st.form_submit_button("Atualizar Produto"):
                dados = {"ID_Produto": id_edit}
                if novo_nome: dados["Nome"] = novo_nome
                if novo_preco_venda: dados["Preco_Venda"] = novo_preco_venda
                if novo_estoque: dados["Estoque"] = novo_estoque
                
                res = enviar_dados("editar", "Produtos", dados)
                if res.get("sucesso"): st.success(res["mensagem"])
                else: st.error(f"Erro: {res.get('erro')}")

    with tab_del:
        with st.form("form_del_prod"):
            id_del = st.text_input("ID do Produto a ser excluído")
            st.warning("Esta ação apagará a linha inteira da planilha permanentemente.")
            if st.form_submit_button("Excluir Produto"):
                res = enviar_dados("excluir", "Produtos", {"ID_Produto": id_del})
                if res.get("sucesso"): st.success(res["mensagem"])
                else: st.error(f"Erro: {res.get('erro')}")

# ==================== ABA CLIENTES ====================
elif menu == "👥 Clientes":
    st.subheader("Base de Clientes (CRM)")
    
    tab_lista_cli, tab_add_cli, tab_edit_cli, tab_del_cli = st.tabs(["📋 Lista de Clientes", "➕ Cadastrar", "✏️ Editar", "🗑️ Remover"])
    
    with tab_lista_cli:
        dados_cli = carregar_dados("Clientes")
        if dados_cli and "erro" not in dados_cli[0]:
            st.dataframe(pd.DataFrame(dados_cli), use_container_width=True)
        else:
            st.warning("Nenhum cliente cadastrado.")

    with tab_add_cli:
        with st.form("form_add_cli", clear_on_submit=True):
            col1, col2 = st.columns(2)
            cpf_cli = col1.text_input("CPF do Cliente")
            nome_cli = col2.text_input("Nome Completo")
            telefone_cli = col1.text_input("Telefone")
            
            if st.form_submit_button("Cadastrar Cliente", type="primary"):
                dados = {"CPF": cpf_cli, "Nome": nome_cli, "Telefone": telefone_cli}
                res = enviar_dados("adicionar", "Clientes", dados)
                if res.get("sucesso"): st.success("Cliente cadastrado com sucesso!")
                else: st.error(f"Erro: {res.get('erro')}")

    with tab_edit_cli:
        with st.form("form_edit_cli"):
            cpf_edit = st.text_input("CPF do Cliente para editar")
            novo_nome_cli = st.text_input("Novo Nome")
            novo_tel_cli = st.text_input("Novo Telefone")
            
            if st.form_submit_button("Atualizar Cliente"):
                dados = {"CPF": cpf_edit}
                if novo_nome_cli: dados["Nome"] = novo_nome_cli
                if novo_tel_cli: dados["Telefone"] = novo_tel_cli
                
                res = enviar_dados("editar", "Clientes", dados)
                if res.get("sucesso"): st.success(res["mensagem"])
                else: st.error(f"Erro: {res.get('erro')}")

    with tab_del_cli:
        with st.form("form_del_cli"):
            cpf_del = st.text_input("CPF do Cliente a ser removido")
            if st.form_submit_button("Remover Cliente"):
                res = enviar_dados("excluir", "Clientes", {"CPF": cpf_del})
                if res.get("sucesso"): st.success(res["mensagem"])
                else: st.error(f"Erro: {res.get('erro')}")

# ==================== ABA QR CODE ====================
elif menu == "📱 Gerador de QR Code":
    st.subheader("Gerador de QR Code para as Prateleiras")
    st.write("Selecione um produto cadastrado para gerar o QR code que ficará exposto na gôndola.")
    
    dados_prod = carregar_dados("Produtos")
    if dados_prod and "erro" not in dados_prod[0]:
        df_produtos = pd.DataFrame(dados_prod)
        
        produto_coluna = "Nome" if "Nome" in df_produtos.columns else df_produtos.columns[0]
        produto_selecionado = st.selectbox("Selecione o Produto", df_produtos[produto_coluna].tolist())
        
        detalhes = df_produtos[df_produtos[produto_coluna] == produto_selecionado].iloc[0]
        
        link_produto = f"https://seu-app.streamlit.app/?produto={detalhes.get('ID_Produto', 1)}"
        st.info(f"Link associado ao QR Code: `{link_produto}`")
        
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(link_produto)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(byte_im, caption=f"QR Code - {produto_selecionado}", width=250)
        with col2:
            st.write(f"**Produto:** {produto_selecionado}")
            st.write(f"**Preço de Venda:** R$ {detalhes.get('Preco_Venda', '0.00')}")
            st.write(f"**Preço Atacado:** R$ {detalhes.get('Preco_Atacado', '0.00')}")
            st.download_button(
                label="Baixar Imagem do QR Code",
                data=byte_im,
                file_name=f"qrcode_{produto_selecionado}.png",
                mime="image/png"
            )
    else:
        st.warning("Nenhum produto encontrado para gerar o QR Code.")

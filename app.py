import streamlit as st
from groq import Groq
import sqlite3 as sq
from datetime import datetime

# --- Configurações Iniciais ---
try:
    chave_secreta = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=chave_secreta)
except:
    st.error("A chave da API não foi configurada nos segredos!")
    st.stop()


# --- Funções do Banco de Dados ---
def criar_dados():
    dados = sq.connect('historico.db')
    d = dados.cursor()
    d.execute(
        '''
        CREATE TABLE IF NOT EXISTS estudos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conteudo_usuario TEXT,
            resposta_ia TEXT,
            data_registro TEXT
        )
    '''
    )
    dados.commit()
    dados.close()

def salvar_dados(text_usuario, resposta):
    dados = sq.connect('historico.db')
    d = dados.cursor()
    data_atual = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    d.execute('INSERT INTO estudos (conteudo_usuario, resposta_ia, data_registro) VALUES (?, ?, ?)', 
              (text_usuario, resposta, data_atual))
    dados.commit()
    dados.close()

def ler_dados():
    dados = sq.connect('historico.db')
    d = dados.cursor()
    d.execute('SELECT * FROM estudos ORDER BY id DESC')
    resultados = d.fetchall()
    dados.close()
    return resultados

# Garante que a tabela existe ao iniciar
criar_dados()

# --- Interface Principal ---
st.title('Seu Mentor IA 🧠')

# --- MUDANÇA AQUI: Criando o Formulário ---

with st.form(key='formulario_estudos', clear_on_submit=True):
    # A caixa de texto fica indentada (dentro do form)
    text_usuario = st.text_area('FEITO PELO IGOR!!! Estou aqui para agir como mentor nos seus estudos, resuma seu estudo:', placeholder='Digite o que estudei aqui...') 
    
    # O botão DEVE ser st.form_submit_button
    botao_enviar = st.form_submit_button('Enviar')

# A lógica acontece QUANDO o botão do formulário é clicado
if botao_enviar:
    if not text_usuario:
        st.warning('Digite algo antes de enviar!')
    else:
        # Spinner para feedback visual enquanto carrega
        with st.spinner('Consultando o mentor...'):
            chat = client.chat.completions.create(
                messages=[
                    {
                        'role': 'system',
                        'content': '''
                            Você é o Igor, um mentor de estudos focado em alta performance.
                            Sua atitude é: Direto, exigente, mas motivador (Estilo "Tropa de Elite").
                            
                            REGRA DE OURO: Você DEVE responder seguindo essa referencia de formato abaixo:
                            
                            Nota: [Dê uma nota de 0 a 10 baseada na clareza do resumo] / Caso de não viavel não diga a nota (Explique o porque da nota)
                            Análise: [Seu feedback curto e grosso em 1 parágrafo]
                            Próximo Passo: [Uma sugestão técnica do que estudar amanhã]
                            '''
                    },
                    {
                        'role': 'user',
                        'content': text_usuario,
                    }
                ],
                model="llama-3.3-70b-versatile",
            )

            resposta = chat.choices[0].message.content
            salvar_dados(text_usuario, resposta)

        # Mostra a resposta fora do spinner
        st.write('### Resposta do Mentor Igor:')
        st.write(resposta)

# --- Barra Lateral ---
st.sidebar.title('Histórico dos resumos 📜')
historico = ler_dados()

for item in historico:
    with st.sidebar.expander(f'Data: {item[3]}'):
        st.write(f'**Você estudou:** {item[1]}')
        st.divider()

        st.write(f'**Luiz:** {item[2]}')

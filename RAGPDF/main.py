from langchain_chroma.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

PATH_DB = "db"

prompt_template = """
    Responda a pergunta do usuário:
    {question}

    com base nessas informações:
    {base_conhecimento}

    Se você não encontrar a resposta para a pergunta do usuário nessas informações, responda que não sabe.
"""

def make_a_question():

    question = input("Faca uma pergunta: ")

    # Carregar o banco de dados
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma(persist_directory=PATH_DB, embedding_function=embeddings)

    # Comparar a pergunta vetorizada (embedding) com o meu banco de dados
    # k = quantos resultados eu quero recuperar (quanto maior, mais chunks, maior o contexto)
    results = db.similarity_search_with_relevance_scores(question, k=3)

    print(results)
    #print(len(results))

    # results[0][1] é o score do primeiro chunk encontrado, [0] é o melhor resultado, [0][1] é o score, vai de 0 a 1.
    #if len(results) == 0 or results[0][1] < 0.4:
    if len(results) == 0:
        print("Não encontrou nenhuma informação relevante na base")

        # como não encontrei nada na minha base de dados que tenha um bom score de resposta, eu nem chego a enviar pra LLM!
        # Não consumo token, nem nada. Eu já mato aqui o código
        # Atualmente não to considerando score (0-1) porque alguns teste o score fica negativo, aí o langchain reclama
        # mas eu tiro porque funciona mesmo assim pra eu aprender
        return

    texts_results = []
    for result in results:
        text = result[0].page_content
        texts_results.append(text)

    base_conhecimento = "\n\n----\n\n".join(texts_results)
    prompt = ChatPromptTemplate.from_template(prompt_template)
    # Passando os parametros para o prompt, o invoke pega e preenche o template (é do langchain). O invoke executa algo.
    prompt = prompt.invoke({"question": question, "base_conhecimento": base_conhecimento})
    #print(prompt)

    model = ChatGoogleGenerativeAI( model="gemini-2.5-flash" )
    # Aqui o invoke envia a mensagem para o Gemini
    response_text = model.invoke(prompt).content
    print("AI Response: ", response_text)


make_a_question()

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

load_dotenv()

# Sempre que eu trocar de pdf, preciso apagar o banco vetorial e rodar a página denovo
# rm -rf db ou apagar manualmente a pasta
# Atualmente, esse projeto lê só 1 pdf, não todos os pdf da pasta

def create_db():
    # carregar o documento da base de conhecimento
    doc = load_docs()

    # Security: presidio microsoft. Subtituir os dados sensiveis antes mesmo de salvar no banco vetorial
    # ou seja, esses dados nao serao enviados para a LLM, só uma substituicao deles
    # doc = anonymize_documents(doc)

    # dividir os documentos em pedacos de texto (chuncks)
    chunks = divide_into_chunks(doc)

    # vetorizar os chuncks com o processo de embedding
    vectorize_chunks(chunks)



def load_docs():
    loader = PyMuPDFLoader("base/o-medico-e-o-monstro.pdf")
    doc = loader.load()

    return doc

def anonymize_documents(doc):

    # text = "My name is John Doe. My email is john@email.com"
    text = doc[0].page_content
    #print(text)

    # Analiza/Detecta informacoes sensiveis e retorna onde elas estao
    analyzer = AnalyzerEngine()
    results = analyzer.analyze(text=text, language="en")
    #print(results)

    # Pega as posicoes encontradas pelo AnalyzerEngine e substitui os dados
    anonymizer = AnonymizerEngine()
    anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
    #print(anonymized.text)

    doc[0].page_content = anonymized.text

    return doc


def divide_into_chunks(doc):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=500,
        length_function=len,
        add_start_index=True
    )

    chunks = splitter.split_documents(doc)
    # print(len(chunks))
    # ta quebrando em 16 chunks
    return chunks


def vectorize_chunks(chunks):

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    db = Chroma.from_documents(chunks, embeddings, persist_directory="db")
    print("banco de dados criado")

create_db()
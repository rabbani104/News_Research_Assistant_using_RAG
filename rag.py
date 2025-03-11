import os
from uuid import uuid4
from dotenv import load_dotenv
from pathlib import Path
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.storage import InMemoryStore
from langchain.vectorstores import DuckDB

load_dotenv()


# api_key = os.getenv("GROQ_API_KEY")
# if not api_key:
#     raise ValueError("GROQ API key is missing!")

# Constants
CHUNK_SIZE = 1000
EMBEDDING_MODEL = "Alibaba-NLP/gte-base-en-v1.5"
VECTORSTORE_DIR = Path(__file__).parent / "resources/vectorstore"
COLLECTION_NAME = "news_research"

llm = None
vector_store = None

def initialize_components(api_key):
    global llm, vector_store

    if llm is None:
        llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key, temperature=0.9, max_tokens=500)

    if vector_store is None:
        ef = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"trust_remote_code": True}
        )
        
        storage = InMemoryStore()
        vector_store = DuckDB(
            embedding_function=ef,
            storage_context=storage,
        )

def process_urls(urls, api_key):
    yield "Initializing Components"
    initialize_components(api_key)

    yield "Resetting vector store...✅"
    vector_store.clear()

    yield "Loading data...✅"
    loader = UnstructuredURLLoader(urls)
    data = loader.load()

    yield "Splitting text into chunks...✅"
    text_splitter = RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n', '.', ' '],
        chunk_size=CHUNK_SIZE,
    )

    docs = text_splitter.split_documents(data)

    yield "Add chunks to vector database...✅"
    uuids = [str(uuid4()) for _ in range(len(docs))]
    vector_store.add_documents(docs, ids=uuids)

    yield "Done adding docs to vector database...✅"

def generate_answer(query):
    if not vector_store:
        raise RuntimeError("Vector DB not initialized")
    chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=vector_store.as_retriever())
    result = chain.invoke({"question": query}, return_only_outputs=True)
    sources = result.get("sources", "")

    return result['answer'], sources

if __name__ == "__main__":
    urls = [
        "https://www.cnbc.com/2024/12/21/how-the-federal-reserves-rate-policy-affects-mortgages.html",
        "https://www.cnbc.com/2024/12/20/why-mortgage-rates-jumped-despite-fed-interest-rate-cut.html"
    ]

    process_urls(urls)

    answer, sources = generate_answer("Tell me what was the 30 year fixed mortgage rate along with the date?")
    print(f"Answer: {answer}")
    print(f"Sources: {sources}")

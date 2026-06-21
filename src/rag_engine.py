import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from src.config import (
    GEMINI_API_KEY, 
    EMBEDDING_MODEL, 
    LLM_MODEL, 
    CHUNK_SIZE, 
    CHUNK_OVERLAP, 
    DB_DIR, 
    DOCS_DIR,
    METADATA_FILE,
    validate_config
)

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

class NutritionRAGEngine:
    def __init__(self):
        """
        Initialize the embedding model and database state.
        Automatically triggers database building if none exists.
        """
        # Ensure directories exist
        DB_DIR.mkdir(parents=True, exist_ok=True)
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load local embedding model
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.vector_store = None
        self.qa_chain = None
        
        # Check if vector DB has files, if not, trigger build
        self.auto_build_db_if_needed()

    def auto_build_db_if_needed(self):
        """
        Verify if the ChromaDB vector database exists.
        If it does not exist, automatically ingest raw documents.
        """
        db_files = list(DB_DIR.glob("**/*"))
        has_db = len([f for f in db_files if f.is_file()]) > 0
        
        if not has_db:
            # Auto-build database
            self.rebuild_database()
        else:
            # Initialize connection to existing DB
            self.initialize_vector_store()
            self.setup_qa_chain()

    def rebuild_database(self) -> Dict[str, Any]:
        """
        Scans data/raw_documents, chunks PDFs, stores them in ChromaDB,
        and saves indexing statistics in a JSON metadata file.
        """
        try:
            # 1. Scan and count PDFs
            pdf_files = list(Path(DOCS_DIR).glob("*.pdf"))
            num_pdfs = len(pdf_files)
            
            if num_pdfs == 0:
                self.save_metadata(0, 0, "No source PDFs found in raw_documents directory.", "Degraded")
                return {"status": "success", "chunks": 0, "pdfs": 0}
                
            # 2. Ingest
            loader = PyPDFDirectoryLoader(str(DOCS_DIR))
            documents = loader.load()
            if not documents:
                self.save_metadata(num_pdfs, 0, "PDFs were found but could not be parsed.", "Degraded")
                return {"status": "success", "chunks": 0, "pdfs": num_pdfs}
                
            # 3. Chunk
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                add_start_index=True
            )
            chunks = text_splitter.split_documents(documents)
            
            # 4. Generate embeddings and persist in ChromaDB
            self.vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=str(DB_DIR)
            )
            
            # Save metadata
            num_chunks = len(chunks)
            self.save_metadata(num_pdfs, num_chunks, "Successfully indexed raw documents on startup.", "Healthy")
            
            # Reload chains
            self.setup_qa_chain()
            return {"status": "success", "chunks": num_chunks, "pdfs": num_pdfs}
            
        except Exception as e:
            self.save_metadata(0, 0, f"Error building database: {str(e)}", "Error")
            return {"status": "error", "message": str(e)}

    def save_metadata(self, num_pdfs: int, num_chunks: int, message: str, health: str):
        """
        Safely update vector DB index stats in metadata JSON.
        """
        meta = {
            "num_pdfs_loaded": num_pdfs,
            "num_chunks_indexed": num_chunks,
            "last_indexing_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "health_status": health,
            "message": message
        }
        try:
            with open(METADATA_FILE, "w") as f:
                json.dump(meta, f, indent=4)
        except Exception:
            pass

    def get_metadata(self) -> Dict[str, Any]:
        """
        Retrieve indexing metadata JSON. Returns default dict if file does not exist.
        """
        if METADATA_FILE.exists():
            try:
                with open(METADATA_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "num_pdfs_loaded": 0,
            "num_chunks_indexed": 0,
            "last_indexing_timestamp": "Never",
            "health_status": "Not Initialized",
            "message": "Metadata file missing."
        }

    def initialize_vector_store(self):
        """
        Connect to the existing persistent vector database on disk.
        """
        if DB_DIR.exists() and len(list(DB_DIR.glob("*"))) > 0:
            try:
                self.vector_store = Chroma(
                    persist_directory=str(DB_DIR),
                    embedding_function=self.embeddings
                )
            except Exception as e:
                self.vector_store = None
                self.save_metadata(0, 0, f"Failed to initialize Chroma connection: {str(e)}", "Error")
        else:
            self.vector_store = None

    def setup_qa_chain(self):
        """
        Establish connection to ChatGoogleGenerativeAI and construct retrieval chains.
        """
        # Always initialize the direct LLM first
        if not validate_config():
            return
            
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=LLM_MODEL,
                temperature=0.2,
                google_api_key=os.getenv("GEMINI_API_KEY")
            )
        except Exception:
            self.llm = None
            
        if not self.vector_store:
            return
            
        try:
            # Grounding prompt instructions preventing hallucinations and medical diagnostics
            system_prompt = (
                "You are a helpful, professional, and evidence-based Health & Nutrition AI Assistant.\n"
                "Your objective is to provide high-quality educational answers strictly based on the provided source context.\n"
                "Do not make up facts or extrapolate beyond the provided text.\n"
                "Always provide an educational disclaimer in your responses. Never prescribe medical dosages or medical advice.\n"
                "If the answer cannot be verified from the context below, state clearly that you cannot find verified evidence in the guides and will rely on general knowledge.\n\n"
                "Context:\n{context}"
            )
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}")
            ])
            
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}
            )
            
            combine_docs_chain = create_stuff_documents_chain(self.llm, prompt)
            self.qa_chain = create_retrieval_chain(retriever, combine_docs_chain)
        except Exception as e:
            self.qa_chain = None

    def answer_query(self, query: str) -> Dict[str, Any]:
        """
        Query ChromaDB vector index, run LLM QA chain, and return grounded answer with sources.
        Falls back to general LLM query if no relevant context is found.
        """
        if not validate_config():
            return {
                "answer": "Google AI Studio API key is missing or invalid. Please check your environment variables (.env file) and ensure a valid GEMINI_API_KEY is configured.",
                "sources": []
            }
            
        # Ensure LLM and chain are set up
        if not hasattr(self, 'llm') or not self.llm or (self.vector_store and not self.qa_chain):
            self.setup_qa_chain()
            
        # Fallback to direct general LLM if vector database is not loaded or qa_chain failed
        use_fallback = False
        if not self.vector_store or not self.qa_chain:
            use_fallback = True
            
        if not use_fallback:
            try:
                # Retrieve documents first to verify relevance score (similarity validation)
                docs_with_scores = self.vector_store.similarity_search_with_relevance_scores(query, k=4)
                
                # Check if relevance scores are acceptable (Default threshold: 0.15)
                has_relevant = False
                for doc, score in docs_with_scores:
                    if score >= 0.15:
                        has_relevant = True
                        break
                
                if not docs_with_scores or not has_relevant:
                    use_fallback = True
                else:
                    # Run RAG QA chain
                    response = self.qa_chain.invoke({"input": query})
                    sources = []
                    context_docs = response.get("context", [])
                    for doc in context_docs:
                        source_name = Path(doc.metadata.get("source", "Unknown Guide")).name
                        page = doc.metadata.get("page", 0) + 1
                        sources.append(f"{source_name} (Page {page})")
                    sources = list(set(sources))
                    
                    return {
                        "answer": response.get("answer", "No response generated."),
                        "sources": sources
                    }
            except Exception:
                # If anything fails in RAG, fallback to general LLM
                use_fallback = True
                
        if use_fallback:
            if not hasattr(self, 'llm') or not self.llm:
                return {
                    "answer": "Unable to initialize the AI model. Please verify your Gemini API key.",
                    "sources": []
                }
            try:
                system_prompt_general = (
                    "You are a helpful, professional, and supportive AI Nutrition Coach.\n"
                    "Provide a high-quality educational answer on health, diet, weight management, or nutrition based on general scientific consensus.\n"
                    "Always structure your response clearly with bullet points where appropriate, and keep it practical.\n"
                    "Remember to include a brief, friendly general health disclaimer at the end."
                )
                messages = [
                    ("system", system_prompt_general),
                    ("human", query)
                ]
                response = self.llm.invoke(messages)
                return {
                    "answer": response.content,
                    "sources": ["General Nutrition Consensus"]
                }
            except Exception as e:
                return {
                    "answer": f"An error occurred during response synthesis: {str(e)}",
                    "sources": []
                }

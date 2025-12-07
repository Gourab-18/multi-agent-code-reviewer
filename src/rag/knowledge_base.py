import os
import argparse
from typing import List, Optional
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

load_dotenv()

# Constants
KB_DIR = os.path.join(os.getcwd(), "data/knowledge_base")
CHROMA_DB_DIR = os.path.join(os.getcwd(), "data/chroma_db")

class KnowledgeBaseBuilder:
    """Builds and populates the ChromaDB vector store from markdown files."""
    
    def __init__(self, kb_dir: str = KB_DIR, db_dir: str = CHROMA_DB_DIR):
        self.kb_dir = kb_dir
        self.db_dir = db_dir
        self.embeddings = OpenAIEmbeddings()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n## ", "\n### ", "\n", " ", ""]
        )

    def build(self):
        """Rebuilds the entire knowledge base."""
        if not os.path.exists(self.kb_dir):
            print(f"Knowledge base directory not found: {self.kb_dir}")
            return

        print(f"Loading documents from {self.kb_dir}...")
        
        # Load documents
        documents = []
        for filename in os.listdir(self.kb_dir):
            if filename.endswith(".md") or filename.endswith(".txt"):
                file_path = os.path.join(self.kb_dir, filename)
                category = self._infer_category(filename)
                
                try:
                    loader = TextLoader(file_path)
                    docs = loader.load()
                    
                    # Add metadata
                    for doc in docs:
                        doc.metadata["source_file"] = filename
                        doc.metadata["category"] = category
                        
                    documents.extend(docs)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")

        if not documents:
            print("No documents found.")
            return

        print(f"Loaded {len(documents)} source files.")
        
        # Split documents
        chunks = self.splitter.split_documents(documents)
        print(f"Split into {len(chunks)} chunks.")

        # Create/Update Vector Store
        # We delete existing logic for a clean rebuild usually, or persist. 
        # Here we will try to create a persistent instance.
        print(f"Creating vector store in {self.db_dir}...")
        
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.db_dir
        )
        print("Knowledge base built successfully.")

    def _infer_category(self, filename: str) -> str:
        """Simple heuristic to categorize files."""
        lower_name = filename.lower()
        if "security" in lower_name:
            return "security"
        elif "performance" in lower_name:
            return "performance"
        elif "quality" in lower_name or "clean" in lower_name:
            return "quality"
        return "general"

class KnowledgeBaseRetriever:
    """Retrieves context from the ChromaDB vector store."""
    
    def __init__(self, db_dir: str = CHROMA_DB_DIR):
        if not os.path.exists(db_dir):
            raise ValueError(f"Vector store not found at {db_dir}. Please run builder first.")
            
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma(
            persist_directory=db_dir,
            embedding_function=self.embeddings
        )
        
    def retrieve(self, query: str, category: Optional[str] = None, k: int = 5) -> List[Document]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: The search query string.
            category: Optional category filter (security, performance, quality).
            k: Number of results to return.
        """
        filter_dict = None
        if category:
            filter_dict = {"category": category}
            
        return self.vectorstore.similarity_search(
            query,
            k=k,
            filter=filter_dict
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage the RAG Knowledge Base")
    parser.add_argument("--build", action="store_true", help="Rebuild the knowledge base from files")
    parser.add_argument("--query", type=str, help="Test query")
    parser.add_argument("--category", type=str, help="Filter by category")
    
    args = parser.parse_args()
    
    if args.build:
        builder = KnowledgeBaseBuilder()
        builder.build()
        
    if args.query:
        try:
            retriever = KnowledgeBaseRetriever()
            results = retriever.retrieve(args.query, args.category)
            print(f"\nResults for '{args.query}' (Category: {args.category}):")
            for i, doc in enumerate(results, 1):
                print(f"\n--- Result {i} ({doc.metadata.get('source_file')}) ---")
                print(doc.page_content[:200] + "...")
        except Exception as e:
            print(f"Error retrieving: {e}")

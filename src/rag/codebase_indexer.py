import os
import argparse
from typing import List, Dict, Any
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from tree_sitter import Node

from src.tools.code_parser import CodeParser

load_dotenv()

# Constants
CHROMA_DB_DIR = os.path.join(os.getcwd(), "data/chroma_db_codebase") # Separate DB for codebase to avoid mixing with KB

class CodebaseIndexer:
    """Indexes source code files into a vector store."""
    
    def __init__(self, db_dir: str = CHROMA_DB_DIR):
        self.db_dir = db_dir
        self.embeddings = OpenAIEmbeddings()
        self.parser = CodeParser()

    def index_repo(self, repo_path: str):
        """Indexes all supported files in a repository."""
        if not os.path.exists(repo_path):
            print(f"Repository not found: {repo_path}")
            return

        print(f"Indexing repository at {repo_path}...")
        documents = []
        
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden folders and venv
            if ".git" in root or ".venv" in root or "__pycache__" in root:
                continue
                
            for file in files:
                if file.endswith((".py", ".js", ".ts", ".jsx", ".tsx")):
                    file_path = os.path.join(root, file)
                    docs = self._process_file(file_path)
                    documents.extend(docs)

        if not documents:
            print("No source files found to index.")
            return

        print(f"Generated {len(documents)} code chunks.")
        
        # Persist
        print(f"Creating vector store in {self.db_dir}...")
        # Since we might want to update, using exist_ok logic by just overwriting/appending via library
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.db_dir,
            collection_name="codebase_index"
        )
        print("Codebase indexing complete.")

    def _process_file(self, file_path: str) -> List[Document]:
        """Reads a file and chunks it by classes/functions."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            # Skip non-utf8 files
            return []

        language = "python" # default
        if file_path.endswith(".js") or file_path.endswith(".jsx"):
            language = "javascript"
        elif file_path.endswith(".ts") or file_path.endswith(".tsx"):
            language = "typescript"

        ast = self.parser.parse(content, language)
        if not ast:
            # Fallback for small files if parsing fails: just index properly as one chunk
            return [Document(
                page_content=content[:8000],  # Truncate if too huge
                metadata={"file_path": file_path, "type": "module"}
            )]

        chunks = []
        
        # 1. Extract Functions
        funcs = self.parser.extract_functions(ast)
        for func in funcs:
            func_content = self._get_lines(content, func['start_line'], func['end_line'])
            chunks.append(Document(
                page_content=f"Function: {func['name']}\n{func_content}",
                metadata={
                    "file_path": file_path,
                    "function_name": func['name'],
                    "type": "function",
                    "start_line": func['start_line']
                }
            ))

        # 2. Extract Classes
        classes = self.parser.extract_classes(ast)
        for cls in classes:
            # Note: Class content might overlap with methods, but good for retrieving class-level context
            # We might want to just store signature or docstring if it's too large, but full content is fine for RAG usually
            # as long as we don't duplicate excessively. For simplicity, we index the whole class block.
            cls_content = self._get_lines(content, cls['start_line'], cls['end_line'])
            chunks.append(Document(
                page_content=f"Class: {cls['name']}\n{cls_content}",
                metadata={
                    "file_path": file_path,
                    "class_name": cls['name'],
                    "type": "class",
                    "start_line": cls['start_line']
                }
            ))
            
        # 3. If no functions/classes found (e.g. script), index whole file
        if not funcs and not classes:
             chunks.append(Document(
                page_content=content,
                metadata={"file_path": file_path, "type": "module"}
            ))

        return chunks

    def _get_lines(self, content: str, start: int, end: int) -> str:
        """Helper to extract line range (1-based header)."""
        lines = content.splitlines()
        # Adjusted for 0-indexed list vs 1-indexed AST
        return "\n".join(lines[start-1:end])


class CodebaseRetriever:
    """Retrieves similar code patterns from indexed codebase."""
    
    def __init__(self, db_dir: str = CHROMA_DB_DIR):
        if not os.path.exists(db_dir):
             # Don't crash, just warn, allows instantiation before build in some flows
             print(f"Warning: Codebase index not found at {db_dir}")
             
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma(
            persist_directory=db_dir,
            embedding_function=self.embeddings,
            collection_name="codebase_index"
        )
        
    def retrieve_similar(self, code_snippet: str, k: int = 3) -> List[Document]:
        """Finds k most similar code chunks."""
        return self.vectorstore.similarity_search(code_snippet, k=k)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index codebase for RAG")
    parser.add_argument("--path", type=str, required=True, help="Path to repo to index")
    
    args = parser.parse_args()
    
    indexer = CodebaseIndexer()
    indexer.index_repo(args.path)

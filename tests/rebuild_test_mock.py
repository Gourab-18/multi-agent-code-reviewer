import sys
from unittest.mock import MagicMock, patch
import os
import unittest

# 1. Mock the missing modules BEFORE importing the source
# This allows us to test the logic even if packages aren't installed yet
sys.modules["langchain_openai"] = MagicMock()
sys.modules["langchain_community"] = MagicMock()
sys.modules["langchain_community.vectorstores"] = MagicMock()
sys.modules["langchain_community.document_loaders"] = MagicMock()
sys.modules["langchain_text_splitters"] = MagicMock()
sys.modules["langchain_core"] = MagicMock()
sys.modules["langchain_core.documents"] = MagicMock()
sys.modules["chromadb"] = MagicMock()

# Mock specific classes that are instantiated
mock_embeddings = MagicMock()
sys.modules["langchain_openai"].OpenAIEmbeddings.return_value = mock_embeddings

mock_splitter = MagicMock()
sys.modules["langchain_text_splitters"].RecursiveCharacterTextSplitter.return_value = mock_splitter

mock_chroma = MagicMock()
sys.modules["langchain_community.vectorstores"].Chroma = mock_chroma

mock_loader = MagicMock()
sys.modules["langchain_community.document_loaders"].TextLoader = mock_loader

# Now we can safely import the module under test
# We need to add src to path first
sys.path.append(os.path.join(os.getcwd(), "src"))
try:
    from src.rag.knowledge_base import KnowledgeBaseBuilder
except ImportError as e:
    # Fallback if src is not a package or path issue
    import importlib.util
    spec = importlib.util.spec_from_file_location("knowledge_base", "src/rag/knowledge_base.py")
    knowledge_base = importlib.util.module_from_spec(spec)
    sys.modules["src.rag.knowledge_base"] = knowledge_base
    spec.loader.exec_module(knowledge_base)
    KnowledgeBaseBuilder = knowledge_base.KnowledgeBaseBuilder

class TestKnowledgeBaseBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = KnowledgeBaseBuilder()
        
    @patch("os.listdir")
    @patch("os.path.exists")
    def test_build_flow(self, mock_exists, mock_listdir):
        # Setup mocks
        mock_exists.return_value = True
        mock_listdir.return_value = ["security_best_practices.md", "ignore_me.py"]
        
        # Mock loader instance
        loader_instance = mock_loader.return_value
        doc_mock = MagicMock()
        doc_mock.metadata = {}
        loader_instance.load.return_value = [doc_mock]
        
        # Mock splitter
        mock_splitter.split_documents.return_value = ["chunk1", "chunk2"]
        
        # Run build
        self.builder.build()
        
        # Verify Loader was called for the .md file
        mock_loader.assert_called() 
        # Verify category inference
        self.assertEqual(doc_mock.metadata["category"], "security")
        
        # Verify Splitter was called
        mock_splitter.split_documents.assert_called_with([doc_mock])
        
        # Verify Chroma DB creation was called
        mock_chroma.from_documents.assert_called_with(
            documents=["chunk1", "chunk2"],
            embedding=mock_embeddings,
            persist_directory=self.builder.db_dir
        )
        print("\nSUCCESS: KnowledgeBaseBuilder logic verified (Mocks used for dependencies).")

if __name__ == "__main__":
    unittest.main()

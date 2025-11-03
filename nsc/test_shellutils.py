#!/usr/bin/env python3
"""
OBINexus ShellUtils Test Suite
===============================
Comprehensive tests for NexusSearch, file archiving, and witness pattern
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from pheno_nexus_search import (
    NexusSearchAVL,
    PhenoToken,
    TokenType,
    WitnessState,
    AVLTrieNode
)
from file_archiver import (
    PlatformAwareArchiver,
    FileType,
    PlatformType,
    FileDescriptor
)
from obinexus_shellutils import OBINexusShellUtils


class TestPhenoToken(unittest.TestCase):
    """Test Pheno Token system"""
    
    def test_token_creation(self):
        """Test basic token creation"""
        token = PhenoToken(
            token_type=TokenType.WORD,
            token_value="test",
            token_memory_index=1
        )
        self.assertEqual(token.token_type, TokenType.WORD)
        self.assertEqual(token.token_value, "test")
        self.assertEqual(token.token_memory_index, 1)
        self.assertEqual(token.witness_state, WitnessState.UNOBSERVED)
    
    def test_epsilon_state(self):
        """Test state minimization to epsilon"""
        token = PhenoToken(TokenType.WORD, "test", 1)
        epsilon = token.to_epsilon()
        
        self.assertEqual(epsilon.token_type, TokenType.EPSILON)
        self.assertIsNone(epsilon.token_value)
        self.assertEqual(epsilon.token_memory_index, 1)


class TestAVLTrieNode(unittest.TestCase):
    """Test AVL Trie Node structure"""
    
    def test_node_creation(self):
        """Test basic node creation"""
        node = AVLTrieNode('a')
        self.assertEqual(node.char, 'a')
        self.assertEqual(node.height, 1)
        self.assertEqual(node.balance_factor, 0)
        self.assertFalse(node.is_end_of_word)
    
    def test_witness_sets(self):
        """Test witness set functionality"""
        node = AVLTrieNode('t')
        token = PhenoToken(TokenType.CHARACTER, 't', 1)
        
        node.witness_set_primary.add(token)
        self.assertEqual(len(node.witness_set_primary), 1)
        self.assertIn(token, node.witness_set_primary)


class TestNexusSearchAVL(unittest.TestCase):
    """Test NexusSearch AVL trie implementation"""
    
    def setUp(self):
        """Set up test search engine"""
        self.search = NexusSearchAVL()
    
    def test_insert_word(self):
        """Test word insertion"""
        token = self.search.insert_word("cat", "doc1", 0)
        
        self.assertIsNotNone(token)
        self.assertEqual(token.token_type, TokenType.WORD)
        self.assertEqual(token.token_value, "cat")
        self.assertEqual(token.witness_state, WitnessState.CHANGED)
    
    def test_search_bfs(self):
        """Test BFS search"""
        # Insert test words
        words = ["cat", "cats", "dog", "dot", "cattle"]
        for i, word in enumerate(words):
            self.search.insert_word(word, f"doc{i}", i)
        
        # Search for "cat"
        results = self.search.search_bfs("cat", max_results=5)
        
        self.assertGreater(len(results), 0)
        
        # First result should be exact match with score 1.0
        word, score = results[0]
        self.assertEqual(word, "cat")
        self.assertEqual(score, 1.0)
    
    def test_search_dfs(self):
        """Test DFS search"""
        words = ["apple", "application", "apply"]
        for i, word in enumerate(words):
            self.search.insert_word(word, f"doc{i}", i)
        
        results = self.search.search_dfs("app", max_results=3)
        
        self.assertGreater(len(results), 0)
        # All results should start with "app"
        for word, score in results:
            self.assertTrue(word.startswith("app"))
    
    def test_event_bubbling(self):
        """Test actor model event bubbling"""
        token = self.search.insert_word("test", "doc1", 0)
        
        # Check that event was queued
        events = self.search.process_event_queue()
        self.assertGreater(len(events), 0)
        
        # Verify event structure
        event = events[0]
        self.assertIn('token', event)
        self.assertIn('old_state', event)
        self.assertIn('new_state', event)
    
    def test_levenshtein_distance(self):
        """Test edit distance calculation"""
        distance = self.search._levenshtein_distance("cat", "hat")
        self.assertEqual(distance, 1)
        
        distance = self.search._levenshtein_distance("kitten", "sitting")
        self.assertEqual(distance, 3)


class TestPlatformAwareArchiver(unittest.TestCase):
    """Test platform-aware file archiving"""
    
    def setUp(self):
        """Create temporary directory for tests"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.archiver = PlatformAwareArchiver(base_dir=self.temp_dir)
        
        # Create test files
        (self.temp_dir / "test.md").write_text("# Test Markdown")
        (self.temp_dir / "test.pdf").write_bytes(b"%PDF-1.4\ntest")
        (self.temp_dir / "test.txt").write_text("Test text")
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)
    
    def test_platform_detection(self):
        """Test platform detection"""
        self.assertIn(self.archiver.platform, 
                     [PlatformType.WINDOWS, PlatformType.UNIX, PlatformType.UNKNOWN])
    
    def test_file_type_detection(self):
        """Test file type detection"""
        md_file = self.temp_dir / "test.md"
        pdf_file = self.temp_dir / "test.pdf"
        
        md_type = self.archiver._get_file_type(md_file)
        pdf_type = self.archiver._get_file_type(pdf_file)
        
        self.assertEqual(md_type, FileType.MARKDOWN)
        self.assertEqual(pdf_type, FileType.PDF)
    
    def test_duplicate_name_generation(self):
        """Test platform-specific duplicate name generation"""
        original = self.temp_dir / "document.md"
        
        # Test copy 1
        dup1 = self.archiver.generate_duplicate_name(original, 1)
        self.assertNotEqual(str(dup1), str(original))
        
        # Test copy 2
        dup2 = self.archiver.generate_duplicate_name(original, 2)
        self.assertNotEqual(str(dup2), str(dup1))
    
    def test_file_duplication(self):
        """Test actual file duplication"""
        source = self.temp_dir / "test.md"
        duplicate = self.archiver.duplicate_file(source)
        
        self.assertTrue(duplicate.exists())
        self.assertNotEqual(duplicate, source)
        
        # Verify content is same
        self.assertEqual(source.read_text(), duplicate.read_text())
    
    def test_directory_scan(self):
        """Test directory scanning"""
        files = self.archiver.scan_directory(
            directory=self.temp_dir,
            file_types={FileType.MARKDOWN, FileType.PDF}
        )
        
        self.assertGreater(len(files), 0)
        
        # Verify we found markdown and PDF
        types_found = {f.file_type for f in files}
        self.assertIn(FileType.MARKDOWN, types_found)
        self.assertIn(FileType.PDF, types_found)
    
    def test_archive_creation(self):
        """Test archive creation"""
        archives = self.archiver.create_archive(
            output_name="test_archive",
            separate_by_editability=True
        )
        
        # Should have created editable and non-editable archives
        self.assertIn('editable', archives)
        self.assertIn('non_editable', archives)
        
        # Verify archives exist
        for archive_type, archive_path in archives.items():
            self.assertTrue(archive_path.exists())
            self.assertTrue(archive_path.name.endswith('.zip'))


class TestOBINexusShellUtils(unittest.TestCase):
    """Test integrated shellutils module"""
    
    def setUp(self):
        """Create temporary directory and test files"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.utils = OBINexusShellUtils(base_dir=self.temp_dir)
        
        # Create test documents
        (self.temp_dir / "doc1.md").write_text("# Document One\nNexus search system")
        (self.temp_dir / "doc2.md").write_text("# Document Two\nAVL tree algorithms")
        (self.temp_dir / "doc3.txt").write_text("Testing the nexus framework")
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)
    
    def test_document_indexing(self):
        """Test document indexing"""
        doc_path = self.temp_dir / "doc1.md"
        doc_index = self.utils.index_document(doc_path)
        
        self.assertIsNotNone(doc_index)
        self.assertEqual(doc_index.file_path, doc_path)
        self.assertGreater(len(doc_index.tokens), 0)
    
    def test_directory_indexing(self):
        """Test directory indexing"""
        indexed = self.utils.index_directory(directory=self.temp_dir)
        
        self.assertGreater(len(indexed), 0)
        self.assertEqual(len(self.utils.document_index), len(indexed))
    
    def test_search_functionality(self):
        """Test search across indexed documents"""
        # Index directory first
        self.utils.index_directory(directory=self.temp_dir)
        
        # Search for "nexus"
        results = self.utils.search("nexus", algorithm='bfs', max_results=5)
        
        self.assertGreater(len(results), 0)
        
        # Verify results contain "nexus"
        found_nexus = any("nexus" in word.lower() for word, _, _ in results)
        self.assertTrue(found_nexus)
    
    def test_statistics(self):
        """Test statistics generation"""
        self.utils.index_directory(directory=self.temp_dir)
        
        stats = self.utils.get_statistics()
        
        self.assertIn('files', stats)
        self.assertIn('search', stats)
        self.assertIn('platform', stats)
        
        self.assertGreater(stats['search']['indexed_documents'], 0)
        self.assertGreater(stats['search']['total_tokens'], 0)


def run_all_tests():
    """Run all test suites"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPhenoToken))
    suite.addTests(loader.loadTestsFromTestCase(TestAVLTrieNode))
    suite.addTests(loader.loadTestsFromTestCase(TestNexusSearchAVL))
    suite.addTests(loader.loadTestsFromTestCase(TestPlatformAwareArchiver))
    suite.addTests(loader.loadTestsFromTestCase(TestOBINexusShellUtils))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)

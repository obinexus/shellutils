#!/usr/bin/env python3
"""
OBINexus Integrated Shellutils Module
======================================
Combines NexusSearch AVL trie, file archiving, and witness pattern
for comprehensive document management and search.

Main Components:
1. PhenoNexusSearch - AVL trie search with witness pattern
2. PlatformAwareArchiver - File duplication and archiving
3. WitnessActorModel - Event bubbling and state management
"""

from pheno_nexus_search import (
    NexusSearchAVL,
    PhenoToken,
    TokenType,
    WitnessState,
    AVLTrieNode
)
from file_archiver import (
    PlatformAwareArchiver,
    FileDescriptor,
    FileType,
    PlatformType
)
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
import json


@dataclass
class DocumentIndex:
    """Document index entry for NexusSearch"""
    doc_id: str
    file_path: Path
    file_type: FileType
    tokens: List[PhenoToken]
    checksum: str


class OBINexusShellUtils:
    """
    Integrated shellutils for OBINexus framework
    Provides unified interface for search, archiving, and file management
    """
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path.cwd()
        self.search_engine = NexusSearchAVL()
        self.archiver = PlatformAwareArchiver(base_dir=self.base_dir)
        self.document_index: Dict[str, DocumentIndex] = {}
        
    def index_document(self, file_path: Path) -> DocumentIndex:
        """
        Index a document for search
        Extracts words and creates Pheno tokens
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        # Register file in archiver
        descriptor = self.archiver.register_file(file_path)
        
        # Read document content
        try:
            content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            print(f"Warning: Could not read {file_path} as text (binary file?)")
            content = ""
        
        # Tokenize and index
        words = self._tokenize_content(content)
        tokens = []
        
        for i, word in enumerate(words):
            token = self.search_engine.insert_word(
                word,
                doc_id=str(file_path),
                position=i
            )
            tokens.append(token)
        
        # Create document index entry
        doc_index = DocumentIndex(
            doc_id=str(file_path),
            file_path=file_path,
            file_type=descriptor.file_type,
            tokens=tokens,
            checksum=descriptor.checksum
        )
        
        self.document_index[str(file_path)] = doc_index
        return doc_index
    
    def _tokenize_content(self, content: str) -> List[str]:
        """Simple tokenization - split on whitespace and punctuation"""
        import re
        # Split on whitespace and common punctuation
        words = re.findall(r'\b\w+\b', content.lower())
        return words
    
    def index_directory(self, directory: Path = None, 
                       file_types: Set[FileType] = None) -> List[DocumentIndex]:
        """
        Index all documents in directory
        Returns list of DocumentIndex entries
        """
        directory = directory or self.base_dir
        file_types = file_types or {FileType.MARKDOWN, FileType.TEXT, FileType.PDF}
        
        # Scan directory
        file_descriptors = self.archiver.scan_directory(
            directory=directory,
            file_types=file_types
        )
        
        # Index each file
        indexed_docs = []
        for descriptor in file_descriptors:
            try:
                doc_index = self.index_document(descriptor.path)
                indexed_docs.append(doc_index)
                print(f"Indexed: {descriptor.path.name} "
                      f"({len(doc_index.tokens)} tokens)")
            except Exception as e:
                print(f"Warning: Failed to index {descriptor.path}: {e}")
        
        return indexed_docs
    
    def search(self, query: str, algorithm: str = 'bfs', 
               max_results: int = 10) -> List[Tuple[str, float, Path]]:
        """
        Search indexed documents
        Returns: List of (word, score, document_path) tuples
        """
        if algorithm.lower() == 'bfs':
            results = self.search_engine.search_bfs(query, max_results)
        else:
            results = self.search_engine.search_dfs(query, max_results)
        
        # Enhance results with document information
        enhanced_results = []
        for word, score in results:
            # Find documents containing this word
            docs = self._find_documents_with_word(word)
            for doc_path in docs:
                enhanced_results.append((word, score, doc_path))
        
        return enhanced_results
    
    def _find_documents_with_word(self, word: str) -> List[Path]:
        """Find all documents containing a specific word"""
        matching_docs = []
        for doc_index in self.document_index.values():
            for token in doc_index.tokens:
                if token.token_value == word:
                    matching_docs.append(doc_index.file_path)
                    break
        return matching_docs
    
    def create_duplicate(self, file_path: Path) -> Path:
        """Create platform-aware duplicate of file"""
        return self.archiver.duplicate_file(file_path)
    
    def create_archive(self, output_name: str, 
                      separate_by_editability: bool = True) -> Dict[str, Path]:
        """Create archive of indexed documents"""
        files = [doc.file_path for doc in self.document_index.values()]
        return self.archiver.create_archive(
            output_name=output_name,
            files=files,
            separate_by_editability=separate_by_editability
        )
    
    def export_index(self, output_path: Path):
        """Export document index to JSON"""
        export_data = {
            'base_dir': str(self.base_dir),
            'platform': self.archiver.platform.name,
            'documents': []
        }
        
        for doc_index in self.document_index.values():
            doc_data = {
                'doc_id': doc_index.doc_id,
                'file_path': str(doc_index.file_path),
                'file_type': doc_index.file_type.name,
                'token_count': len(doc_index.tokens),
                'checksum': doc_index.checksum
            }
            export_data['documents'].append(doc_data)
        
        output_path.write_text(json.dumps(export_data, indent=2))
        print(f"Exported index to: {output_path}")
    
    def get_statistics(self) -> Dict[str, any]:
        """Get comprehensive statistics"""
        file_summary = self.archiver.get_file_summary()
        
        total_tokens = sum(len(doc.tokens) for doc in self.document_index.values())
        
        search_stats = {
            'indexed_documents': len(self.document_index),
            'total_tokens': total_tokens,
            'unique_words': self.search_engine.memory_allocator,
            'pending_events': len(self.search_engine.actor_event_queue)
        }
        
        return {
            'files': file_summary,
            'search': search_stats,
            'platform': self.archiver.platform.name
        }


def main():
    """Command-line interface for OBINexus shellutils"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description='OBINexus Integrated Shellutils - Search, Archive, Manage'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Index documents for search')
    index_parser.add_argument('directory', type=Path, nargs='?', default=Path.cwd())
    index_parser.add_argument('--export', type=Path, help='Export index to JSON')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search indexed documents')
    search_parser.add_argument('query', type=str, help='Search query')
    search_parser.add_argument('--algorithm', choices=['bfs', 'dfs'], default='bfs')
    search_parser.add_argument('--max', type=int, default=10, help='Max results')
    
    # Archive command
    archive_parser = subparsers.add_parser('archive', help='Create archive')
    archive_parser.add_argument('--output', type=str, default='nexus_archive')
    archive_parser.add_argument('--combined', action='store_true', 
                               help='Create single combined archive')
    
    # Duplicate command
    dup_parser = subparsers.add_parser('duplicate', help='Duplicate file')
    dup_parser.add_argument('file', type=Path, help='File to duplicate')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Initialize shellutils
    utils = OBINexusShellUtils()
    
    if args.command == 'index':
        print(f"Indexing directory: {args.directory}")
        indexed = utils.index_directory(args.directory)
        print(f"\nIndexed {len(indexed)} documents")
        
        if args.export:
            utils.export_index(args.export)
        
        stats = utils.get_statistics()
        print(f"\nStatistics:")
        print(f"  Total tokens: {stats['search']['total_tokens']}")
        print(f"  Unique words: {stats['search']['unique_words']}")
    
    elif args.command == 'search':
        # Must index first
        print("Indexing current directory...")
        utils.index_directory()
        
        print(f"\nSearching for: '{args.query}' (algorithm: {args.algorithm})")
        results = utils.search(args.query, algorithm=args.algorithm, 
                             max_results=args.max)
        
        print(f"\nFound {len(results)} results:")
        for word, score, doc_path in results[:args.max]:
            print(f"  {word} ({score:.3f}) in {doc_path.name}")
    
    elif args.command == 'archive':
        # Index directory first
        print("Indexing for archive...")
        utils.index_directory()
        
        archives = utils.create_archive(
            output_name=args.output,
            separate_by_editability=not args.combined
        )
        
        print(f"\nArchives created:")
        for archive_type, archive_path in archives.items():
            print(f"  {archive_type}: {archive_path}")
    
    elif args.command == 'duplicate':
        if not args.file.exists():
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        
        duplicate_path = utils.create_duplicate(args.file)
        print(f"Created duplicate: {duplicate_path}")
    
    elif args.command == 'stats':
        # Index current directory
        print("Indexing current directory...")
        utils.index_directory()
        
        stats = utils.get_statistics()
        print("\n=== OBINexus Shellutils Statistics ===")
        print(f"\nPlatform: {stats['platform']}")
        print(f"\nFiles:")
        print(f"  Total: {stats['files']['total_files']}")
        print(f"  Editable: {stats['files']['editable']}")
        print(f"  Non-editable: {stats['files']['non_editable']}")
        print(f"  Size: {stats['files']['total_size_mb']:.2f} MB")
        print(f"\nSearch Index:")
        print(f"  Documents: {stats['search']['indexed_documents']}")
        print(f"  Tokens: {stats['search']['total_tokens']}")
        print(f"  Unique words: {stats['search']['unique_words']}")


if __name__ == '__main__':
    main()

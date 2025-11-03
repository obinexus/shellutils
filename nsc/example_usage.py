#!/usr/bin/env python3
"""
OBINexus ShellUtils - Example Usage
====================================
Demonstrates all major features of the shellutils module
"""

from pathlib import Path
import tempfile
import shutil
from obinexus_shellutils import OBINexusShellUtils


def example_1_basic_search():
    """Example 1: Basic search functionality"""
    print("=" * 60)
    print("Example 1: Basic NexusSearch with AVL Trie")
    print("=" * 60)
    
    from pheno_nexus_search import NexusSearchAVL
    
    search = NexusSearchAVL()
    
    # Insert test words
    words = ["nexus", "search", "algorithm", "avl", "tree", "trie", "nexuslink"]
    print("\nInserting words:")
    for i, word in enumerate(words):
        token = search.insert_word(word, f"doc_{i}", i)
        print(f"  {word} -> Memory Index: {token.token_memory_index}")
    
    # Search using BFS
    print("\nBFS Search for 'nexus':")
    results = search.search_bfs("nexus", max_results=5)
    for word, score in results:
        print(f"  {word}: {score:.3f}")
    
    # Search using DFS
    print("\nDFS Search for 'algorithm':")
    results = search.search_dfs("algorithm", max_results=5)
    for word, score in results:
        print(f"  {word}: {score:.3f}")
    
    # Process event queue
    print("\nProcessing event queue...")
    events = search.process_event_queue()
    print(f"  Processed {len(events)} events")
    print()


def example_2_file_duplication():
    """Example 2: Platform-aware file duplication"""
    print("=" * 60)
    print("Example 2: Platform-Aware File Duplication")
    print("=" * 60)
    
    from file_archiver import PlatformAwareArchiver
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        archiver = PlatformAwareArchiver(base_dir=temp_dir)
        
        # Create test file
        test_file = temp_dir / "document.md"
        test_file.write_text("# Test Document\nSample content")
        
        print(f"\nPlatform detected: {archiver.platform.name}")
        print(f"Original file: {test_file.name}")
        
        # Create duplicates
        print("\nCreating duplicates:")
        for i in range(3):
            duplicate = archiver.duplicate_file(test_file)
            print(f"  Copy {i+1}: {duplicate.name}")
        
        # Get file summary
        summary = archiver.get_file_summary()
        print(f"\nFile Summary:")
        print(f"  Total files: {summary['total_files']}")
        print(f"  Editable: {summary['editable']}")
        print()
        
    finally:
        shutil.rmtree(temp_dir)


def example_3_archive_creation():
    """Example 3: Creating archives with separation"""
    print("=" * 60)
    print("Example 3: Archive Creation with Editability Separation")
    print("=" * 60)
    
    from file_archiver import PlatformAwareArchiver
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        archiver = PlatformAwareArchiver(base_dir=temp_dir)
        
        # Create test files
        (temp_dir / "doc1.md").write_text("# Markdown Document 1")
        (temp_dir / "doc2.md").write_text("# Markdown Document 2")
        (temp_dir / "doc3.txt").write_text("Text Document")
        (temp_dir / "report.pdf").write_bytes(b"%PDF-1.4\nFake PDF")
        
        print("\nCreated test files:")
        print("  doc1.md (editable)")
        print("  doc2.md (editable)")
        print("  doc3.txt (editable)")
        print("  report.pdf (non-editable)")
        
        # Create archives with separation
        print("\nCreating archives...")
        archives = archiver.create_archive(
            output_name="example_archive",
            separate_by_editability=True
        )
        
        print("\nArchives created:")
        for archive_type, archive_path in archives.items():
            size_kb = archive_path.stat().st_size / 1024
            print(f"  {archive_type}: {archive_path.name} ({size_kb:.2f} KB)")
        
        # Cleanup archives
        for archive_path in archives.values():
            archive_path.unlink()
        
        print()
        
    finally:
        shutil.rmtree(temp_dir)


def example_4_integrated_search():
    """Example 4: Integrated document search"""
    print("=" * 60)
    print("Example 4: Integrated Document Search")
    print("=" * 60)
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        utils = OBINexusShellUtils(base_dir=temp_dir)
        
        # Create test documents
        docs = {
            "nexus_intro.md": "# NexusSearch\nAVL trie-based search system",
            "algorithm.md": "# Algorithms\nBFS and DFS traversal methods",
            "witness.md": "# Witness Pattern\nActor model with event bubbling",
            "guide.txt": "User guide for nexus framework installation"
        }
        
        print("\nCreating test documents:")
        for filename, content in docs.items():
            doc_path = temp_dir / filename
            doc_path.write_text(content)
            print(f"  {filename}")
        
        # Index directory
        print("\nIndexing documents...")
        indexed = utils.index_directory(directory=temp_dir)
        print(f"  Indexed {len(indexed)} documents")
        
        # Search examples
        queries = ["nexus", "algorithm", "witness"]
        
        for query in queries:
            print(f"\nSearch for '{query}':")
            results = utils.search(query, algorithm='bfs', max_results=3)
            for word, score, doc_path in results[:3]:
                print(f"  {word} ({score:.3f}) in {doc_path.name}")
        
        # Get statistics
        print("\nStatistics:")
        stats = utils.get_statistics()
        print(f"  Documents indexed: {stats['search']['indexed_documents']}")
        print(f"  Total tokens: {stats['search']['total_tokens']}")
        print(f"  Unique words: {stats['search']['unique_words']}")
        print()
        
    finally:
        shutil.rmtree(temp_dir)


def example_5_witness_pattern():
    """Example 5: Witness pattern and event bubbling"""
    print("=" * 60)
    print("Example 5: Witness Pattern and Event Bubbling")
    print("=" * 60)
    
    from pheno_nexus_search import (
        NexusSearchAVL,
        PhenoToken,
        TokenType,
        WitnessState
    )
    
    search = NexusSearchAVL()
    
    print("\nCreating tokens with witness states:")
    
    # Create tokens with different states
    tokens = []
    words = ["actor", "witness", "event", "bubble"]
    
    for word in words:
        token = search.insert_word(word, "example_doc", 0)
        tokens.append(token)
        print(f"  {word}: {token.witness_state.name}")
    
    # Process event queue
    print("\nProcessing event bubbling:")
    events = search.process_event_queue()
    
    for i, event in enumerate(events, 1):
        token = event['token']
        print(f"  Event {i}: {token.token_value} "
              f"({event['old_state'].name} -> {event['new_state'].name})")
    
    # Show witness state for a token
    if tokens:
        token = tokens[0]
        state = search.get_witness_state(token)
        print(f"\nWitness State for '{token.token_value}':")
        print(f"  State: {state['state'].name}")
        print(f"  Memory Index: {state['memory_index']}")
        print(f"  Pending Events: {state['events_pending']}")
    
    print()


def example_6_state_minimization():
    """Example 6: State machine minimization"""
    print("=" * 60)
    print("Example 6: State Machine Minimization (Epsilon States)")
    print("=" * 60)
    
    from pheno_nexus_search import PhenoToken, TokenType, WitnessState
    
    print("\nDemonstrating state minimization:")
    
    # Create regular token
    token = PhenoToken(
        token_type=TokenType.WORD,
        token_value="complex_state",
        token_memory_index=42,
        witness_state=WitnessState.OBSERVED
    )
    
    print("\nOriginal Token:")
    print(f"  Type: {token.token_type.name}")
    print(f"  Value: {token.token_value}")
    print(f"  Memory: {token.token_memory_index}")
    print(f"  State: {token.witness_state.name}")
    
    # Minimize to epsilon state
    epsilon_token = token.to_epsilon()
    
    print("\nMinimized (Epsilon) Token:")
    print(f"  Type: {epsilon_token.token_type.name}")
    print(f"  Value: {epsilon_token.token_value}")
    print(f"  Memory: {epsilon_token.token_memory_index}")
    print(f"  State: {epsilon_token.witness_state.name}")
    
    print("\nState minimization preserves memory index while reducing state complexity")
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("OBINexus ShellUtils - Complete Examples")
    print("=" * 60)
    print()
    
    try:
        example_1_basic_search()
        example_2_file_duplication()
        example_3_archive_creation()
        example_4_integrated_search()
        example_5_witness_pattern()
        example_6_state_minimization()
        
        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        print()
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        raise


if __name__ == '__main__':
    main()

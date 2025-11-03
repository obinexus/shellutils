# OBINexus ShellUtils

**Integrated shellutils for OBINexus framework with NexusSearch and file management**

## Overview

OBINexus ShellUtils provides a comprehensive toolkit for document management, search, and archiving based on the OBINexus framework principles:

- **NexusSearch**: AVL trie-based search with character-level witnessing
- **Pheno Token System**: Type-Value-Memory separation for state machine minimization
- **Platform-Aware Duplication**: Windows vs Unix/Linux naming conventions
- **Actor Model**: Event bubbling for state observation
- **File Archiving**: Intelligent separation of editable/non-editable documents

## Architecture

### Core Components

1. **Pheno Token System** (`pheno_nexus_search.py`)
   - Token structure: `(Type, Value, Memory_Index)`
   - State machine minimization (epsilon states)
   - Witness pattern for state observation

2. **AVL Trie NexusSearch** (`pheno_nexus_search.py`)
   - Self-balancing trie with O(log n) operations
   - BFS/DFS traversal algorithms
   - A* scoring for relevance ranking
   - Dual witness sets (primary/secondary)

3. **Platform-Aware Archiver** (`file_archiver.py`)
   - Windows: `filename-copy.ext` → `filename-copy2.ext`
   - Unix/Linux: `filename2.ext` → `filename3.ext`
   - Automatic editability detection
   - ZIP archive creation

4. **Integrated Module** (`obinexus_shellutils.py`)
   - Unified interface for all operations
   - Document indexing and search
   - Archive management
   - Statistics and reporting

## Installation

### Using pip

```bash
pip install obinexus-shellutils
```

### From source

```bash
git clone https://github.com/obinexus/shellutils.git
cd shellutils
python setup.py install
```

### Shell scripts only

```bash
curl -O https://raw.githubusercontent.com/obinexus/shellutils/main/shellutils.sh
chmod +x shellutils.sh
```

## Quick Start

### Python API

```python
from obinexus_shellutils import OBINexusShellUtils
from pathlib import Path

# Initialize
utils = OBINexusShellUtils(base_dir=Path.cwd())

# Index documents
indexed_docs = utils.index_directory()
print(f"Indexed {len(indexed_docs)} documents")

# Search (BFS algorithm)
results = utils.search("nexus", algorithm='bfs', max_results=10)
for word, score, doc_path in results:
    print(f"{word} ({score:.3f}) in {doc_path.name}")

# Create archive
archives = utils.create_archive(
    output_name="my_docs",
    separate_by_editability=True
)

# Duplicate file (platform-aware)
duplicate_path = utils.create_duplicate(Path("document.md"))
print(f"Created: {duplicate_path}")
```

### Command Line

```bash
# Index current directory
obinexus-shellutils index ./docs --export index.json

# Search indexed documents
obinexus-shellutils search "algorithm" --algorithm bfs --max 10

# Create archive
obinexus-shellutils archive --output my_archive --combined

# Duplicate file
obinexus-shellutils duplicate document.md

# Show statistics
obinexus-shellutils stats
```

### Shell Script

```bash
# Scan directory
./shellutils.sh scan ./documentation

# Duplicate file
./shellutils.sh duplicate report.pdf

# Create archive
./shellutils.sh archive ./docs nexus_docs

# Check platform
./shellutils.sh platform
```

## Technical Details

### NexusSearch Algorithm

The NexusSearch implementation uses an AVL-balanced trie structure where:

1. **Characters as Witnesses**: Each character in the trie is witnessed by Pheno tokens
2. **Dual Witness Sets**: Primary and secondary witness sets track state changes
3. **BFS/DFS Traversal**: Choose algorithm based on use case:
   - **BFS**: Better for relevance (explores breadth-first)
   - **DFS**: Faster for first match (explores depth-first)
4. **A* Scoring**: Multi-factor relevance scoring:
   - Exact match: 1.0
   - Prefix match: 0.9
   - Contains match: 0.7
   - Edit distance similarity
   - Depth penalty

### Pheno Token Structure

```python
@dataclass
class PhenoToken:
    token_type: TokenType      # FILE, DIRECTORY, CHARACTER, WORD, etc.
    token_value: Any           # Actual content
    token_memory_index: int    # Allocated memory index
    witness_state: WitnessState  # UNOBSERVED, OBSERVED, CHANGED, BUBBLING
```

### State Machine Minimization

Based on OBINexus principles, the system implements state machine minimization:

- **Epsilon States**: Empty states representing minimized/reduced states
- **Type-Value-Memory Separation**: Compile-time safety through separation
- **Witness Pattern**: Observer pattern for state changes
- **Event Bubbling**: Events propagate upward, not downstream

### AVL Rotations

Four rotation types maintain balance:

1. **Left-Left (LL)**: Right rotation
2. **Right-Right (RR)**: Left rotation
3. **Left-Right (LR)**: Left rotation on child, then right on node
4. **Right-Left (RL)**: Right rotation on child, then left on node

Balance factor: `left_height - right_height ∈ [-1, +1]`

### Platform-Specific Naming

| Platform | Original | Copy 1 | Copy 2 |
|----------|----------|--------|--------|
| Windows | `doc.md` | `doc-copy.md` | `doc-copy2.md` |
| Unix/Linux | `doc.md` | `doc2.md` | `doc3.md` |

## Use Cases

### 1. Documentation Management

```python
utils = OBINexusShellUtils(base_dir=Path("./docs"))

# Index all markdown and PDF files
utils.index_directory()

# Search documentation
results = utils.search("installation guide", algorithm='bfs')

# Create separate archives for different file types
archives = utils.create_archive(
    output_name="project_docs",
    separate_by_editability=True
)
# Creates: project_docs_editable.zip, project_docs_non_editable.zip
```

### 2. Research Paper Organization

```python
from file_archiver import PlatformAwareArchiver, FileType

archiver = PlatformAwareArchiver(base_dir=Path("./research"))

# Scan for papers
papers = archiver.scan_directory(file_types={FileType.PDF})

# Create backups with versioning
for paper_desc in papers:
    backup = archiver.duplicate_file(paper_desc.path)
    print(f"Backup created: {backup}")

# Archive by category
archives = archiver.create_archive(
    output_name="research_2025",
    separate_by_editability=False
)
```

### 3. Code Documentation Search

```python
from pheno_nexus_search import NexusSearchAVL, TokenType

search = NexusSearchAVL()

# Index code documentation
docs = ["README.md", "API.md", "USAGE.md", "CONTRIBUTING.md"]
for doc_path in docs:
    content = Path(doc_path).read_text()
    words = content.lower().split()
    for word in words:
        search.insert_word(word, doc_path)

# Search with BFS
results_bfs = search.search_bfs("authentication", max_results=5)

# Search with DFS
results_dfs = search.search_dfs("api", max_results=5)
```

## API Reference

### OBINexusShellUtils

**Main integrated interface**

#### Methods

- `index_document(file_path)` → DocumentIndex
- `index_directory(directory, file_types)` → List[DocumentIndex]
- `search(query, algorithm, max_results)` → List[Tuple[str, float, Path]]
- `create_duplicate(file_path)` → Path
- `create_archive(output_name, separate_by_editability)` → Dict[str, Path]
- `export_index(output_path)` → None
- `get_statistics()` → Dict[str, any]

### NexusSearchAVL

**AVL trie search engine**

#### Methods

- `insert_word(word, doc_id, position)` → PhenoToken
- `search_bfs(pattern, max_results)` → List[Tuple[str, float]]
- `search_dfs(pattern, max_results)` → List[Tuple[str, float]]
- `get_witness_state(token)` → Dict[str, Any]
- `process_event_queue()` → List[Dict]

### PlatformAwareArchiver

**File duplication and archiving**

#### Methods

- `register_file(file_path)` → FileDescriptor
- `generate_duplicate_name(original_path, copy_number)` → Path
- `duplicate_file(source_path, target_path)` → Path
- `scan_directory(directory, file_types)` → List[FileDescriptor]
- `create_archive(output_name, files, separate_by_editability)` → Dict[str, Path]
- `get_file_summary()` → Dict[str, any]

## Examples

See the `examples/` directory for complete examples:

- `basic_search.py` - Simple search implementation
- `document_indexer.py` - Full document indexing system
- `archive_manager.py` - Archive creation and management
- `witness_pattern.py` - Actor model event system

## Testing

```bash
# Run all tests
pytest tests/

# With coverage
pytest --cov=. tests/

# Specific test
pytest tests/test_nexus_search.py
```

## Performance

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Insert word | O(log n * m) | O(m) |
| Search BFS | O(V + E) | O(V) |
| Search DFS | O(V + E) | O(h) |
| AVL rotation | O(1) | O(1) |
| File duplicate | O(n) | O(n) |
| Archive create | O(n * m) | O(n) |

Where:
- n = number of nodes
- m = word length
- V = vertices in trie
- E = edges in trie
- h = height of trie

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/obinexus/shellutils.git
cd shellutils
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Related Projects

- **NexusLink**: [github.com/obinexus/nexuslink](https://github.com/obinexus/nexuslink)
- **RiftLang**: [github.com/obinexus/riftlang](https://github.com/obinexus/riftlang)
- **OBINexus Framework**: [obinexus.com](https://obinexus.com)

## References

- [State Machine Minimization](docs/state_machine_minimization.md)
- [AVL Tree Algorithms](docs/avl_algorithms.md)
- [Witness Pattern](docs/witness_pattern.md)
- [Actor Model](docs/actor_model.md)

## Support

- Issues: [github.com/obinexus/shellutils/issues](https://github.com/obinexus/shellutils/issues)
- Documentation: [github.com/obinexus/shellutils/wiki](https://github.com/obinexus/shellutils/wiki)
- Email: support@obinexus.com

---

**Computing from the ❤️**  
OBINexus Computing © 2025

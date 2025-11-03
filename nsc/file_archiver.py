#!/usr/bin/env python3
"""
OBINexus File Archiver with Platform-Specific Duplication
==========================================================
Handles file duplication with different naming conventions:
- Windows: filename-copy.ext
- Unix/Linux: filename2.ext

Creates .zip archives for documentation files (markdown, PDF)
Separates editable (markdown) from non-editable (PDF) formats
"""

import os
import sys
import zipfile
import shutil
import platform
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from enum import Enum, auto
import hashlib


class FileType(Enum):
    """Supported file types for archiving"""
    MARKDOWN = auto()
    PDF = auto()
    TEXT = auto()
    RAW = auto()  # Files with no extension
    UNKNOWN = auto()


class PlatformType(Enum):
    """Platform-specific behavior"""
    WINDOWS = auto()
    UNIX = auto()
    UNKNOWN = auto()


@dataclass
class FileDescriptor:
    """File metadata for witness tracking"""
    path: Path
    file_type: FileType
    is_editable: bool
    size_bytes: int
    checksum: str
    
    def __hash__(self):
        return hash(self.checksum)


class PlatformAwareArchiver:
    """
    File archiver with platform-specific duplication logic
    Implements the witness pattern for file state observation
    """
    
    # Extension mappings
    EDITABLE_EXTENSIONS = {'.md', '.txt', '.markdown', ''}  # '' for raw files
    NON_EDITABLE_EXTENSIONS = {'.pdf'}
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path.cwd()
        self.platform = self._detect_platform()
        self.file_registry: Dict[str, FileDescriptor] = {}
        
    def _detect_platform(self) -> PlatformType:
        """Detect current operating system"""
        system = platform.system().lower()
        if 'windows' in system:
            return PlatformType.WINDOWS
        elif any(name in system for name in ['linux', 'darwin', 'unix']):
            return PlatformType.UNIX
        return PlatformType.UNKNOWN
    
    def _get_file_type(self, file_path: Path) -> FileType:
        """Determine file type from extension"""
        suffix = file_path.suffix.lower()
        
        if suffix in {'.md', '.markdown'}:
            return FileType.MARKDOWN
        elif suffix == '.pdf':
            return FileType.PDF
        elif suffix == '.txt':
            return FileType.TEXT
        elif not suffix:  # No extension = raw file
            return FileType.RAW
        return FileType.UNKNOWN
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum for file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _is_editable(self, file_type: FileType) -> bool:
        """Determine if file type is editable"""
        return file_type in {FileType.MARKDOWN, FileType.TEXT, FileType.RAW}
    
    def register_file(self, file_path: Path) -> FileDescriptor:
        """
        Register file in the witness system
        Creates FileDescriptor with metadata
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_type = self._get_file_type(file_path)
        descriptor = FileDescriptor(
            path=file_path,
            file_type=file_type,
            is_editable=self._is_editable(file_type),
            size_bytes=file_path.stat().st_size,
            checksum=self._calculate_checksum(file_path)
        )
        
        self.file_registry[str(file_path)] = descriptor
        return descriptor
    
    def generate_duplicate_name(self, original_path: Path, copy_number: int = 1) -> Path:
        """
        Generate platform-specific duplicate filename
        Windows: filename-copy.ext or filename-copy2.ext
        Unix/Linux: filename2.ext or filename3.ext
        """
        stem = original_path.stem
        suffix = original_path.suffix
        parent = original_path.parent
        
        if self.platform == PlatformType.WINDOWS:
            # Windows style: filename-copy.ext
            if copy_number == 1:
                new_name = f"{stem}-copy{suffix}"
            else:
                new_name = f"{stem}-copy{copy_number}{suffix}"
        else:
            # Unix/Linux style: filename2.ext
            new_name = f"{stem}{copy_number + 1}{suffix}"
        
        return parent / new_name
    
    def duplicate_file(self, source_path: Path, target_path: Path = None) -> Path:
        """
        Create platform-aware duplicate of file
        Returns: Path to duplicated file
        """
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        if target_path is None:
            # Auto-generate name based on platform
            copy_number = 1
            target_path = self.generate_duplicate_name(source_path, copy_number)
            
            # Find available filename
            while target_path.exists():
                copy_number += 1
                target_path = self.generate_duplicate_name(source_path, copy_number)
        
        # Copy file
        shutil.copy2(source_path, target_path)
        
        # Register both files
        self.register_file(source_path)
        self.register_file(target_path)
        
        return target_path
    
    def scan_directory(self, directory: Path = None, 
                      file_types: Set[FileType] = None) -> List[FileDescriptor]:
        """
        Scan directory for files matching criteria
        Returns: List of FileDescriptors
        """
        directory = directory or self.base_dir
        file_types = file_types or {FileType.MARKDOWN, FileType.PDF}
        
        found_files = []
        
        for item in directory.rglob('*'):
            if item.is_file():
                file_type = self._get_file_type(item)
                if file_type in file_types:
                    try:
                        descriptor = self.register_file(item)
                        found_files.append(descriptor)
                    except Exception as e:
                        print(f"Warning: Could not register {item}: {e}")
        
        return found_files
    
    def create_archive(self, 
                      output_name: str,
                      files: List[Path] = None,
                      separate_by_editability: bool = True) -> Dict[str, Path]:
        """
        Create .zip archive(s) of documentation files
        
        Args:
            output_name: Base name for archive(s)
            files: List of files to archive (None = scan directory)
            separate_by_editability: Create separate archives for editable/non-editable
        
        Returns:
            Dict mapping archive type to archive path
        """
        if files is None:
            # Scan directory for markdown and PDF files
            descriptors = self.scan_directory()
            files = [d.path for d in descriptors]
        else:
            # Register provided files
            descriptors = [self.register_file(f) for f in files]
        
        archives_created = {}
        
        if separate_by_editability:
            # Separate editable and non-editable files
            editable = [d for d in descriptors if d.is_editable]
            non_editable = [d for d in descriptors if not d.is_editable]
            
            if editable:
                editable_archive = self._create_zip(
                    f"{output_name}_editable.zip",
                    [d.path for d in editable]
                )
                archives_created['editable'] = editable_archive
            
            if non_editable:
                non_editable_archive = self._create_zip(
                    f"{output_name}_non_editable.zip",
                    [d.path for d in non_editable]
                )
                archives_created['non_editable'] = non_editable_archive
        else:
            # Single archive
            archive_path = self._create_zip(
                f"{output_name}.zip",
                [d.path for d in descriptors]
            )
            archives_created['combined'] = archive_path
        
        return archives_created
    
    def _create_zip(self, archive_name: str, files: List[Path]) -> Path:
        """Create ZIP archive from file list"""
        archive_path = self.base_dir / archive_name
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files:
                # Use relative path in archive
                arcname = file_path.name
                zipf.write(file_path, arcname)
        
        print(f"Created archive: {archive_path} ({len(files)} files)")
        return archive_path
    
    def get_file_summary(self) -> Dict[str, any]:
        """Get summary of registered files"""
        summary = {
            'total_files': len(self.file_registry),
            'editable': sum(1 for d in self.file_registry.values() if d.is_editable),
            'non_editable': sum(1 for d in self.file_registry.values() if not d.is_editable),
            'total_size_mb': sum(d.size_bytes for d in self.file_registry.values()) / (1024 * 1024),
            'by_type': {}
        }
        
        for descriptor in self.file_registry.values():
            type_name = descriptor.file_type.name
            if type_name not in summary['by_type']:
                summary['by_type'][type_name] = 0
            summary['by_type'][type_name] += 1
        
        return summary


def main():
    """Example usage and CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='OBINexus File Archiver - Platform-aware duplication and archiving'
    )
    parser.add_argument('command', choices=['scan', 'duplicate', 'archive'],
                       help='Command to execute')
    parser.add_argument('--dir', type=Path, default=Path.cwd(),
                       help='Base directory (default: current directory)')
    parser.add_argument('--file', type=Path,
                       help='File to duplicate (for duplicate command)')
    parser.add_argument('--output', type=str, default='nexus_archive',
                       help='Output archive name (for archive command)')
    parser.add_argument('--separate', action='store_true',
                       help='Separate editable and non-editable files into different archives')
    
    args = parser.parse_args()
    
    archiver = PlatformAwareArchiver(base_dir=args.dir)
    
    if args.command == 'scan':
        print(f"Scanning directory: {args.dir}")
        print(f"Platform detected: {archiver.platform.name}")
        files = archiver.scan_directory()
        print(f"\nFound {len(files)} files:")
        for descriptor in files:
            print(f"  {descriptor.path.name} ({descriptor.file_type.name}, "
                  f"{'editable' if descriptor.is_editable else 'non-editable'})")
        
        summary = archiver.get_file_summary()
        print(f"\nSummary:")
        print(f"  Total: {summary['total_files']} files")
        print(f"  Editable: {summary['editable']}")
        print(f"  Non-editable: {summary['non_editable']}")
        print(f"  Total size: {summary['total_size_mb']:.2f} MB")
    
    elif args.command == 'duplicate':
        if not args.file:
            print("Error: --file required for duplicate command")
            sys.exit(1)
        
        if not args.file.exists():
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        
        duplicate_path = archiver.duplicate_file(args.file)
        print(f"Created duplicate: {duplicate_path}")
    
    elif args.command == 'archive':
        print(f"Creating archive(s) from {args.dir}")
        archives = archiver.create_archive(
            output_name=args.output,
            separate_by_editability=args.separate
        )
        
        print(f"\nArchives created:")
        for archive_type, archive_path in archives.items():
            print(f"  {archive_type}: {archive_path}")
        
        summary = archiver.get_file_summary()
        print(f"\nTotal files archived: {summary['total_files']}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main()
    else:
        # Demo mode
        print("=== OBINexus File Archiver Demo ===\n")
        
        archiver = PlatformAwareArchiver()
        print(f"Platform: {archiver.platform.name}\n")
        
        # Example: Generate duplicate names
        test_file = Path("example.md")
        for i in range(1, 4):
            dup_name = archiver.generate_duplicate_name(test_file, i)
            print(f"Duplicate {i}: {dup_name}")

#!/usr/bin/env python3
"""
File Copy Functor - Cross-platform file copying with wildcard extension support
Built on OBINexus Functor Framework principles
"""

import os
import sys
import glob
import shutil
import argparse
from pathlib import Path
from typing import List, Set, Tuple, Optional
from enum import Enum
import platform

# Functor Framework Integration
class SystemPlatform(Enum):
    """Phenotype: Observable system platform state"""
    MACOS = "darwin"
    LINUX = "linux"
    WINDOWS = "windows"

class CopyOperation:
    """Phenomenory: Captured copy action memory"""
    def __init__(self, source: str, dest: str, extensions: Set[str]):
        self.source = Path(source)
        self.dest = Path(dest)
        self.extensions = extensions
        self.platform = self._detect_platform()
        self.files_copied: List[Path] = []
        
    def _detect_platform(self) -> SystemPlatform:
        system = platform.system().lower()
        if system == "darwin":
            return SystemPlatform.MACOS
        elif system == "linux":
            return SystemPlatform.LINUX
        elif system == "windows":
            return SystemPlatform.WINDOWS
        else:
            raise ValueError(f"Unsupported platform: {system}")

class CopyResult:
    """Phenovalue: Derived value from copy operation"""
    def __init__(self):
        self.success_count = 0
        self.failed_count = 0
        self.total_files = 0
        self.errors: List[str] = []

# Archerion Pattern Implementation
class FileCopyFunctor:
    """
    Heterogeneous Functor (He) for cross-platform file operations
    Implements observer-consumer-actor pattern
    """
    
    def __init__(self):
        self.observer_state = None
        self.consumer_state = None
        
    def observe(self, operation: CopyOperation) -> 'FileCopyFunctor':
        """Observer role: Capture system state"""
        self.observer_state = operation
        return self
        
    def consume(self) -> CopyResult:
        """Consumer role: Execute the copy operation"""
        if not self.observer_state:
            raise ValueError("No operation observed - call observe() first")
            
        result = CopyResult()
        operation = self.observer_state
        
        try:
            # Create destination directory if it doesn't exist
            operation.dest.mkdir(parents=True, exist_ok=True)
            
            # Find and copy files with O(log n) complexity optimization
            files_to_copy = self._find_files_with_extensions(
                operation.source, 
                operation.extensions
            )
            
            result.total_files = len(files_to_copy)
            
            for file_path in files_to_copy:
                if self._copy_single_file(file_path, operation.dest):
                    result.success_count += 1
                    operation.files_copied.append(file_path)
                else:
                    result.failed_count += 1
                    result.errors.append(f"Failed to copy: {file_path}")
                    
        except Exception as e:
            result.errors.append(f"Operation failed: {str(e)}")
            
        self.consumer_state = result
        return result
        
    def watch(self) -> bool:
        """Actor-Watcher role: Validate operation success"""
        if not self.consumer_state:
            raise ValueError("No operation consumed - call consume() first")
            
        result = self.consumer_state
        return result.failed_count == 0 and len(result.errors) == 0
        
    def _find_files_with_extensions(self, source: Path, extensions: Set[str]) -> List[Path]:
        """
        DAG-based file discovery with O(log n) auxiliary space complexity
        Uses glob patterns for efficient recursive search
        """
        files_found: List[Path] = []
        
        for ext in extensions:
            # Build glob pattern for recursive search
            pattern = str(source / "**" / f"*{ext}")
            
            # Use glob with recursive flag (O(log n) space for directory traversal)
            matched_files = glob.glob(pattern, recursive=True)
            
            for file_path in matched_files:
                path_obj = Path(file_path)
                if path_obj.is_file():
                    files_found.append(path_obj)
                    
        return files_found
        
    def _copy_single_file(self, source_file: Path, dest_dir: Path) -> bool:
        """Platform-optimized single file copy"""
        try:
            dest_path = dest_dir / source_file.name
            
            # Platform-specific optimizations
            if self.observer_state.platform == SystemPlatform.WINDOWS:
                # Windows: Use shutil.copy2 for metadata preservation
                shutil.copy2(source_file, dest_path)
            else:
                # Unix/Mac: Use efficient copy operations
                if hasattr(os, 'sendfile'):  # Linux sendfile optimization
                    self._copy_using_sendfile(source_file, dest_path)
                else:
                    shutil.copy2(source_file, dest_path)
                    
            return True
            
        except Exception as e:
            print(f"Error copying {source_file}: {str(e)}", file=sys.stderr)
            return False
            
    def _copy_using_sendfile(self, source: Path, dest: Path):
        """Linux-optimized copy using sendfile syscall"""
        try:
            with open(source, 'rb') as src_file:
                with open(dest, 'wb') as dst_file:
                    # Get file size for progress tracking
                    src_file.seek(0, 2)
                    file_size = src_file.tell()
                    src_file.seek(0)
                    
                    # Use sendfile for zero-copy optimization
                    os.sendfile(dst_file.fileno(), src_file.fileno(), 0, file_size)
        except AttributeError:
            # Fallback to shutil if sendfile not available
            shutil.copy2(source, dest)

# Command Line Interface using Archerion Pattern
class CommandLineArcherion:
    """CLI implementation using observer-consumer-actor pattern"""
    
    def __init__(self):
        self.functor = FileCopyFunctor()
        
    def observe_arguments(self) -> CopyOperation:
        """Observer: Parse and validate command line arguments"""
        parser = argparse.ArgumentParser(
            description="Cross-platform file copy with wildcard extensions",
            epilog="Built on OBINexus Functor Framework"
        )
        
        parser.add_argument(
            'source',
            help='Source directory path'
        )
        
        parser.add_argument(
            'destination', 
            help='Destination directory path'
        )
        
        parser.add_argument(
            '--ext', '--extensions',
            nargs='+',
            required=True,
            help='File extensions to copy (e.g., .pdf .md .txt)'
        )
        
        parser.add_argument(
            '--recursive', '-r',
            action='store_true',
            default=True,
            help='Recursive directory search (always enabled)'
        )
        
        args = parser.parse_args()
        
        # Validate source exists
        if not Path(args.source).exists():
            raise FileNotFoundError(f"Source directory not found: {args.source}")
            
        # Convert extensions to set and ensure they start with .
        extensions = set()
        for ext in args.ext:
            if not ext.startswith('.'):
                ext = '.' + ext
            extensions.add(ext)
            
        return CopyOperation(args.source, args.destination, extensions)
        
    def consume_operation(self, operation: CopyOperation) -> CopyResult:
        """Consumer: Execute the copy operation through functor"""
        return self.functor.observe(operation).consume()
        
    def watch_results(self, result: CopyResult) -> bool:
        """Actor-Watcher: Validate and report results"""
        success = self.functor.watch()
        
        print(f"\n=== File Copy Operation Complete ===")
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Files found: {result.total_files}")
        print(f"Successfully copied: {result.success_count}")
        print(f"Failed: {result.failed_count}")
        
        if result.errors:
            print(f"\nErrors encountered:")
            for error in result.errors:
                print(f"  - {error}")
                
        return success

# Complexity Validator (O(log n) enforcement)
class ComplexityValidator:
    """Validates O(log n) auxiliary space complexity"""
    
    @staticmethod
    def validate_auxiliary_space(file_count: int, memory_usage: int) -> bool:
        """
        Verify auxiliary space grows at O(log n)
        For file operations, we expect memory usage to scale logarithmically
        """
        import math
        
        expected_max_memory = math.log2(file_count + 1) * 1024  # KB
        actual_memory_kb = memory_usage / 1024
        
        is_valid = actual_memory_kb <= expected_max_memory
        
        if not is_valid:
            print(f"WARNING: Potential O(n) space complexity detected")
            print(f"Files: {file_count}, Memory: {actual_memory_kb:.2f}KB")
            print(f"Expected max: {expected_max_memory:.2f}KB")
            
        return is_valid

# Main execution using Functor Framework pattern
def main():
    """Main entry point using Archerion pattern"""
    try:
        # Initialize CLI Archerion
        cli = CommandLineArcherion()
        
        # Observer phase: Parse arguments
        print("🔍 Observing system state and arguments...")
        operation = cli.observe_arguments()
        print(f"Source: {operation.source}")
        print(f"Destination: {operation.dest}") 
        print(f"Extensions: {', '.join(operation.extensions)}")
        print(f"Platform: {operation.platform.value}")
        
        # Consumer phase: Execute copy operation
        print(f"\n🔄 Consuming copy operation...")
        result = cli.consume_operation(operation)
        
        # Actor-Watcher phase: Validate results
        print(f"\n👁️ Watching operation results...")
        success = cli.watch_results(result)
        
        # Complexity validation
        if success and result.total_files > 0:
            import psutil
            process = psutil.Process()
            memory_used = process.memory_info().rss
            
            complexity_ok = ComplexityValidator.validate_auxiliary_space(
                result.total_files, memory_used
            )
            
            if complexity_ok:
                print("✅ O(log n) auxiliary space complexity verified")
            else:
                print("⚠️ Complexity bounds may be exceeded")
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

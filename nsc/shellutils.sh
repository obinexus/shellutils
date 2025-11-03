#!/bin/bash
#
# OBINexus ShellUtils - File Duplication and Archiving
# =====================================================
# Platform-aware file duplication and archiving utilities
# Supports: Linux, macOS, WSL, Windows (via Git Bash)
#
# Usage:
#   ./shellutils.sh duplicate <file>
#   ./shellutils.sh archive <directory> <output_name>
#   ./shellutils.sh scan <directory>
#

set -euo pipefail

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Detect platform
detect_platform() {
    local platform="UNKNOWN"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        platform="UNIX"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        platform="UNIX"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
        platform="WINDOWS"
    fi
    
    echo "$platform"
}

# Generate platform-specific duplicate name
generate_duplicate_name() {
    local original="$1"
    local copy_number="${2:-1}"
    local platform=$(detect_platform)
    
    local dir=$(dirname "$original")
    local filename=$(basename "$original")
    local extension="${filename##*.}"
    local basename="${filename%.*}"
    
    # Handle files without extension
    if [[ "$basename" == "$filename" ]]; then
        extension=""
    fi
    
    local new_name=""
    if [[ "$platform" == "WINDOWS" ]]; then
        # Windows style: filename-copy.ext
        if [[ $copy_number -eq 1 ]]; then
            if [[ -n "$extension" ]]; then
                new_name="${basename}-copy.${extension}"
            else
                new_name="${basename}-copy"
            fi
        else
            if [[ -n "$extension" ]]; then
                new_name="${basename}-copy${copy_number}.${extension}"
            else
                new_name="${basename}-copy${copy_number}"
            fi
        fi
    else
        # Unix/Linux style: filename2.ext
        if [[ -n "$extension" ]]; then
            new_name="${basename}$((copy_number + 1)).${extension}"
        else
            new_name="${basename}$((copy_number + 1))"
        fi
    fi
    
    echo "${dir}/${new_name}"
}

# Find next available duplicate name
find_available_name() {
    local original="$1"
    local copy_number=1
    local new_path=""
    
    while true; do
        new_path=$(generate_duplicate_name "$original" $copy_number)
        if [[ ! -e "$new_path" ]]; then
            echo "$new_path"
            return 0
        fi
        copy_number=$((copy_number + 1))
        
        # Safety check
        if [[ $copy_number -gt 1000 ]]; then
            echo "Error: Too many copies (>1000)" >&2
            return 1
        fi
    done
}

# Duplicate file with platform-aware naming
duplicate_file() {
    local source="$1"
    
    if [[ ! -f "$source" ]]; then
        echo -e "${RED}Error: File not found: $source${NC}" >&2
        return 1
    fi
    
    local target=$(find_available_name "$source")
    
    if [[ $? -ne 0 ]]; then
        return 1
    fi
    
    cp -p "$source" "$target"
    echo -e "${GREEN}Created duplicate: $target${NC}"
    echo "$target"
}

# Scan directory for documentation files
scan_directory() {
    local dir="${1:-.}"
    local platform=$(detect_platform)
    
    echo -e "${BLUE}=== Scanning Directory ===${NC}"
    echo "Directory: $dir"
    echo "Platform: $platform"
    echo ""
    
    local markdown_count=0
    local pdf_count=0
    local txt_count=0
    local raw_count=0
    
    echo "Markdown files (.md):"
    while IFS= read -r -d '' file; do
        echo "  $(basename "$file")"
        markdown_count=$((markdown_count + 1))
    done < <(find "$dir" -type f -name "*.md" -print0 2>/dev/null)
    
    echo ""
    echo "PDF files (.pdf):"
    while IFS= read -r -d '' file; do
        echo "  $(basename "$file")"
        pdf_count=$((pdf_count + 1))
    done < <(find "$dir" -type f -name "*.pdf" -print0 2>/dev/null)
    
    echo ""
    echo "Text files (.txt):"
    while IFS= read -r -d '' file; do
        echo "  $(basename "$file")"
        txt_count=$((txt_count + 1))
    done < <(find "$dir" -type f -name "*.txt" -print0 2>/dev/null)
    
    echo ""
    echo -e "${GREEN}Summary:${NC}"
    echo "  Markdown: $markdown_count"
    echo "  PDF: $pdf_count"
    echo "  Text: $txt_count"
    echo "  Total: $((markdown_count + pdf_count + txt_count))"
}

# Create archive of documentation files
create_archive() {
    local dir="${1:-.}"
    local output_name="${2:-nexus_archive}"
    local separate="${3:-false}"
    
    echo -e "${BLUE}=== Creating Archive ===${NC}"
    echo "Source: $dir"
    echo "Output: $output_name"
    echo ""
    
    # Create temporary directories for organizing files
    local temp_dir=$(mktemp -d)
    local editable_dir="$temp_dir/editable"
    local non_editable_dir="$temp_dir/non_editable"
    
    mkdir -p "$editable_dir" "$non_editable_dir"
    
    # Copy editable files (markdown, txt, raw)
    find "$dir" -type f \( -name "*.md" -o -name "*.txt" \) -exec cp {} "$editable_dir/" \; 2>/dev/null || true
    
    # Copy non-editable files (PDF)
    find "$dir" -type f -name "*.pdf" -exec cp {} "$non_editable_dir/" \; 2>/dev/null || true
    
    local editable_count=$(find "$editable_dir" -type f | wc -l)
    local non_editable_count=$(find "$non_editable_dir" -type f | wc -l)
    
    if [[ "$separate" == "true" ]]; then
        # Create separate archives
        if [[ $editable_count -gt 0 ]]; then
            (cd "$editable_dir" && zip -r "${output_name}_editable.zip" .)
            mv "$editable_dir/${output_name}_editable.zip" .
            echo -e "${GREEN}Created: ${output_name}_editable.zip ($editable_count files)${NC}"
        fi
        
        if [[ $non_editable_count -gt 0 ]]; then
            (cd "$non_editable_dir" && zip -r "${output_name}_non_editable.zip" .)
            mv "$non_editable_dir/${output_name}_non_editable.zip" .
            echo -e "${GREEN}Created: ${output_name}_non_editable.zip ($non_editable_count files)${NC}"
        fi
    else
        # Create combined archive
        local combined_dir="$temp_dir/combined"
        mkdir -p "$combined_dir"
        
        if [[ $editable_count -gt 0 ]]; then
            cp "$editable_dir"/* "$combined_dir/" 2>/dev/null || true
        fi
        if [[ $non_editable_count -gt 0 ]]; then
            cp "$non_editable_dir"/* "$combined_dir/" 2>/dev/null || true
        fi
        
        local total_count=$(find "$combined_dir" -type f | wc -l)
        if [[ $total_count -gt 0 ]]; then
            (cd "$combined_dir" && zip -r "${output_name}.zip" .)
            mv "$combined_dir/${output_name}.zip" .
            echo -e "${GREEN}Created: ${output_name}.zip ($total_count files)${NC}"
        fi
    fi
    
    # Cleanup
    rm -rf "$temp_dir"
}

# Display usage information
usage() {
    cat << EOF
${BLUE}OBINexus ShellUtils - File Duplication and Archiving${NC}

Usage:
    $0 <command> [arguments]

Commands:
    duplicate <file>                    Duplicate file with platform-aware naming
    archive <directory> <output_name>   Create archive from directory
    scan <directory>                    Scan directory for documentation files
    platform                            Display detected platform
    help                                Show this help message

Examples:
    $0 duplicate document.md
    $0 archive /path/to/docs nexus_docs
    $0 scan ./documentation
    $0 platform

Platform Naming:
    Windows:     filename-copy.ext, filename-copy2.ext
    Unix/Linux:  filename2.ext, filename3.ext

EOF
}

# Main command dispatcher
main() {
    if [[ $# -eq 0 ]]; then
        usage
        exit 0
    fi
    
    local command="$1"
    shift
    
    case "$command" in
        duplicate)
            if [[ $# -lt 1 ]]; then
                echo -e "${RED}Error: Missing file argument${NC}" >&2
                usage
                exit 1
            fi
            duplicate_file "$1"
            ;;
        
        archive)
            local dir="${1:-.}"
            local output="${2:-nexus_archive}"
            local separate="${3:-false}"
            create_archive "$dir" "$output" "$separate"
            ;;
        
        scan)
            local dir="${1:-.}"
            scan_directory "$dir"
            ;;
        
        platform)
            local platform=$(detect_platform)
            echo "Detected platform: $platform"
            ;;
        
        help|--help|-h)
            usage
            ;;
        
        *)
            echo -e "${RED}Error: Unknown command: $command${NC}" >&2
            usage
            exit 1
            ;;
    esac
}

# Run main if script is executed (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

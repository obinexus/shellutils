#!/bin/sh
"""
File Copy Wrapper - Shell interface for the File Copy Functor
Uses Python functor framework for cross-platform compatibility
"""

# Check if Python 3.9+ is available
if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "Error: Python 3.9+ is required" >&2
    exit 1
fi

# Verify Python version
PYTHON_VERSION=$($PYTHON -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python 3.9+ required, found $PYTHON_VERSION" >&2
    exit 1
fi

# Execute the Python functor
exec $PYTHON -c "
import sys
sys.path.insert(0, '.')
from file_copy_functor import main
main()
" \"$@\"

# Make executable
chmod +x file_copy_functor.py
chmod +x file_copy_wrapper.sh

# Copy all PDF and MD files recursively
./file_copy_wrapper.sh /path/to/source /path/to/destination --ext .pdf .md

# Copy with multiple extensions
./file_copy_wrapper.sh ~/Documents ~/Backup --ext .pdf .md .txt .docx

# Use wildcard-style extensions
./file_copy_functor.py /source /dest --ext .pdf .md .txt

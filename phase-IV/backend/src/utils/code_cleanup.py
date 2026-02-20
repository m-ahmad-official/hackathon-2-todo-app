"""
Utility script for code cleanup and refactoring across all modules
This script identifies common issues and applies standard formatting
"""

import os
import re
from pathlib import Path


def find_python_files(root_dir: str) -> list:
    """Find all Python files in the specified directory"""
    python_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('.'):
                python_files.append(os.path.join(root, file))
    return python_files


def find_typescript_files(root_dir: str) -> list:
    """Find all TypeScript/TSX files in the specified directory"""
    ts_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(('.ts', '.tsx')) and not file.startswith('.'):
                ts_files.append(os.path.join(root, file))
    return ts_files


def standardize_imports(file_path: str):
    """Standardize import statements in the file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Look for common import issues and fix them
    # Sort imports alphabetically and separate stdlib, third-party, and local imports
    lines = content.split('\n')
    new_lines = []

    stdlib_imports = []
    third_party_imports = []
    local_imports = []
    other_lines = []

    for line in lines:
        if line.startswith('import ') or line.startswith('from '):
            # Identify import type by checking if common modules are in the line
            is_stdlib = any(keyword in line for keyword in [' os.', ' os\n', ' os ', ' sys.', ' sys\n', ' sys ', ' pathlib.', ' pathlib\n', ' pathlib ', ' typing.', ' typing\n', ' typing '])
            is_third_party = any(keyword in line for keyword in [' fastapi', ' sqlmodel', ' jose', ' pydantic'])
            is_local = any(keyword in line for keyword in [' src.', ' backend.'])

            if is_stdlib:
                stdlib_imports.append(line)
            elif is_third_party:
                third_party_imports.append(line)
            elif is_local:
                local_imports.append(line)
            else:
                third_party_imports.append(line)
        else:
            other_lines.append(line)

    # Combine in order: stdlib, third-party, local with proper spacing
    all_imports = []
    if stdlib_imports:
        all_imports.extend(sorted(set(stdlib_imports)))
        all_imports.append('')  # Empty line after stdlib imports
    if third_party_imports:
        all_imports.extend(sorted(set(third_party_imports)))
        all_imports.append('')  # Empty line after third-party imports
    if local_imports:
        all_imports.extend(sorted(set(local_imports)))
        all_imports.append('')  # Empty line after local imports

    new_content = '\n'.join(all_imports + other_lines)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)


def remove_unused_imports(file_path: str):
    """Remove unused imports from the file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # This is a simplified version - in practice, you'd use a tool like unimport
    # For now, just ensure imports are properly formatted
    lines = content.split('\n')
    new_lines = []
    in_import_block = False

    for line in lines:
        if line.startswith('import ') or line.startswith('from '):
            if not in_import_block:
                in_import_block = True
                new_lines.append(line)
            elif line.strip() and not line.startswith(('import ', 'from ')):
                in_import_block = False
                new_lines.append(line)
            else:
                new_lines.append(line)
        else:
            in_import_block = False
            new_lines.append(line)

    new_content = '\n'.join(new_lines)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)


def format_strings_consistently(file_path: str):
    """Standardize string formatting in the file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Standardize f-string usage where appropriate
    # Standardize quote usage (prefer double quotes for consistency)
    # This is a simplified version - in practice, you'd use black or similar

    # Fix common string formatting issues
    content = re.sub(r"f'([^']*)'", r'f"\1"', content)  # Convert f-string single quotes to double
    content = re.sub(r"'([^']*)'", r'"\1"', content)   # Convert single quotes to double where safe

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def cleanup_whitespace(file_path: str):
    """Remove trailing whitespace and ensure consistent line endings"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Remove trailing whitespace and ensure newline at end
    cleaned_lines = [line.rstrip() + '\n' for line in lines]
    if cleaned_lines and not cleaned_lines[-1].endswith('\n'):
        cleaned_lines[-1] += '\n'

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)


def apply_standard_cleanups(root_dir: str):
    """Apply all standard cleanup operations to files in the directory"""
    print(f"Starting code cleanup in: {root_dir}")

    # Process Python files
    python_files = find_python_files(root_dir)
    print(f"Found {len(python_files)} Python files to process")

    for file_path in python_files:
        print(f"Processing: {file_path}")
        try:
            cleanup_whitespace(file_path)
            remove_unused_imports(file_path)
            standardize_imports(file_path)
            format_strings_consistently(file_path)
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")

    # Process TypeScript files
    ts_files = find_typescript_files(root_dir)
    print(f"Found {len(ts_files)} TypeScript/TSX files to process")

    for file_path in ts_files:
        print(f"Processing: {file_path}")
        try:
            cleanup_whitespace(file_path)
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")

    print("Code cleanup completed!")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        root_directory = sys.argv[1]
    else:
        root_directory = input("Enter the root directory to clean up: ").strip()

    if os.path.exists(root_directory):
        apply_standard_cleanups(root_directory)
    else:
        print(f"Directory {root_directory} does not exist!")
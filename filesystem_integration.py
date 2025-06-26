#!/usr/bin/env python3
"""
Filesystem Integration
Advanced file operations and project management
"""

import asyncio
import os
import shutil
import json
from typing import Dict, List, Any, Optional, Union, Generator
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import fnmatch
import hashlib
import zipfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FileInfo:
    """File information structure"""
    path: str
    name: str
    size: int
    modified: datetime
    is_directory: bool
    extension: str = ""
    permissions: str = ""
    checksum: str = ""
    
@dataclass
class ProjectStructure:
    """Project structure representation"""
    root_path: str
    files: List[FileInfo]
    directories: List[str]
    total_files: int
    total_size: int
    languages: Dict[str, int]
    structure_map: Dict[str, Any]

@dataclass
class FileOperation:
    """File operation tracking"""
    operation_type: str
    source_path: str
    target_path: str = ""
    timestamp: datetime = None
    status: str = "pending"
    error_message: str = ""
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class FilesystemManager:
    """Advanced filesystem operations and project management"""
    
    def __init__(self, workspace_root: str = "./workspace"):
        self.workspace_root = Path(workspace_root)
        self.workspace_root.mkdir(exist_ok=True)
        
        self.operation_history: List[FileOperation] = []
        self.project_cache: Dict[str, ProjectStructure] = {}
        
        # File type mappings
        self.language_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.html': 'HTML',
            '.css': 'CSS',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.r': 'R',
            '.sql': 'SQL',
            '.sh': 'Shell',
            '.yml': 'YAML',
            '.yaml': 'YAML',
            '.json': 'JSON',
            '.xml': 'XML',
            '.md': 'Markdown',
            '.dockerfile': 'Docker',
            '.tf': 'Terraform'
        }
    
    async def scan_project(self, project_path: str, include_hidden: bool = False) -> ProjectStructure:
        """Scan project directory and analyze structure"""
        
        project_path = Path(project_path)
        if not project_path.exists():
            raise FileNotFoundError(f"Project path does not exist: {project_path}")
        
        logger.info(f"📂 Scanning project: {project_path}")
        
        files = []
        directories = []
        languages = {}
        total_size = 0
        
        # Walk through directory structure
        for root, dirs, filenames in os.walk(project_path):
            root_path = Path(root)
            
            # Filter hidden directories if not included
            if not include_hidden:
                dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            # Add directories
            for dir_name in dirs:
                dir_path = root_path / dir_name
                directories.append(str(dir_path.relative_to(project_path)))
            
            # Process files
            for filename in filenames:
                file_path = root_path / filename
                
                # Skip hidden files if not included
                if not include_hidden and filename.startswith('.'):
                    continue
                
                try:
                    stat = file_path.stat()
                    extension = file_path.suffix.lower()
                    
                    file_info = FileInfo(
                        path=str(file_path.relative_to(project_path)),
                        name=filename,
                        size=stat.st_size,
                        modified=datetime.fromtimestamp(stat.st_mtime),
                        is_directory=False,
                        extension=extension,
                        permissions=oct(stat.st_mode)[-3:],
                        checksum=await self._calculate_file_checksum(file_path)
                    )
                    
                    files.append(file_info)
                    total_size += stat.st_size
                    
                    # Count languages
                    language = self.language_extensions.get(extension, 'Other')
                    languages[language] = languages.get(language, 0) + 1
                    
                except (OSError, PermissionError) as e:
                    logger.warning(f"Skipping file {file_path}: {e}")
        
        # Build structure map
        structure_map = await self._build_structure_map(project_path, files, directories)
        
        project_structure = ProjectStructure(
            root_path=str(project_path),
            files=files,
            directories=directories,
            total_files=len(files),
            total_size=total_size,
            languages=languages,
            structure_map=structure_map
        )
        
        # Cache the structure
        self.project_cache[str(project_path)] = project_structure
        
        logger.info(f"✅ Scanned {len(files)} files in {len(directories)} directories")
        
        return project_structure
    
    async def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of file"""
        
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
    
    async def _build_structure_map(self, 
                                 root_path: Path,
                                 files: List[FileInfo],
                                 directories: List[str]) -> Dict[str, Any]:
        """Build hierarchical structure map"""
        
        structure = {}
        
        # Add directories
        for dir_path in directories:
            parts = Path(dir_path).parts
            current = structure
            
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]
        
        # Add files to structure
        for file_info in files:
            parts = Path(file_info.path).parts
            current = structure
            
            # Navigate to parent directory
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Add file
            filename = parts[-1]
            current[filename] = {
                "type": "file",
                "size": file_info.size,
                "extension": file_info.extension,
                "modified": file_info.modified.isoformat()
            }
        
        return structure
    
    async def create_project_structure(self, 
                                     project_name: str,
                                     template: str = "default",
                                     custom_structure: Dict[str, Any] = None) -> str:
        """Create new project with specified structure"""
        
        project_path = self.workspace_root / project_name
        
        if project_path.exists():
            raise FileExistsError(f"Project already exists: {project_path}")
        
        logger.info(f"🏗️ Creating project: {project_name}")
        
        # Create project root
        project_path.mkdir(parents=True)
        
        operation = FileOperation(
            operation_type="create_project",
            source_path=str(project_path)
        )
        
        try:
            if custom_structure:
                await self._create_custom_structure(project_path, custom_structure)
            else:
                await self._create_template_structure(project_path, template)
            
            operation.status = "completed"
            
        except Exception as e:
            operation.status = "failed"
            operation.error_message = str(e)
            raise
        
        finally:
            self.operation_history.append(operation)
        
        logger.info(f"✅ Project created: {project_path}")
        return str(project_path)
    
    async def _create_template_structure(self, project_path: Path, template: str):
        """Create project structure from template"""
        
        templates = {
            "default": {
                "src": {},
                "tests": {},
                "docs": {},
                "README.md": "# Project\n\nDescription of the project.",
                "requirements.txt": "# Add your dependencies here\n",
                ".gitignore": "*.pyc\n__pycache__/\n.env\n"
            },
            "python_package": {
                "src": {
                    "__init__.py": "",
                    "main.py": "#!/usr/bin/env python3\n\ndef main():\n    print('Hello, World!')\n\nif __name__ == '__main__':\n    main()\n"
                },
                "tests": {
                    "__init__.py": "",
                    "test_main.py": "import unittest\n\nclass TestMain(unittest.TestCase):\n    def test_example(self):\n        self.assertTrue(True)\n"
                },
                "setup.py": "from setuptools import setup, find_packages\n\nsetup(\n    name='project',\n    version='0.1.0',\n    packages=find_packages()\n)\n",
                "requirements.txt": "pytest>=6.0.0\n",
                "README.md": "# Python Package\n\nA Python package template.",
                ".gitignore": "*.pyc\n__pycache__/\n*.egg-info/\ndist/\nbuild/\n.pytest_cache/\n"
            },
            "web_app": {
                "frontend": {
                    "src": {
                        "index.html": "<!DOCTYPE html>\n<html>\n<head>\n    <title>Web App</title>\n</head>\n<body>\n    <h1>Hello, World!</h1>\n</body>\n</html>",
                        "style.css": "body { font-family: Arial, sans-serif; }",
                        "script.js": "console.log('Hello, World!');"
                    }
                },
                "backend": {
                    "app.py": "from flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef hello():\n    return 'Hello, World!'\n\nif __name__ == '__main__':\n    app.run(debug=True)\n"
                },
                "requirements.txt": "flask>=2.0.0\n",
                "README.md": "# Web Application\n\nA web application template."
            }
        }
        
        structure = templates.get(template, templates["default"])
        await self._create_custom_structure(project_path, structure)
    
    async def _create_custom_structure(self, base_path: Path, structure: Dict[str, Any]):
        """Create custom directory/file structure"""
        
        for name, content in structure.items():
            path = base_path / name
            
            if isinstance(content, dict):
                # Create directory
                path.mkdir(exist_ok=True)
                await self._create_custom_structure(path, content)
            else:
                # Create file
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
    
    async def copy_files(self, 
                        source_patterns: List[str],
                        destination: str,
                        preserve_structure: bool = True) -> List[str]:
        """Copy files matching patterns to destination"""
        
        destination_path = Path(destination)
        destination_path.mkdir(parents=True, exist_ok=True)
        
        copied_files = []
        
        for pattern in source_patterns:
            logger.info(f"📋 Copying files matching: {pattern}")
            
            # Find files matching pattern
            matching_files = await self._find_files_by_pattern(pattern)
            
            for source_file in matching_files:
                source_path = Path(source_file)
                
                if preserve_structure:
                    # Preserve directory structure
                    rel_path = source_path.relative_to(source_path.anchor)
                    target_path = destination_path / rel_path
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    # Flatten structure
                    target_path = destination_path / source_path.name
                
                operation = FileOperation(
                    operation_type="copy",
                    source_path=str(source_path),
                    target_path=str(target_path)
                )
                
                try:
                    shutil.copy2(source_path, target_path)
                    copied_files.append(str(target_path))
                    operation.status = "completed"
                    
                except Exception as e:
                    operation.status = "failed"
                    operation.error_message = str(e)
                    logger.error(f"Failed to copy {source_path}: {e}")
                
                finally:
                    self.operation_history.append(operation)
        
        logger.info(f"✅ Copied {len(copied_files)} files")
        return copied_files
    
    async def _find_files_by_pattern(self, pattern: str) -> List[str]:
        """Find files matching glob pattern"""
        
        files = []
        
        # Handle absolute and relative patterns
        if os.path.isabs(pattern):
            search_root = Path(pattern).anchor
            pattern = str(Path(pattern).relative_to(search_root))
        else:
            search_root = Path.cwd()
        
        for root, dirs, filenames in os.walk(search_root):
            for filename in filenames:
                file_path = Path(root) / filename
                relative_path = file_path.relative_to(search_root)
                
                if fnmatch.fnmatch(str(relative_path), pattern):
                    files.append(str(file_path))
        
        return files
    
    async def search_in_files(self, 
                            search_path: str,
                            query: str,
                            file_patterns: List[str] = None,
                            case_sensitive: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """Search for text in files"""
        
        search_path = Path(search_path)
        results = {}
        
        file_patterns = file_patterns or ['*']
        
        logger.info(f"🔍 Searching for '{query}' in {search_path}")
        
        for root, dirs, filenames in os.walk(search_path):
            for filename in filenames:
                file_path = Path(root) / filename
                
                # Check if file matches any pattern
                if not any(fnmatch.fnmatch(filename, pattern) for pattern in file_patterns):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    
                    matches = []
                    for line_num, line in enumerate(lines, 1):
                        search_line = line if case_sensitive else line.lower()
                        search_query = query if case_sensitive else query.lower()
                        
                        if search_query in search_line:
                            matches.append({
                                "line_number": line_num,
                                "line_content": line.strip(),
                                "column": search_line.index(search_query)
                            })
                    
                    if matches:
                        results[str(file_path)] = matches
                
                except Exception as e:
                    logger.debug(f"Skipping file {file_path}: {e}")
        
        logger.info(f"✅ Found {sum(len(matches) for matches in results.values())} matches in {len(results)} files")
        return results
    
    async def replace_in_files(self, 
                             search_path: str,
                             search_text: str,
                             replace_text: str,
                             file_patterns: List[str] = None,
                             dry_run: bool = True) -> Dict[str, int]:
        """Replace text in files"""
        
        search_path = Path(search_path)
        replacements = {}
        
        file_patterns = file_patterns or ['*']
        
        logger.info(f"🔄 {'[DRY RUN] ' if dry_run else ''}Replacing '{search_text}' with '{replace_text}' in {search_path}")
        
        for root, dirs, filenames in os.walk(search_path):
            for filename in filenames:
                file_path = Path(root) / filename
                
                # Check if file matches any pattern
                if not any(fnmatch.fnmatch(filename, pattern) for pattern in file_patterns):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if search_text in content:
                        new_content = content.replace(search_text, replace_text)
                        replacement_count = content.count(search_text)
                        
                        if not dry_run:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            
                            operation = FileOperation(
                                operation_type="replace",
                                source_path=str(file_path),
                                status="completed"
                            )
                            self.operation_history.append(operation)
                        
                        replacements[str(file_path)] = replacement_count
                
                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {e}")
        
        logger.info(f"✅ {'Would replace' if dry_run else 'Replaced'} text in {len(replacements)} files")
        return replacements
    
    async def create_archive(self, 
                           source_path: str,
                           archive_path: str,
                           compression: str = "zip",
                           exclude_patterns: List[str] = None) -> str:
        """Create archive of project or directory"""
        
        source_path = Path(source_path)
        archive_path = Path(archive_path)
        
        exclude_patterns = exclude_patterns or [
            "*.pyc", "__pycache__", ".git", ".env", "node_modules"
        ]
        
        logger.info(f"📦 Creating archive: {archive_path}")
        
        if compression == "zip":
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_path):
                    # Filter excluded directories
                    dirs[:] = [d for d in dirs if not any(
                        fnmatch.fnmatch(d, pattern) for pattern in exclude_patterns
                    )]
                    
                    for file in files:
                        file_path = Path(root) / file
                        
                        # Skip excluded files
                        if any(fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns):
                            continue
                        
                        arcname = file_path.relative_to(source_path)
                        zipf.write(file_path, arcname)
        
        operation = FileOperation(
            operation_type="archive",
            source_path=str(source_path),
            target_path=str(archive_path),
            status="completed"
        )
        self.operation_history.append(operation)
        
        logger.info(f"✅ Archive created: {archive_path}")
        return str(archive_path)
    
    def get_project_stats(self, project_path: str) -> Dict[str, Any]:
        """Get project statistics"""
        
        if project_path in self.project_cache:
            structure = self.project_cache[project_path]
        else:
            return {"error": "Project not scanned"}
        
        # Calculate detailed statistics
        stats = {
            "total_files": structure.total_files,
            "total_directories": len(structure.directories),
            "total_size": structure.total_size,
            "total_size_human": self._human_readable_size(structure.total_size),
            "languages": structure.languages,
            "largest_files": sorted(
                structure.files,
                key=lambda f: f.size,
                reverse=True
            )[:10],
            "recent_files": sorted(
                structure.files,
                key=lambda f: f.modified,
                reverse=True
            )[:10],
            "file_extensions": {},
            "average_file_size": structure.total_size // max(1, structure.total_files)
        }
        
        # Count file extensions
        for file_info in structure.files:
            ext = file_info.extension or "no_extension"
            stats["file_extensions"][ext] = stats["file_extensions"].get(ext, 0) + 1
        
        return stats
    
    def _human_readable_size(self, size: int) -> str:
        """Convert bytes to human readable format"""
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def get_operation_history(self, limit: int = 50) -> List[FileOperation]:
        """Get recent file operations"""
        
        return self.operation_history[-limit:]
    
    def clear_cache(self):
        """Clear project cache"""
        
        self.project_cache.clear()
        logger.info("🧹 Project cache cleared")
    
    async def watch_directory(self, 
                            directory: str,
                            callback: callable,
                            patterns: List[str] = None) -> None:
        """Watch directory for changes (simplified implementation)"""
        
        directory = Path(directory)
        patterns = patterns or ['*']
        
        logger.info(f"👁️ Watching directory: {directory}")
        
        # Simple polling-based watcher
        last_scan = {}
        
        while True:
            try:
                current_scan = {}
                
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        file_path = Path(root) / file
                        
                        if any(fnmatch.fnmatch(file, pattern) for pattern in patterns):
                            try:
                                stat = file_path.stat()
                                current_scan[str(file_path)] = stat.st_mtime
                            except OSError:
                                continue
                
                # Check for changes
                for file_path, mtime in current_scan.items():
                    if file_path not in last_scan or last_scan[file_path] != mtime:
                        await callback("modified", file_path)
                
                # Check for deletions
                for file_path in last_scan:
                    if file_path not in current_scan:
                        await callback("deleted", file_path)
                
                last_scan = current_scan
                await asyncio.sleep(1)  # Poll every second
                
            except Exception as e:
                logger.error(f"Watch error: {e}")
                await asyncio.sleep(5)

async def main():
    """Demo filesystem integration"""
    
    print("📂 Filesystem Integration Demo")
    print("=" * 50)
    
    # Initialize filesystem manager
    fs_manager = FilesystemManager("./demo_workspace")
    
    # Create a test project
    print("\n1. Creating test project...")
    project_path = await fs_manager.create_project_structure(
        "demo_project",
        template="python_package"
    )
    print(f"Created project: {project_path}")
    
    # Scan the project
    print("\n2. Scanning project structure...")
    structure = await fs_manager.scan_project(project_path)
    print(f"Found {structure.total_files} files in {len(structure.directories)} directories")
    print(f"Languages: {structure.languages}")
    
    # Get project statistics
    print("\n3. Project statistics:")
    stats = fs_manager.get_project_stats(project_path)
    print(f"Total size: {stats['total_size_human']}")
    print(f"Average file size: {fs_manager._human_readable_size(stats['average_file_size'])}")
    
    # Search in files
    print("\n4. Searching in files...")
    search_results = await fs_manager.search_in_files(
        project_path,
        "def",
        file_patterns=["*.py"]
    )
    print(f"Found 'def' in {len(search_results)} files")
    
    # Create archive
    print("\n5. Creating project archive...")
    archive_path = await fs_manager.create_archive(
        project_path,
        f"{project_path}.zip"
    )
    print(f"Archive created: {archive_path}")
    
    # Show operation history
    print("\n6. Operation history:")
    history = fs_manager.get_operation_history(limit=5)
    for op in history:
        print(f"  {op.operation_type}: {op.source_path} [{op.status}]")

if __name__ == "__main__":
    asyncio.run(main())
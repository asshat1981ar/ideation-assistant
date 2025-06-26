#!/usr/bin/env python3
"""
Code Execution and Interaction Engine
Safe code execution, testing, and build automation
"""

import asyncio
import subprocess
import os
import tempfile
import json
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import logging
import sys
import time
import signal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ExecutionResult:
    """Code execution result"""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    command: str
    working_directory: str
    timestamp: datetime
    environment: Dict[str, str] = None
    
    def __post_init__(self):
        if self.environment is None:
            self.environment = {}

@dataclass
class TestResult:
    """Test execution result"""
    test_name: str
    passed: bool
    failed: bool
    skipped: bool
    errors: List[str]
    execution_time: float
    output: str

@dataclass
class BuildResult:
    """Build execution result"""
    success: bool
    build_type: str
    artifacts: List[str]
    execution_time: float
    output: str
    errors: List[str]

class SafeCodeExecutor:
    """Safe code execution with sandboxing and limits"""
    
    def __init__(self, workspace_dir: str = "./code_workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        self.execution_history: List[ExecutionResult] = []
        self.active_processes: Dict[str, subprocess.Popen] = {}
        
        # Default limits
        self.default_timeout = 30  # seconds
        self.max_output_size = 1024 * 1024  # 1MB
        self.allowed_commands = {
            'python', 'python3', 'node', 'npm', 'pip', 'pip3',
            'gcc', 'g++', 'javac', 'java', 'go', 'cargo',
            'make', 'cmake', 'docker', 'git'
        }
    
    async def execute_code(self, 
                          code: str,
                          language: str,
                          timeout: int = None,
                          working_dir: str = None,
                          environment: Dict[str, str] = None) -> ExecutionResult:
        """Execute code safely with specified language"""
        
        timeout = timeout or self.default_timeout
        # Use the temp directory as working directory for execution
        execution_working_dir = Path(working_dir) if working_dir else self.workspace_dir
        environment = environment or {}
        
        logger.info(f"🚀 Executing {language} code")
        
        # Create temporary file for code
        temp_file = await self._create_temp_file(code, language)
        
        try:
            # Get execution command - use filename only since we're executing from temp dir
            command = self._get_execution_command(temp_file, language, use_filename_only=True)
            
            # Execute with safety measures - use temp file's parent as working dir
            result = await self._safe_execute(
                command=command,
                working_dir=temp_file.parent,
                timeout=timeout,
                environment=environment
            )
            
            # Store in history
            self.execution_history.append(result)
            
            return result
            
        finally:
            # Cleanup temporary file
            if temp_file.exists():
                temp_file.unlink()
    
    async def _create_temp_file(self, code: str, language: str) -> Path:
        """Create temporary file for code execution"""
        
        extensions = {
            'python': '.py',
            'javascript': '.js',
            'typescript': '.ts',
            'java': '.java',
            'cpp': '.cpp',
            'c': '.c',
            'go': '.go',
            'rust': '.rs',
            'shell': '.sh'
        }
        
        extension = extensions.get(language.lower(), '.txt')
        
        # Create temporary file with proper path handling
        temp_dir = self.workspace_dir / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Use timestamp and random component for unique filename
        import random
        unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
        temp_file = temp_dir / f"code_{unique_id}{extension}"
        
        # Ensure the file doesn't already exist
        counter = 0
        while temp_file.exists() and counter < 100:
            counter += 1
            temp_file = temp_dir / f"code_{unique_id}_{counter}{extension}"
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Make executable if shell script
        if language.lower() == 'shell':
            temp_file.chmod(0o755)
        
        logger.debug(f"Created temp file: {temp_file}")
        return temp_file
    
    def _get_execution_command(self, file_path: Path, language: str, use_filename_only: bool = False) -> List[str]:
        """Get command to execute code file"""
        
        # Use just filename if we're executing from the file's directory
        file_ref = file_path.name if use_filename_only else str(file_path)
        
        commands = {
            'python': ['python3', file_ref],
            'javascript': ['node', file_ref],
            'typescript': ['npx', 'ts-node', file_ref],
            'java': self._get_java_command(file_path),
            'cpp': self._get_cpp_command(file_path),
            'c': self._get_c_command(file_path),
            'go': ['go', 'run', file_ref],
            'rust': self._get_rust_command(file_path),
            'shell': ['bash', file_ref]
        }
        
        command = commands.get(language.lower())
        if not command:
            raise ValueError(f"Unsupported language: {language}")
        
        # Verify command is allowed
        if command[0] not in self.allowed_commands:
            raise ValueError(f"Command not allowed: {command[0]}")
        
        return command
    
    def _get_java_command(self, file_path: Path) -> List[str]:
        """Get Java compilation and execution command"""
        class_name = file_path.stem
        return ['java', '-cp', str(file_path.parent), class_name]
    
    def _get_cpp_command(self, file_path: Path) -> List[str]:
        """Get C++ compilation and execution command"""
        executable = file_path.with_suffix('')
        return ['g++', '-o', str(executable), str(file_path), '&&', str(executable)]
    
    def _get_c_command(self, file_path: Path) -> List[str]:
        """Get C compilation and execution command"""
        executable = file_path.with_suffix('')
        return ['gcc', '-o', str(executable), str(file_path), '&&', str(executable)]
    
    def _get_rust_command(self, file_path: Path) -> List[str]:
        """Get Rust execution command"""
        return ['rustc', str(file_path), '-o', str(file_path.with_suffix('')), '&&', str(file_path.with_suffix(''))]
    
    async def _safe_execute(self, 
                           command: List[str],
                           working_dir: Path,
                           timeout: int,
                           environment: Dict[str, str]) -> ExecutionResult:
        """Execute command with safety measures"""
        
        start_time = time.time()
        
        # Prepare environment
        env = os.environ.copy()
        env.update(environment)
        
        # Add safety restrictions to environment
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        env['PYTHONUNBUFFERED'] = '1'
        
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                preexec_fn=self._setup_process_limits if os.name != 'nt' else None
            )
            
            process_id = f"exec_{int(time.time())}"
            self.active_processes[process_id] = process
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                stdout = stdout.decode('utf-8', errors='replace')
                stderr = stderr.decode('utf-8', errors='replace')
                
                # Limit output size
                if len(stdout) > self.max_output_size:
                    stdout = stdout[:self.max_output_size] + "\n... [Output truncated]"
                
                if len(stderr) > self.max_output_size:
                    stderr = stderr[:self.max_output_size] + "\n... [Error output truncated]"
                
                execution_time = time.time() - start_time
                
                result = ExecutionResult(
                    success=process.returncode == 0,
                    stdout=stdout,
                    stderr=stderr,
                    exit_code=process.returncode,
                    execution_time=execution_time,
                    command=' '.join(command),
                    working_directory=str(working_dir),
                    timestamp=datetime.now(),
                    environment=environment
                )
                
                logger.info(f"✅ Execution completed in {execution_time:.2f}s")
                return result
                
            except asyncio.TimeoutError:
                # Kill process on timeout
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=5)
                except asyncio.TimeoutError:
                    process.kill()
                
                execution_time = time.time() - start_time
                
                result = ExecutionResult(
                    success=False,
                    stdout="",
                    stderr=f"Execution timed out after {timeout} seconds",
                    exit_code=-1,
                    execution_time=execution_time,
                    command=' '.join(command),
                    working_directory=str(working_dir),
                    timestamp=datetime.now(),
                    environment=environment
                )
                
                logger.warning(f"⏰ Execution timed out after {timeout}s")
                return result
                
            finally:
                if process_id in self.active_processes:
                    del self.active_processes[process_id]
        
        except Exception as e:
            execution_time = time.time() - start_time
            
            result = ExecutionResult(
                success=False,
                stdout="",
                stderr=f"Execution error: {str(e)}",
                exit_code=-2,
                execution_time=execution_time,
                command=' '.join(command),
                working_directory=str(working_dir),
                timestamp=datetime.now(),
                environment=environment
            )
            
            logger.error(f"❌ Execution failed: {e}")
            return result
    
    def _setup_process_limits(self):
        """Setup process limits for safety (Unix only)"""
        try:
            import resource
            
            # Limit CPU time (30 seconds)
            resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
            
            # Limit memory (512MB)
            resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
            
            # Limit number of processes
            resource.setrlimit(resource.RLIMIT_NPROC, (50, 50))
            
        except ImportError:
            # resource module not available on Windows
            pass
    
    async def execute_script(self, 
                           script_path: str,
                           args: List[str] = None,
                           timeout: int = None) -> ExecutionResult:
        """Execute a script file with arguments"""
        
        script_path = Path(script_path)
        args = args or []
        timeout = timeout or self.default_timeout
        
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        # Determine script type from extension
        extension = script_path.suffix.lower()
        
        if extension == '.py':
            command = ['python3', str(script_path)] + args
        elif extension in ['.js', '.mjs']:
            command = ['node', str(script_path)] + args
        elif extension == '.sh':
            command = ['bash', str(script_path)] + args
        else:
            # Try to execute directly
            script_path.chmod(0o755)
            command = [str(script_path)] + args
        
        return await self._safe_execute(
            command=command,
            working_dir=script_path.parent,
            timeout=timeout,
            environment={}
        )
    
    async def kill_process(self, process_id: str) -> bool:
        """Kill a running process"""
        
        if process_id in self.active_processes:
            process = self.active_processes[process_id]
            process.terminate()
            
            try:
                await asyncio.wait_for(process.wait(), timeout=5)
            except asyncio.TimeoutError:
                process.kill()
            
            del self.active_processes[process_id]
            logger.info(f"🛑 Process {process_id} terminated")
            return True
        
        return False
    
    def get_active_processes(self) -> List[str]:
        """Get list of active process IDs"""
        return list(self.active_processes.keys())
    
    def get_execution_history(self, limit: int = 20) -> List[ExecutionResult]:
        """Get recent execution history"""
        return self.execution_history[-limit:]

class TestRunner:
    """Automated test execution and reporting"""
    
    def __init__(self, executor: SafeCodeExecutor):
        self.executor = executor
        self.test_history: List[TestResult] = []
    
    async def run_python_tests(self, 
                             test_directory: str,
                             test_pattern: str = "test_*.py",
                             framework: str = "pytest") -> List[TestResult]:
        """Run Python tests"""
        
        test_dir = Path(test_directory)
        
        logger.info(f"🧪 Running Python tests in {test_dir}")
        
        if framework == "pytest":
            command = ['python3', '-m', 'pytest', str(test_dir), '-v', '--tb=short']
        elif framework == "unittest":
            command = ['python3', '-m', 'unittest', 'discover', str(test_dir), '-p', test_pattern, '-v']
        else:
            raise ValueError(f"Unsupported test framework: {framework}")
        
        result = await self.executor._safe_execute(
            command=command,
            working_dir=test_dir.parent,
            timeout=60,
            environment={}
        )
        
        # Parse test results
        test_results = self._parse_test_output(result.stdout, framework)
        
        self.test_history.extend(test_results)
        
        return test_results
    
    async def run_javascript_tests(self, 
                                 test_directory: str,
                                 framework: str = "jest") -> List[TestResult]:
        """Run JavaScript tests"""
        
        test_dir = Path(test_directory)
        
        logger.info(f"🧪 Running JavaScript tests in {test_dir}")
        
        if framework == "jest":
            command = ['npm', 'test']
        elif framework == "mocha":
            command = ['npx', 'mocha', str(test_dir / "*.test.js")]
        else:
            raise ValueError(f"Unsupported test framework: {framework}")
        
        result = await self.executor._safe_execute(
            command=command,
            working_dir=test_dir,
            timeout=60,
            environment={}
        )
        
        # Parse test results
        test_results = self._parse_js_test_output(result.stdout, framework)
        
        self.test_history.extend(test_results)
        
        return test_results
    
    def _parse_test_output(self, output: str, framework: str) -> List[TestResult]:
        """Parse test framework output"""
        
        test_results = []
        
        if framework == "pytest":
            # Simple pytest output parsing
            lines = output.split('\n')
            for line in lines:
                if '::' in line and ('PASSED' in line or 'FAILED' in line or 'SKIPPED' in line):
                    parts = line.split('::')
                    test_name = parts[-1].split()[0]
                    
                    test_result = TestResult(
                        test_name=test_name,
                        passed='PASSED' in line,
                        failed='FAILED' in line,
                        skipped='SKIPPED' in line,
                        errors=[],
                        execution_time=0.0,
                        output=line
                    )
                    test_results.append(test_result)
        
        return test_results
    
    def _parse_js_test_output(self, output: str, framework: str) -> List[TestResult]:
        """Parse JavaScript test framework output"""
        
        # Simplified parsing - would need more sophisticated parsing for real use
        return []

class BuildSystem:
    """Build automation and artifact management"""
    
    def __init__(self, executor: SafeCodeExecutor):
        self.executor = executor
        self.build_history: List[BuildResult] = []
    
    async def build_python_package(self, project_dir: str) -> BuildResult:
        """Build Python package"""
        
        project_path = Path(project_dir)
        
        logger.info(f"🔨 Building Python package in {project_path}")
        
        start_time = time.time()
        artifacts = []
        errors = []
        
        try:
            # Check for setup.py or pyproject.toml
            if (project_path / "setup.py").exists():
                command = ['python3', 'setup.py', 'build']
            elif (project_path / "pyproject.toml").exists():
                command = ['python3', '-m', 'build']
            else:
                # Create a simple wheel
                command = ['python3', '-m', 'pip', 'wheel', '.', '--no-deps']
            
            result = await self.executor._safe_execute(
                command=command,
                working_dir=project_path,
                timeout=300,  # 5 minutes
                environment={}
            )
            
            if result.success:
                # Find build artifacts
                build_dir = project_path / "build"
                dist_dir = project_path / "dist"
                
                for directory in [build_dir, dist_dir]:
                    if directory.exists():
                        for artifact in directory.rglob("*"):
                            if artifact.is_file():
                                artifacts.append(str(artifact))
            else:
                errors.append(result.stderr)
            
            build_result = BuildResult(
                success=result.success,
                build_type="python_package",
                artifacts=artifacts,
                execution_time=time.time() - start_time,
                output=result.stdout,
                errors=errors
            )
            
        except Exception as e:
            build_result = BuildResult(
                success=False,
                build_type="python_package",
                artifacts=[],
                execution_time=time.time() - start_time,
                output="",
                errors=[str(e)]
            )
        
        self.build_history.append(build_result)
        
        if build_result.success:
            logger.info(f"✅ Build completed: {len(artifacts)} artifacts")
        else:
            logger.error("❌ Build failed")
        
        return build_result
    
    async def build_javascript_project(self, project_dir: str) -> BuildResult:
        """Build JavaScript/Node.js project"""
        
        project_path = Path(project_dir)
        
        logger.info(f"🔨 Building JavaScript project in {project_path}")
        
        start_time = time.time()
        artifacts = []
        errors = []
        
        try:
            # Install dependencies first
            install_result = await self.executor._safe_execute(
                command=['npm', 'install'],
                working_dir=project_path,
                timeout=300,
                environment={}
            )
            
            if not install_result.success:
                errors.append(f"npm install failed: {install_result.stderr}")
            
            # Run build
            build_result = await self.executor._safe_execute(
                command=['npm', 'run', 'build'],
                working_dir=project_path,
                timeout=300,
                environment={}
            )
            
            if build_result.success:
                # Find build artifacts
                build_dirs = [project_path / "build", project_path / "dist", project_path / "public"]
                
                for directory in build_dirs:
                    if directory.exists():
                        for artifact in directory.rglob("*"):
                            if artifact.is_file():
                                artifacts.append(str(artifact))
            else:
                errors.append(build_result.stderr)
            
            final_result = BuildResult(
                success=build_result.success and install_result.success,
                build_type="javascript_project",
                artifacts=artifacts,
                execution_time=time.time() - start_time,
                output=f"{install_result.stdout}\n{build_result.stdout}",
                errors=errors
            )
            
        except Exception as e:
            final_result = BuildResult(
                success=False,
                build_type="javascript_project",
                artifacts=[],
                execution_time=time.time() - start_time,
                output="",
                errors=[str(e)]
            )
        
        self.build_history.append(final_result)
        
        if final_result.success:
            logger.info(f"✅ Build completed: {len(artifacts)} artifacts")
        else:
            logger.error("❌ Build failed")
        
        return final_result
    
    async def run_quality_checks(self, project_dir: str, language: str) -> Dict[str, Any]:
        """Run code quality checks"""
        
        project_path = Path(project_dir)
        
        logger.info(f"🔍 Running quality checks for {language} project")
        
        checks = {}
        
        if language.lower() == "python":
            # Run flake8 for linting
            lint_result = await self.executor._safe_execute(
                command=['python3', '-m', 'flake8', str(project_path)],
                working_dir=project_path,
                timeout=60,
                environment={}
            )
            checks["linting"] = {
                "success": lint_result.success,
                "output": lint_result.stdout,
                "errors": lint_result.stderr
            }
            
            # Run black for formatting check
            format_result = await self.executor._safe_execute(
                command=['python3', '-m', 'black', '--check', str(project_path)],
                working_dir=project_path,
                timeout=60,
                environment={}
            )
            checks["formatting"] = {
                "success": format_result.success,
                "output": format_result.stdout,
                "errors": format_result.stderr
            }
        
        elif language.lower() == "javascript":
            # Run ESLint
            lint_result = await self.executor._safe_execute(
                command=['npx', 'eslint', '.'],
                working_dir=project_path,
                timeout=60,
                environment={}
            )
            checks["linting"] = {
                "success": lint_result.success,
                "output": lint_result.stdout,
                "errors": lint_result.stderr
            }
        
        return checks

class CodeInteractionEngine:
    """Complete code interaction and execution engine"""
    
    def __init__(self, workspace_dir: str = "./code_workspace"):
        self.executor = SafeCodeExecutor(workspace_dir)
        self.test_runner = TestRunner(self.executor)
        self.build_system = BuildSystem(self.executor)
        
        self.interactive_sessions: Dict[str, Any] = {}
    
    async def create_and_run_project(self, 
                                   project_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create and run a complete project"""
        
        project_name = project_config["name"]
        language = project_config["language"]
        
        logger.info(f"🚀 Creating and running project: {project_name}")
        
        # Create project directory
        project_path = self.executor.workspace_dir / project_name
        project_path.mkdir(exist_ok=True)
        
        # Create project files
        files = project_config.get("files", {})
        for file_path, content in files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(content)
        
        # Run the project
        execution_result = None
        if "main_file" in project_config:
            main_file = project_path / project_config["main_file"]
            execution_result = await self.executor.execute_script(str(main_file))
        
        # Run tests if available
        test_results = []
        if "test_directory" in project_config:
            test_dir = project_path / project_config["test_directory"]
            if test_dir.exists():
                if language.lower() == "python":
                    test_results = await self.test_runner.run_python_tests(str(test_dir))
                elif language.lower() == "javascript":
                    test_results = await self.test_runner.run_javascript_tests(str(test_dir))
        
        # Build if configuration provided
        build_result = None
        if project_config.get("build", False):
            if language.lower() == "python":
                build_result = await self.build_system.build_python_package(str(project_path))
            elif language.lower() == "javascript":
                build_result = await self.build_system.build_javascript_project(str(project_path))
        
        return {
            "project_path": str(project_path),
            "execution_result": execution_result,
            "test_results": test_results,
            "build_result": build_result,
            "created_files": list(files.keys())
        }
    
    async def start_interactive_session(self, language: str) -> str:
        """Start interactive coding session"""
        
        session_id = f"session_{int(time.time())}"
        
        logger.info(f"🎯 Starting interactive {language} session: {session_id}")
        
        session = {
            "session_id": session_id,
            "language": language,
            "created_at": datetime.now(),
            "execution_history": [],
            "variables": {},
            "working_directory": str(self.executor.workspace_dir / session_id)
        }
        
        # Create session directory
        session_dir = Path(session["working_directory"])
        session_dir.mkdir(exist_ok=True)
        
        self.interactive_sessions[session_id] = session
        
        return session_id
    
    async def execute_in_session(self, 
                               session_id: str,
                               code: str) -> ExecutionResult:
        """Execute code in an interactive session"""
        
        if session_id not in self.interactive_sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        session = self.interactive_sessions[session_id]
        
        # Execute code
        result = await self.executor.execute_code(
            code=code,
            language=session["language"],
            working_dir=session["working_directory"]
        )
        
        # Add to session history
        session["execution_history"].append(result)
        
        return result
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get interactive session information"""
        
        if session_id not in self.interactive_sessions:
            return {"error": "Session not found"}
        
        session = self.interactive_sessions[session_id]
        
        return {
            "session_id": session_id,
            "language": session["language"],
            "created_at": session["created_at"].isoformat(),
            "executions_count": len(session["execution_history"]),
            "last_execution": session["execution_history"][-1] if session["execution_history"] else None
        }

async def main():
    """Demo code execution capabilities"""
    
    print("⚡ Code Execution Engine Demo")
    print("=" * 50)
    
    # Initialize code interaction engine
    engine = CodeInteractionEngine()
    
    # Demo 1: Execute simple Python code
    print("\n1. Executing Python code...")
    python_code = """
print("Hello from Python!")
import math
result = math.sqrt(16)
print(f"Square root of 16 is: {result}")
"""
    
    result = await engine.executor.execute_code(python_code, "python")
    print(f"Success: {result.success}")
    print(f"Output: {result.stdout}")
    if result.stderr:
        print(f"Errors: {result.stderr}")
    
    # Demo 2: Create and run a project
    print("\n2. Creating and running a project...")
    project_config = {
        "name": "demo_project",
        "language": "python",
        "files": {
            "main.py": """
def greet(name):
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("World"))
    print("Project is running successfully!")
""",
            "test_main.py": """
import unittest
from main import greet

class TestGreet(unittest.TestCase):
    def test_greet(self):
        self.assertEqual(greet("Alice"), "Hello, Alice!")

if __name__ == "__main__":
    unittest.main()
"""
        },
        "main_file": "main.py",
        "test_directory": ".",
        "build": False
    }
    
    project_result = await engine.create_and_run_project(project_config)
    print(f"Project created at: {project_result['project_path']}")
    if project_result["execution_result"]:
        print(f"Execution output: {project_result['execution_result'].stdout}")
    
    # Demo 3: Interactive session
    print("\n3. Interactive session...")
    session_id = await engine.start_interactive_session("python")
    print(f"Started session: {session_id}")
    
    # Execute code in session
    session_result = await engine.execute_in_session(
        session_id,
        "x = 42\nprint(f'The answer is {x}')"
    )
    print(f"Session output: {session_result.stdout}")
    
    # Get session info
    session_info = engine.get_session_info(session_id)
    print(f"Session executions: {session_info['executions_count']}")
    
    print("\n✅ Code execution demo completed!")

if __name__ == "__main__":
    asyncio.run(main())

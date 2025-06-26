#!/usr/bin/env python3
"""
Main Interface - Ideation Assistant
Complete orchestration interface for all capabilities
"""

import asyncio
import sys
import argparse
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

# Import all our integrated modules
from tool_integration import ToolOrchestrator
from secure_config import SecureConfig
from enhanced_planning_mode import EnhancedPlanningMode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IdeationAssistant:
    """Main Ideation Assistant interface"""
    
    def __init__(self):
        self.orchestrator = None
        self.config = SecureConfig()
        self.interactive_mode = False
    
    async def __aenter__(self):
        self.orchestrator = ToolOrchestrator()
        await self.orchestrator.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.orchestrator:
            await self.orchestrator.__aexit__(exc_type, exc_val, exc_tb)
    
    async def run_command(self, command: str, args: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run a command with the ideation assistant"""
        
        args = args or {}
        
        if command == "status":
            return await self._cmd_status()
        elif command == "setup":
            return await self._cmd_setup()
        elif command == "plan":
            return await self._cmd_plan(args)
        elif command == "develop":
            return await self._cmd_develop(args)
        elif command == "analyze":
            return await self._cmd_analyze(args)
        elif command == "github":
            return await self._cmd_github(args)
        elif command == "execute":
            return await self._cmd_execute(args)
        elif command == "workflow":
            return await self._cmd_workflow(args)
        elif command == "interactive":
            return await self._cmd_interactive()
        else:
            return {"error": f"Unknown command: {command}"}
    
    async def _cmd_status(self) -> Dict[str, Any]:
        """Show system status"""
        
        print("\n🎯 IDEATION ASSISTANT STATUS")
        print("="*50)
        
        # Configuration status
        validations = self.config.validate_configuration()
        config_status = all(validations.values())
        
        print(f"Configuration: {'✅ Complete' if config_status else '⚠️ Incomplete'}")
        
        if not config_status:
            print("Missing configuration:")
            for key, valid in validations.items():
                if not valid:
                    print(f"  ❌ {key}")
        
        # Capabilities
        capabilities = self.orchestrator.get_available_capabilities()
        print(f"\nAvailable Capabilities: {len(capabilities)}")
        for cap in capabilities:
            print(f"  ✅ {cap.name}")
        
        # System health
        security_check = self.config.check_security()
        security_status = "🛡️ Secure" if security_check["secure"] else "⚠️ Security Issues"
        print(f"\nSecurity Status: {security_status}")
        
        return {
            "configuration_complete": config_status,
            "capabilities_count": len(capabilities),
            "security_status": security_check["secure"]
        }
    
    async def _cmd_setup(self) -> Dict[str, Any]:
        """Setup and configure the system"""
        
        print("\n🔧 IDEATION ASSISTANT SETUP")
        print("="*50)
        
        # GitHub setup
        self.config.setup_github_credentials()
        
        # API keys setup
        self.config.setup_api_keys()
        
        # Create environment template
        self.config.create_env_template()
        
        # Security check
        security = self.config.check_security()
        
        print("\n✅ Setup completed!")
        print("Please restart your terminal and run 'source ~/.bashrc' to load environment variables.")
        
        return {
            "setup_completed": True,
            "security_issues": security["issues"],
            "warnings": security["warnings"]
        }
    
    async def _cmd_plan(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create an AI-powered plan"""
        
        domain = args.get("domain", "software_development")
        requirements = args.get("requirements", {})
        iterations = args.get("iterations", 3)
        
        print(f"\n🧠 AI-POWERED PLANNING")
        print(f"Domain: {domain}")
        print(f"Iterations: {iterations}")
        print("="*50)
        
        # Start planning session
        if self.orchestrator.planning_mode:
            session_id = await self.orchestrator.planning_mode.start_planning_session(
                domain=domain,
                requirements=requirements,
                max_iterations=iterations
            )
            
            print(f"✅ Planning session completed: {session_id}")
            
            # Display results
            self.orchestrator.planning_mode.display_planning_results(session_id)
            
            return {
                "session_id": session_id,
                "domain": domain,
                "iterations": iterations
            }
        else:
            print("❌ Planning mode not available (DeepSeek API key required)")
            return {"error": "Planning mode not available"}
    
    async def _cmd_develop(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Develop a complete project"""
        
        project_name = args.get("name", "new_project")
        language = args.get("language", "python")
        template = args.get("template", "default")
        
        print(f"\n🚀 PROJECT DEVELOPMENT")
        print(f"Project: {project_name}")
        print(f"Language: {language}")
        print(f"Template: {template}")
        print("="*50)
        
        # Execute complete development workflow
        workflow_requirements = {
            "domain": args.get("domain", "software_development"),
            "project_name": project_name,
            "description": args.get("description", "Generated project"),
            "language": language,
            "template": template,
            "create_github_repo": args.get("github", False),
            "run_tests": args.get("tests", False),
            "build": args.get("build", False)
        }
        
        # Add code files if provided
        if "files" in args:
            workflow_requirements["code_files"] = args["files"]
            workflow_requirements["main_file"] = args.get("main_file")
        
        workflow_id = await self.orchestrator.execute_complete_workflow(
            "complete_project_development",
            workflow_requirements
        )
        
        # Get workflow status
        status = self.orchestrator.get_workflow_status(workflow_id)
        
        print(f"✅ Development workflow completed: {workflow_id}")
        print(f"Status: {status['status']}")
        
        return {
            "workflow_id": workflow_id,
            "project_name": project_name,
            "status": status["status"]
        }
    
    async def _cmd_analyze(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code and projects"""
        
        project_path = args.get("path", ".")
        language = args.get("language", "python")
        
        print(f"\n🔍 CODE ANALYSIS")
        print(f"Path: {project_path}")
        print(f"Language: {language}")
        print("="*50)
        
        # Execute code analysis workflow
        workflow_requirements = {
            "project_path": project_path,
            "language": language,
            "improvement_goals": args.get("goals", ["code_quality", "performance"])
        }
        
        workflow_id = await self.orchestrator.execute_complete_workflow(
            "code_analysis_and_improvement",
            workflow_requirements
        )
        
        # Get results
        status = self.orchestrator.get_workflow_status(workflow_id)
        
        print(f"✅ Analysis completed: {workflow_id}")
        
        if "results" in status and "project_structure" in status["results"]:
            structure = status["results"]["project_structure"]
            print(f"Files analyzed: {structure['total_files']}")
            print(f"Languages found: {structure['languages']}")
        
        return {
            "workflow_id": workflow_id,
            "analysis_completed": True,
            "results": status.get("results", {})
        }
    
    async def _cmd_github(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """GitHub operations"""
        
        operation = args.get("operation", "status")
        
        print(f"\n🐙 GITHUB OPERATIONS")
        print(f"Operation: {operation}")
        print("="*50)
        
        if not self.orchestrator.github_integration:
            print("❌ GitHub integration not available (credentials required)")
            return {"error": "GitHub integration not available"}
        
        if operation == "create_repo":
            result = await self.orchestrator.execute_tool_command(
                "github",
                "create_repo",
                {
                    "name": args["name"],
                    "description": args.get("description", ""),
                    "private": args.get("private", False)
                }
            )
            
            if result["success"]:
                repo = result["repository"]
                print(f"✅ Repository created: {repo['full_name']}")
                print(f"URL: {repo['url']}")
            else:
                print(f"❌ Failed to create repository: {result.get('error')}")
            
            return result
        
        elif operation == "list_repos":
            # Get user repositories
            repos = await self.orchestrator.github_integration.github_manager.get_user_repositories()
            
            print(f"✅ Found {len(repos)} repositories:")
            for repo in repos[:10]:  # Show first 10
                print(f"  • {repo.full_name} ({repo.stars} ⭐)")
            
            return {
                "success": True,
                "repositories_count": len(repos),
                "repositories": [{"name": r.full_name, "stars": r.stars} for r in repos[:10]]
            }
        
        else:
            return {"error": f"Unknown GitHub operation: {operation}"}
    
    async def _cmd_execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code"""
        
        code = args.get("code", "")
        language = args.get("language", "python")
        file_path = args.get("file")
        
        print(f"\n⚡ CODE EXECUTION")
        print(f"Language: {language}")
        print("="*50)
        
        if file_path:
            # Execute file
            result = await self.orchestrator.execute_tool_command(
                "code",
                "execute_file",
                {"file_path": file_path}
            )
        else:
            # Execute code string
            result = await self.orchestrator.execute_tool_command(
                "code",
                "execute",
                {
                    "code": code,
                    "language": language,
                    "timeout": args.get("timeout", 30)
                }
            )
        
        if result["success"]:
            execution_result = result["result"]
            print(f"✅ Execution completed in {execution_result['execution_time']:.2f}s")
            
            if execution_result["stdout"]:
                print(f"\nOutput:\n{execution_result['stdout']}")
            
            if execution_result["stderr"]:
                print(f"\nErrors:\n{execution_result['stderr']}")
        else:
            print(f"❌ Execution failed: {result.get('error')}")
        
        return result
    
    async def _cmd_workflow(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Workflow operations"""
        
        operation = args.get("operation", "list")
        
        print(f"\n🔄 WORKFLOW OPERATIONS")
        print(f"Operation: {operation}")
        print("="*50)
        
        if operation == "list":
            # List active workflows
            active = self.orchestrator.active_workflows
            history = self.orchestrator.workflow_history[-5:]  # Last 5
            
            print(f"Active Workflows: {len(active)}")
            for workflow_id, workflow in active.items():
                print(f"  • {workflow_id}: {workflow.name} ({workflow.status})")
            
            print(f"\nRecent Workflows: {len(history)}")
            for workflow in history:
                print(f"  • {workflow.workflow_id}: {workflow.name} ({workflow.status})")
            
            return {
                "active_count": len(active),
                "recent_count": len(history)
            }
        
        elif operation == "status":
            workflow_id = args.get("id")
            if not workflow_id:
                return {"error": "Workflow ID required"}
            
            status = self.orchestrator.get_workflow_status(workflow_id)
            
            print(f"Workflow: {workflow_id}")
            print(f"Status: {status.get('status', 'Unknown')}")
            
            if "steps_completed" in status:
                print(f"Progress: {status['steps_completed']}/{status['total_steps']} steps")
            
            return status
        
        else:
            return {"error": f"Unknown workflow operation: {operation}"}
    
    async def _cmd_interactive(self) -> Dict[str, Any]:
        """Start interactive mode"""
        
        print("\n🎯 IDEATION ASSISTANT - INTERACTIVE MODE")
        print("="*50)
        print("Available commands:")
        print("  status     - Show system status")
        print("  plan       - Create AI-powered plan")
        print("  develop    - Develop a project")
        print("  analyze    - Analyze code")
        print("  github     - GitHub operations")
        print("  execute    - Execute code")
        print("  workflow   - Workflow operations")
        print("  help       - Show help")
        print("  exit       - Exit interactive mode")
        print()
        
        self.interactive_mode = True
        
        while self.interactive_mode:
            try:
                command_input = input("ideation> ").strip()
                
                if not command_input:
                    continue
                
                if command_input == "exit":
                    break
                elif command_input == "help":
                    await self._show_help()
                    continue
                
                # Parse command
                parts = command_input.split()
                command = parts[0]
                
                # Simple argument parsing for interactive mode
                args = {}
                for i in range(1, len(parts)):
                    if "=" in parts[i]:
                        key, value = parts[i].split("=", 1)
                        args[key] = value
                
                # Execute command
                result = await self.run_command(command, args)
                
                if "error" in result:
                    print(f"❌ Error: {result['error']}")
                
            except KeyboardInterrupt:
                print("\nExiting interactive mode...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        self.interactive_mode = False
        return {"interactive_mode_ended": True}
    
    async def _show_help(self):
        """Show detailed help"""
        
        print("\n📚 IDEATION ASSISTANT HELP")
        print("="*50)
        
        commands = {
            "status": "Show system status and configuration",
            "setup": "Setup and configure the system",
            "plan": "Create AI-powered planning session\n         Usage: plan domain=web_development iterations=3",
            "develop": "Develop a complete project\n           Usage: develop name=myapp language=python github=true",
            "analyze": "Analyze code and projects\n           Usage: analyze path=./myproject language=python",
            "github": "GitHub operations\n          Usage: github operation=create_repo name=myrepo",
            "execute": "Execute code\n           Usage: execute language=python code='print(\"hello\")'",
            "workflow": "Workflow operations\n            Usage: workflow operation=list",
            "interactive": "Enter interactive mode",
            "help": "Show this help message",
            "exit": "Exit (in interactive mode)"
        }
        
        for cmd, desc in commands.items():
            print(f"\n{cmd}:")
            print(f"  {desc}")

def create_parser():
    """Create command line argument parser"""
    
    parser = argparse.ArgumentParser(
        description="Ideation Assistant - AI-powered development tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status command
    subparsers.add_parser("status", help="Show system status")
    
    # Setup command
    subparsers.add_parser("setup", help="Setup and configure system")
    
    # Plan command
    plan_parser = subparsers.add_parser("plan", help="Create AI-powered plan")
    plan_parser.add_argument("--domain", default="software_development", help="Project domain")
    plan_parser.add_argument("--iterations", type=int, default=3, help="Planning iterations")
    plan_parser.add_argument("--requirements", help="Requirements JSON file")
    
    # Develop command
    dev_parser = subparsers.add_parser("develop", help="Develop a project")
    dev_parser.add_argument("--name", required=True, help="Project name")
    dev_parser.add_argument("--language", default="python", help="Programming language")
    dev_parser.add_argument("--template", default="default", help="Project template")
    dev_parser.add_argument("--description", help="Project description")
    dev_parser.add_argument("--github", action="store_true", help="Create GitHub repository")
    dev_parser.add_argument("--tests", action="store_true", help="Run tests")
    dev_parser.add_argument("--build", action="store_true", help="Build project")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze code")
    analyze_parser.add_argument("--path", default=".", help="Project path")
    analyze_parser.add_argument("--language", default="python", help="Programming language")
    
    # GitHub command
    github_parser = subparsers.add_parser("github", help="GitHub operations")
    github_parser.add_argument("--operation", required=True, 
                              choices=["create_repo", "list_repos"],
                              help="GitHub operation")
    github_parser.add_argument("--name", help="Repository name")
    github_parser.add_argument("--description", help="Repository description")
    github_parser.add_argument("--private", action="store_true", help="Private repository")
    
    # Execute command
    exec_parser = subparsers.add_parser("execute", help="Execute code")
    exec_parser.add_argument("--language", default="python", help="Programming language")
    exec_parser.add_argument("--code", help="Code to execute")
    exec_parser.add_argument("--file", help="File to execute")
    exec_parser.add_argument("--timeout", type=int, default=30, help="Execution timeout")
    
    # Workflow command
    workflow_parser = subparsers.add_parser("workflow", help="Workflow operations")
    workflow_parser.add_argument("--operation", default="list",
                                choices=["list", "status"],
                                help="Workflow operation")
    workflow_parser.add_argument("--id", help="Workflow ID")
    
    # Interactive command
    subparsers.add_parser("interactive", help="Start interactive mode")
    
    return parser

async def main():
    """Main entry point"""
    
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        # No command provided, show help and start interactive mode
        parser.print_help()
        print("\nStarting interactive mode...\n")
        args.command = "interactive"
    
    async with IdeationAssistant() as assistant:
        
        # Convert args to dict
        args_dict = vars(args).copy()
        del args_dict["command"]  # Remove command from args
        
        # Handle requirements file for plan command
        if args.command == "plan" and args_dict.get("requirements"):
            req_file = Path(args_dict["requirements"])
            if req_file.exists():
                with open(req_file) as f:
                    args_dict["requirements"] = json.load(f)
            else:
                args_dict["requirements"] = {}
        
        # Execute command
        try:
            result = await assistant.run_command(args.command, args_dict)
            
            if "error" in result:
                print(f"\n❌ Error: {result['error']}")
                sys.exit(1)
            
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
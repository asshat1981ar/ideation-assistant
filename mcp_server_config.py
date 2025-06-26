#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server Configuration
Setup and management of predefined MCP servers for enhanced capabilities
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    command: List[str]
    args: List[str] = None
    env: Dict[str, str] = None
    working_directory: str = None
    description: str = ""
    capabilities: List[str] = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.args is None:
            self.args = []
        if self.env is None:
            self.env = {}
        if self.capabilities is None:
            self.capabilities = []

@dataclass
class MCPTool:
    """MCP tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: str
    server: str
    examples: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.examples is None:
            self.examples = []

@dataclass
class MCPResource:
    """MCP resource definition"""
    uri: str
    name: str
    description: str
    mime_type: str
    server: str

class MCPServerManager:
    """Manager for MCP servers and their capabilities"""
    
    def __init__(self, config_dir: str = "./mcp_config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.servers: Dict[str, MCPServerConfig] = {}
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.running_servers: Dict[str, subprocess.Popen] = {}
        
        self._load_predefined_servers()
    
    def _load_predefined_servers(self):
        """Load predefined MCP server configurations"""
        
        # File System Server
        self.servers["filesystem"] = MCPServerConfig(
            name="filesystem",
            command=["npx", "-y", "@modelcontextprotocol/server-filesystem"],
            args=[str(Path.cwd())],
            description="File system operations and management",
            capabilities=[
                "file_read", "file_write", "directory_list",
                "file_search", "file_operations"
            ]
        )
        
        # Git Server
        self.servers["git"] = MCPServerConfig(
            name="git",
            command=["npx", "-y", "@modelcontextprotocol/server-git"],
            args=[str(Path.cwd())],
            description="Git repository operations and version control",
            capabilities=[
                "git_status", "git_log", "git_diff", "git_branch",
                "git_commit", "git_push", "git_pull"
            ]
        )
        
        # Web Search Server
        self.servers["search"] = MCPServerConfig(
            name="search",
            command=["npx", "-y", "@modelcontextprotocol/server-brave-search"],
            env={"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY", "")},
            description="Web search and information retrieval",
            capabilities=[
                "web_search", "news_search", "image_search",
                "local_search", "video_search"
            ]
        )
        
        # Database Server
        self.servers["database"] = MCPServerConfig(
            name="database",
            command=["npx", "-y", "@modelcontextprotocol/server-sqlite"],
            args=["./data/ideation.db"],
            description="Database operations and data management",
            capabilities=[
                "sql_query", "table_operations", "data_analysis",
                "schema_management", "backup_restore"
            ]
        )
        
        # Code Analysis Server
        self.servers["code_analysis"] = MCPServerConfig(
            name="code_analysis",
            command=["python", "-m", "mcp_servers.code_analysis"],
            description="Code analysis and quality assessment",
            capabilities=[
                "code_complexity", "code_quality", "security_scan",
                "dependency_analysis", "test_coverage"
            ]
        )
        
        # Planning Server
        self.servers["planning"] = MCPServerConfig(
            name="planning",
            command=["python", "-m", "mcp_servers.planning"],
            description="Project planning and management capabilities",
            capabilities=[
                "project_planning", "resource_estimation", "risk_analysis",
                "timeline_planning", "dependency_mapping"
            ]
        )
        
        # API Integration Server
        self.servers["api_integration"] = MCPServerConfig(
            name="api_integration",
            command=["python", "-m", "mcp_servers.api_integration"],
            description="External API integration and management",
            capabilities=[
                "api_discovery", "api_testing", "webhook_management",
                "rate_limiting", "api_documentation"
            ]
        )
        
        self._register_tools()
        self._register_resources()
    
    def _register_tools(self):
        """Register tools provided by MCP servers"""
        
        # Filesystem tools
        self.tools["read_file"] = MCPTool(
            name="read_file",
            description="Read contents of a file",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"}
                },
                "required": ["path"]
            },
            handler="filesystem.read_file",
            server="filesystem",
            examples=[
                {"path": "./README.md"},
                {"path": "./src/main.py"}
            ]
        )
        
        self.tools["write_file"] = MCPTool(
            name="write_file",
            description="Write content to a file",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write"},
                    "content": {"type": "string", "description": "Content to write"}
                },
                "required": ["path", "content"]
            },
            handler="filesystem.write_file",
            server="filesystem"
        )
        
        # Git tools
        self.tools["git_status"] = MCPTool(
            name="git_status",
            description="Get git repository status",
            input_schema={"type": "object", "properties": {}},
            handler="git.status",
            server="git"
        )
        
        self.tools["git_commit"] = MCPTool(
            name="git_commit",
            description="Create a git commit",
            input_schema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Commit message"},
                    "files": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["message"]
            },
            handler="git.commit",
            server="git"
        )
        
        # Search tools
        self.tools["web_search"] = MCPTool(
            name="web_search",
            description="Search the web for information",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "count": {"type": "integer", "description": "Number of results", "default": 10}
                },
                "required": ["query"]
            },
            handler="search.web_search",
            server="search"
        )
        
        # Database tools
        self.tools["sql_query"] = MCPTool(
            name="sql_query",
            description="Execute SQL query",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL query to execute"},
                    "params": {"type": "array", "description": "Query parameters"}
                },
                "required": ["query"]
            },
            handler="database.query",
            server="database"
        )
        
        # Code analysis tools
        self.tools["analyze_code"] = MCPTool(
            name="analyze_code",
            description="Analyze code quality and complexity",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to analyze"},
                    "language": {"type": "string", "description": "Programming language"}
                },
                "required": ["path"]
            },
            handler="code_analysis.analyze",
            server="code_analysis"
        )
        
        # Planning tools
        self.tools["create_project_plan"] = MCPTool(
            name="create_project_plan",
            description="Create detailed project plan",
            input_schema={
                "type": "object",
                "properties": {
                    "requirements": {"type": "object", "description": "Project requirements"},
                    "constraints": {"type": "object", "description": "Project constraints"},
                    "domain": {"type": "string", "description": "Project domain"}
                },
                "required": ["requirements"]
            },
            handler="planning.create_plan",
            server="planning"
        )
    
    def _register_resources(self):
        """Register resources provided by MCP servers"""
        
        self.resources["project_files"] = MCPResource(
            uri="file://project/*",
            name="Project Files",
            description="Access to project files and directories",
            mime_type="text/plain",
            server="filesystem"
        )
        
        self.resources["git_history"] = MCPResource(
            uri="git://history",
            name="Git History",
            description="Git repository history and changes",
            mime_type="application/json",
            server="git"
        )
        
        self.resources["search_results"] = MCPResource(
            uri="search://results/*",
            name="Search Results",
            description="Web search results and cached data",
            mime_type="application/json",
            server="search"
        )
    
    async def start_server(self, server_name: str) -> bool:
        """Start an MCP server"""
        
        if server_name not in self.servers:
            logger.error(f"Server {server_name} not found")
            return False
        
        if server_name in self.running_servers:
            logger.warning(f"Server {server_name} already running")
            return True
        
        config = self.servers[server_name]
        
        if not config.enabled:
            logger.info(f"Server {server_name} is disabled")
            return False
        
        try:
            cmd = config.command + config.args
            env = {**os.environ, **config.env}
            
            process = subprocess.Popen(
                cmd,
                env=env,
                cwd=config.working_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.running_servers[server_name] = process
            logger.info(f"Started MCP server: {server_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start server {server_name}: {e}")
            return False
    
    async def stop_server(self, server_name: str) -> bool:
        """Stop an MCP server"""
        
        if server_name not in self.running_servers:
            logger.warning(f"Server {server_name} not running")
            return True
        
        try:
            process = self.running_servers[server_name]
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            del self.running_servers[server_name]
            logger.info(f"Stopped MCP server: {server_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop server {server_name}: {e}")
            return False
    
    async def start_all_servers(self) -> Dict[str, bool]:
        """Start all enabled MCP servers"""
        
        results = {}
        
        for server_name, config in self.servers.items():
            if config.enabled:
                results[server_name] = await self.start_server(server_name)
            else:
                results[server_name] = False
        
        return results
    
    async def stop_all_servers(self) -> Dict[str, bool]:
        """Stop all running MCP servers"""
        
        results = {}
        
        for server_name in list(self.running_servers.keys()):
            results[server_name] = await self.stop_server(server_name)
        
        return results
    
    def get_server_status(self, server_name: str) -> Dict[str, Any]:
        """Get status of an MCP server"""
        
        if server_name not in self.servers:
            return {"status": "not_found"}
        
        config = self.servers[server_name]
        is_running = server_name in self.running_servers
        
        status = {
            "name": server_name,
            "enabled": config.enabled,
            "running": is_running,
            "description": config.description,
            "capabilities": config.capabilities,
            "tools_count": len([t for t in self.tools.values() if t.server == server_name]),
            "resources_count": len([r for r in self.resources.values() if r.server == server_name])
        }
        
        if is_running:
            process = self.running_servers[server_name]
            status["pid"] = process.pid
            status["returncode"] = process.returncode
        
        return status
    
    def get_all_servers_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all MCP servers"""
        
        return {
            server_name: self.get_server_status(server_name)
            for server_name in self.servers.keys()
        }
    
    def get_available_tools(self, server_name: str = None) -> List[MCPTool]:
        """Get available tools, optionally filtered by server"""
        
        if server_name:
            return [tool for tool in self.tools.values() if tool.server == server_name]
        
        return list(self.tools.values())
    
    def get_available_resources(self, server_name: str = None) -> List[MCPResource]:
        """Get available resources, optionally filtered by server"""
        
        if server_name:
            return [resource for resource in self.resources.values() if resource.server == server_name]
        
        return list(self.resources.values())
    
    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Call an MCP tool"""
        
        if tool_name not in self.tools:
            return {"error": f"Tool {tool_name} not found"}
        
        tool = self.tools[tool_name]
        
        if tool.server not in self.running_servers:
            return {"error": f"Server {tool.server} not running"}
        
        # Simulate tool call - in real implementation, this would use MCP protocol
        result = {
            "tool": tool_name,
            "server": tool.server,
            "input": kwargs,
            "timestamp": datetime.now().isoformat(),
            "result": "Mock tool execution result",
            "success": True
        }
        
        logger.info(f"Called tool {tool_name} on server {tool.server}")
        return result
    
    def save_configuration(self, config_file: str = "mcp_config.json"):
        """Save MCP configuration to file"""
        
        config_path = self.config_dir / config_file
        
        config_data = {
            "servers": {name: asdict(config) for name, config in self.servers.items()},
            "tools": {name: asdict(tool) for name, tool in self.tools.items()},
            "resources": {name: asdict(resource) for name, resource in self.resources.items()},
            "saved_at": datetime.now().isoformat()
        }
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2, default=str)
        
        logger.info(f"Saved MCP configuration to {config_path}")
    
    def load_configuration(self, config_file: str = "mcp_config.json"):
        """Load MCP configuration from file"""
        
        config_path = self.config_dir / config_file
        
        if not config_path.exists():
            logger.warning(f"Configuration file {config_path} not found")
            return
        
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Load servers
            if "servers" in config_data:
                for name, server_data in config_data["servers"].items():
                    self.servers[name] = MCPServerConfig(**server_data)
            
            # Load tools
            if "tools" in config_data:
                for name, tool_data in config_data["tools"].items():
                    self.tools[name] = MCPTool(**tool_data)
            
            # Load resources
            if "resources" in config_data:
                for name, resource_data in config_data["resources"].items():
                    self.resources[name] = MCPResource(**resource_data)
            
            logger.info(f"Loaded MCP configuration from {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")

class EnhancedMCPIntegration:
    """Enhanced MCP integration for planning and development"""
    
    def __init__(self, server_manager: MCPServerManager):
        self.server_manager = server_manager
        self.tool_registry = {}
        self.capability_map = {}
        
        self._build_capability_map()
    
    def _build_capability_map(self):
        """Build capability to tool mapping"""
        
        for tool in self.server_manager.get_available_tools():
            for capability in self.server_manager.servers[tool.server].capabilities:
                if capability not in self.capability_map:
                    self.capability_map[capability] = []
                self.capability_map[capability].append(tool.name)
    
    async def execute_planning_workflow(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Execute enhanced planning workflow using MCP tools"""
        
        workflow_results = {
            "requirements": requirements,
            "steps": [],
            "tools_used": [],
            "resources_accessed": [],
            "final_output": None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Step 1: Analyze requirements
        if "analyze_code" in self.server_manager.tools:
            analysis_result = await self.server_manager.call_tool(
                "analyze_code",
                path=requirements.get("project_path", "."),
                language=requirements.get("language", "python")
            )
            workflow_results["steps"].append({
                "step": "code_analysis",
                "result": analysis_result
            })
            workflow_results["tools_used"].append("analyze_code")
        
        # Step 2: Search for best practices
        if "web_search" in self.server_manager.tools:
            search_result = await self.server_manager.call_tool(
                "web_search",
                query=f"{requirements.get('domain', 'software')} best practices architecture",
                count=5
            )
            workflow_results["steps"].append({
                "step": "research",
                "result": search_result
            })
            workflow_results["tools_used"].append("web_search")
        
        # Step 3: Create project plan
        if "create_project_plan" in self.server_manager.tools:
            plan_result = await self.server_manager.call_tool(
                "create_project_plan",
                requirements=requirements,
                domain=requirements.get("domain", "software_development")
            )
            workflow_results["steps"].append({
                "step": "planning",
                "result": plan_result
            })
            workflow_results["tools_used"].append("create_project_plan")
            workflow_results["final_output"] = plan_result
        
        return workflow_results
    
    def get_recommended_tools(self, task_type: str) -> List[str]:
        """Get recommended tools for a task type"""
        
        task_capability_map = {
            "file_operations": ["file_read", "file_write", "directory_list"],
            "code_analysis": ["analyze_code", "code_quality", "security_scan"],
            "project_planning": ["create_project_plan", "resource_estimation"],
            "research": ["web_search", "api_discovery"],
            "version_control": ["git_status", "git_commit", "git_diff"],
            "data_management": ["sql_query", "backup_restore"]
        }
        
        return task_capability_map.get(task_type, [])
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all MCP servers"""
        
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "servers": {},
            "overall_status": "healthy",
            "available_tools": len(self.server_manager.tools),
            "available_resources": len(self.server_manager.resources)
        }
        
        for server_name in self.server_manager.servers.keys():
            status = self.server_manager.get_server_status(server_name)
            health_status["servers"][server_name] = status
            
            if status.get("enabled") and not status.get("running"):
                health_status["overall_status"] = "degraded"
        
        return health_status

async def main():
    """Demo MCP server configuration and management"""
    
    print("🔧 MCP Server Configuration Demo")
    print("=" * 50)
    
    # Initialize MCP server manager
    manager = MCPServerManager()
    
    # Display available servers
    print("\nAvailable MCP Servers:")
    for server_name, config in manager.servers.items():
        print(f"  • {server_name}: {config.description}")
        print(f"    Capabilities: {', '.join(config.capabilities[:3])}...")
    
    # Display available tools
    print(f"\nAvailable Tools: {len(manager.tools)}")
    for tool_name, tool in list(manager.tools.items())[:5]:
        print(f"  • {tool_name} ({tool.server}): {tool.description}")
    
    # Start some servers
    print("\nStarting MCP servers...")
    start_results = await manager.start_all_servers()
    
    for server_name, started in start_results.items():
        status = "✅ Started" if started else "❌ Failed"
        print(f"  {server_name}: {status}")
    
    # Get server status
    print("\nServer Status:")
    all_status = manager.get_all_servers_status()
    for server_name, status in all_status.items():
        print(f"  {server_name}: {'🟢 Running' if status['running'] else '🔴 Stopped'}")
    
    # Demo enhanced integration
    print("\nEnhanced MCP Integration Demo:")
    enhanced = EnhancedMCPIntegration(manager)
    
    # Health check
    health = await enhanced.health_check()
    print(f"Overall Status: {health['overall_status']}")
    print(f"Available Tools: {health['available_tools']}")
    
    # Demo planning workflow
    requirements = {
        "domain": "web_development",
        "project_path": ".",
        "language": "python",
        "target_users": 1000
    }
    
    workflow_result = await enhanced.execute_planning_workflow(requirements)
    print(f"Planning workflow completed with {len(workflow_result['steps'])} steps")
    print(f"Tools used: {', '.join(workflow_result['tools_used'])}")
    
    # Save configuration
    manager.save_configuration()
    
    # Stop servers
    print("\nStopping servers...")
    await manager.stop_all_servers()

if __name__ == "__main__":
    asyncio.run(main())
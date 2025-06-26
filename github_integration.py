#!/usr/bin/env python3
"""
GitHub Integration
Complete GitHub repository management and automation
"""

import asyncio
import os
import json
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import aiohttp
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GitRepository:
    """Git repository information"""
    name: str
    url: str
    branch: str
    local_path: str
    remote: str = "origin"
    is_clean: bool = True
    ahead_commits: int = 0
    behind_commits: int = 0
    modified_files: List[str] = None
    untracked_files: List[str] = None
    
    def __post_init__(self):
        if self.modified_files is None:
            self.modified_files = []
        if self.untracked_files is None:
            self.untracked_files = []

@dataclass
class GitHubRepository:
    """GitHub repository metadata"""
    id: int
    name: str
    full_name: str
    description: str
    url: str
    clone_url: str
    ssh_url: str
    default_branch: str
    private: bool
    language: str
    stars: int
    forks: int
    created_at: datetime
    updated_at: datetime
    topics: List[str] = None
    
    def __post_init__(self):
        if self.topics is None:
            self.topics = []

@dataclass
class PullRequest:
    """Pull request information"""
    number: int
    title: str
    description: str
    source_branch: str
    target_branch: str
    state: str
    author: str
    created_at: datetime
    mergeable: bool = True
    checks_passing: bool = True

@dataclass
class Issue:
    """GitHub issue information"""
    number: int
    title: str
    description: str
    state: str
    author: str
    assignees: List[str]
    labels: List[str]
    created_at: datetime
    updated_at: datetime

class GitManager:
    """Local Git operations manager"""
    
    def __init__(self):
        self.repositories: Dict[str, GitRepository] = {}
    
    async def init_repository(self, path: str, remote_url: str = None) -> GitRepository:
        """Initialize a new Git repository"""
        
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🔧 Initializing Git repository: {path}")
        
        # Initialize git repo
        result = await self._run_git_command(["git", "init"], cwd=path)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to initialize git repository: {result.stderr}")
        
        # Add remote if provided
        if remote_url:
            await self._run_git_command(
                ["git", "remote", "add", "origin", remote_url], 
                cwd=path
            )
        
        repo = GitRepository(
            name=path.name,
            url=remote_url or "",
            branch="main",
            local_path=str(path)
        )
        
        self.repositories[str(path)] = repo
        
        logger.info(f"✅ Repository initialized: {path}")
        return repo
    
    async def clone_repository(self, url: str, local_path: str, branch: str = None) -> GitRepository:
        """Clone a repository from URL"""
        
        local_path = Path(local_path)
        
        logger.info(f"📥 Cloning repository: {url}")
        
        cmd = ["git", "clone"]
        if branch:
            cmd.extend(["-b", branch])
        cmd.extend([url, str(local_path)])
        
        result = await self._run_git_command(cmd)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to clone repository: {result.stderr}")
        
        # Get repository info
        repo_info = await self.get_repository_status(str(local_path))
        
        self.repositories[str(local_path)] = repo_info
        
        logger.info(f"✅ Repository cloned: {local_path}")
        return repo_info
    
    async def get_repository_status(self, repo_path: str) -> GitRepository:
        """Get comprehensive repository status"""
        
        repo_path = Path(repo_path)
        
        if not (repo_path / ".git").exists():
            raise ValueError(f"Not a git repository: {repo_path}")
        
        # Get basic info
        name = repo_path.name
        
        # Get remote URL
        remote_result = await self._run_git_command(
            ["git", "remote", "get-url", "origin"], 
            cwd=repo_path
        )
        url = remote_result.stdout.strip() if remote_result.returncode == 0 else ""
        
        # Get current branch
        branch_result = await self._run_git_command(
            ["git", "branch", "--show-current"], 
            cwd=repo_path
        )
        branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "main"
        
        # Get status
        status_result = await self._run_git_command(
            ["git", "status", "--porcelain"], 
            cwd=repo_path
        )
        
        modified_files = []
        untracked_files = []
        
        if status_result.returncode == 0:
            for line in status_result.stdout.strip().split('\n'):
                if line:
                    status_code = line[:2]
                    filename = line[3:]
                    
                    if status_code.strip() == '??':
                        untracked_files.append(filename)
                    else:
                        modified_files.append(filename)
        
        is_clean = len(modified_files) == 0 and len(untracked_files) == 0
        
        # Get ahead/behind info
        ahead_behind = await self._get_ahead_behind_count(repo_path, branch)
        
        repo = GitRepository(
            name=name,
            url=url,
            branch=branch,
            local_path=str(repo_path),
            is_clean=is_clean,
            ahead_commits=ahead_behind[0],
            behind_commits=ahead_behind[1],
            modified_files=modified_files,
            untracked_files=untracked_files
        )
        
        return repo
    
    async def _get_ahead_behind_count(self, repo_path: Path, branch: str) -> Tuple[int, int]:
        """Get ahead/behind commit count"""
        
        try:
            result = await self._run_git_command(
                ["git", "rev-list", "--left-right", "--count", f"origin/{branch}...HEAD"],
                cwd=repo_path
            )
            
            if result.returncode == 0:
                behind, ahead = result.stdout.strip().split('\t')
                return int(ahead), int(behind)
        except:
            pass
        
        return 0, 0
    
    async def commit_changes(self, 
                           repo_path: str,
                           message: str,
                           files: List[str] = None,
                           add_all: bool = False) -> bool:
        """Commit changes to repository"""
        
        repo_path = Path(repo_path)
        
        logger.info(f"💾 Committing changes: {message}")
        
        try:
            # Add files
            if add_all:
                await self._run_git_command(["git", "add", "."], cwd=repo_path)
            elif files:
                for file in files:
                    await self._run_git_command(["git", "add", file], cwd=repo_path)
            
            # Commit
            result = await self._run_git_command(
                ["git", "commit", "-m", message], 
                cwd=repo_path
            )
            
            if result.returncode == 0:
                logger.info("✅ Changes committed successfully")
                return True
            else:
                logger.error(f"Commit failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Commit error: {e}")
            return False
    
    async def push_changes(self, repo_path: str, branch: str = None) -> bool:
        """Push changes to remote repository"""
        
        repo_path = Path(repo_path)
        
        logger.info(f"📤 Pushing changes to remote")
        
        try:
            cmd = ["git", "push"]
            if branch:
                cmd.extend(["origin", branch])
            
            result = await self._run_git_command(cmd, cwd=repo_path)
            
            if result.returncode == 0:
                logger.info("✅ Changes pushed successfully")
                return True
            else:
                logger.error(f"Push failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Push error: {e}")
            return False
    
    async def pull_changes(self, repo_path: str, branch: str = None) -> bool:
        """Pull changes from remote repository"""
        
        repo_path = Path(repo_path)
        
        logger.info(f"📥 Pulling changes from remote")
        
        try:
            cmd = ["git", "pull"]
            if branch:
                cmd.extend(["origin", branch])
            
            result = await self._run_git_command(cmd, cwd=repo_path)
            
            if result.returncode == 0:
                logger.info("✅ Changes pulled successfully")
                return True
            else:
                logger.error(f"Pull failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Pull error: {e}")
            return False
    
    async def create_branch(self, repo_path: str, branch_name: str, checkout: bool = True) -> bool:
        """Create a new branch"""
        
        repo_path = Path(repo_path)
        
        logger.info(f"🌿 Creating branch: {branch_name}")
        
        try:
            # Create branch
            result = await self._run_git_command(
                ["git", "branch", branch_name], 
                cwd=repo_path
            )
            
            if result.returncode != 0:
                logger.error(f"Branch creation failed: {result.stderr}")
                return False
            
            # Checkout if requested
            if checkout:
                result = await self._run_git_command(
                    ["git", "checkout", branch_name], 
                    cwd=repo_path
                )
                
                if result.returncode != 0:
                    logger.error(f"Branch checkout failed: {result.stderr}")
                    return False
            
            logger.info(f"✅ Branch created: {branch_name}")
            return True
            
        except Exception as e:
            logger.error(f"Branch creation error: {e}")
            return False
    
    async def _run_git_command(self, cmd: List[str], cwd: Path = None) -> subprocess.CompletedProcess:
        """Run git command asynchronously"""
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = await process.communicate()
        
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=process.returncode,
            stdout=stdout,
            stderr=stderr
        )

class GitHubManager:
    """GitHub API operations manager"""
    
    def __init__(self, token: str = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.session = None
        
        if not self.token:
            logger.warning("No GitHub token found. Set GITHUB_TOKEN environment variable.")
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests"""
        
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Ideation-Assistant/1.0"
        }
        
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        
        return headers
    
    async def get_user_repositories(self, username: str = None) -> List[GitHubRepository]:
        """Get user repositories"""
        
        if not self.token and not username:
            raise ValueError("GitHub token or username required")
        
        url = f"{self.base_url}/user/repos" if not username else f"{self.base_url}/users/{username}/repos"
        
        logger.info(f"📋 Fetching repositories for: {username or 'authenticated user'}")
        
        repositories = []
        
        async with self.session.get(url, headers=self._get_headers()) as response:
            if response.status == 200:
                repos_data = await response.json()
                
                for repo_data in repos_data:
                    repo = GitHubRepository(
                        id=repo_data["id"],
                        name=repo_data["name"],
                        full_name=repo_data["full_name"],
                        description=repo_data.get("description", ""),
                        url=repo_data["html_url"],
                        clone_url=repo_data["clone_url"],
                        ssh_url=repo_data["ssh_url"],
                        default_branch=repo_data["default_branch"],
                        private=repo_data["private"],
                        language=repo_data.get("language", ""),
                        stars=repo_data["stargazers_count"],
                        forks=repo_data["forks_count"],
                        created_at=datetime.fromisoformat(repo_data["created_at"].replace('Z', '+00:00')),
                        updated_at=datetime.fromisoformat(repo_data["updated_at"].replace('Z', '+00:00')),
                        topics=repo_data.get("topics", [])
                    )
                    repositories.append(repo)
                
                logger.info(f"✅ Found {len(repositories)} repositories")
            else:
                logger.error(f"Failed to fetch repositories: {response.status}")
        
        return repositories
    
    async def create_repository(self, 
                              name: str,
                              description: str = "",
                              private: bool = False,
                              auto_init: bool = True) -> GitHubRepository:
        """Create a new repository"""
        
        if not self.token:
            raise ValueError("GitHub token required for repository creation")
        
        logger.info(f"🏗️ Creating repository: {name}")
        
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": auto_init
        }
        
        async with self.session.post(
            f"{self.base_url}/user/repos",
            headers=self._get_headers(),
            json=data
        ) as response:
            if response.status == 201:
                repo_data = await response.json()
                
                repo = GitHubRepository(
                    id=repo_data["id"],
                    name=repo_data["name"],
                    full_name=repo_data["full_name"],
                    description=repo_data.get("description", ""),
                    url=repo_data["html_url"],
                    clone_url=repo_data["clone_url"],
                    ssh_url=repo_data["ssh_url"],
                    default_branch=repo_data["default_branch"],
                    private=repo_data["private"],
                    language=repo_data.get("language", ""),
                    stars=repo_data["stargazers_count"],
                    forks=repo_data["forks_count"],
                    created_at=datetime.fromisoformat(repo_data["created_at"].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(repo_data["updated_at"].replace('Z', '+00:00'))
                )
                
                logger.info(f"✅ Repository created: {repo.full_name}")
                return repo
            else:
                error_data = await response.json()
                raise RuntimeError(f"Failed to create repository: {error_data}")
    
    async def create_pull_request(self, 
                                owner: str,
                                repo: str,
                                title: str,
                                head: str,
                                base: str,
                                description: str = "") -> PullRequest:
        """Create a pull request"""
        
        if not self.token:
            raise ValueError("GitHub token required for pull request creation")
        
        logger.info(f"🔄 Creating pull request: {title}")
        
        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": description
        }
        
        async with self.session.post(
            f"{self.base_url}/repos/{owner}/{repo}/pulls",
            headers=self._get_headers(),
            json=data
        ) as response:
            if response.status == 201:
                pr_data = await response.json()
                
                pr = PullRequest(
                    number=pr_data["number"],
                    title=pr_data["title"],
                    description=pr_data.get("body", ""),
                    source_branch=pr_data["head"]["ref"],
                    target_branch=pr_data["base"]["ref"],
                    state=pr_data["state"],
                    author=pr_data["user"]["login"],
                    created_at=datetime.fromisoformat(pr_data["created_at"].replace('Z', '+00:00')),
                    mergeable=pr_data.get("mergeable", True)
                )
                
                logger.info(f"✅ Pull request created: #{pr.number}")
                return pr
            else:
                error_data = await response.json()
                raise RuntimeError(f"Failed to create pull request: {error_data}")
    
    async def get_pull_requests(self, owner: str, repo: str, state: str = "open") -> List[PullRequest]:
        """Get pull requests for repository"""
        
        logger.info(f"📋 Fetching pull requests for {owner}/{repo}")
        
        params = {"state": state}
        
        async with self.session.get(
            f"{self.base_url}/repos/{owner}/{repo}/pulls",
            headers=self._get_headers(),
            params=params
        ) as response:
            if response.status == 200:
                prs_data = await response.json()
                
                pull_requests = []
                for pr_data in prs_data:
                    pr = PullRequest(
                        number=pr_data["number"],
                        title=pr_data["title"],
                        description=pr_data.get("body", ""),
                        source_branch=pr_data["head"]["ref"],
                        target_branch=pr_data["base"]["ref"],
                        state=pr_data["state"],
                        author=pr_data["user"]["login"],
                        created_at=datetime.fromisoformat(pr_data["created_at"].replace('Z', '+00:00')),
                        mergeable=pr_data.get("mergeable", True)
                    )
                    pull_requests.append(pr)
                
                logger.info(f"✅ Found {len(pull_requests)} pull requests")
                return pull_requests
            else:
                logger.error(f"Failed to fetch pull requests: {response.status}")
                return []
    
    async def create_issue(self, 
                         owner: str,
                         repo: str,
                         title: str,
                         description: str = "",
                         labels: List[str] = None,
                         assignees: List[str] = None) -> Issue:
        """Create a new issue"""
        
        if not self.token:
            raise ValueError("GitHub token required for issue creation")
        
        logger.info(f"🐛 Creating issue: {title}")
        
        data = {
            "title": title,
            "body": description
        }
        
        if labels:
            data["labels"] = labels
        
        if assignees:
            data["assignees"] = assignees
        
        async with self.session.post(
            f"{self.base_url}/repos/{owner}/{repo}/issues",
            headers=self._get_headers(),
            json=data
        ) as response:
            if response.status == 201:
                issue_data = await response.json()
                
                issue = Issue(
                    number=issue_data["number"],
                    title=issue_data["title"],
                    description=issue_data.get("body", ""),
                    state=issue_data["state"],
                    author=issue_data["user"]["login"],
                    assignees=[assignee["login"] for assignee in issue_data.get("assignees", [])],
                    labels=[label["name"] for label in issue_data.get("labels", [])],
                    created_at=datetime.fromisoformat(issue_data["created_at"].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(issue_data["updated_at"].replace('Z', '+00:00'))
                )
                
                logger.info(f"✅ Issue created: #{issue.number}")
                return issue
            else:
                error_data = await response.json()
                raise RuntimeError(f"Failed to create issue: {error_data}")
    
    async def search_repositories(self, 
                                query: str,
                                language: str = None,
                                sort: str = "stars",
                                order: str = "desc",
                                limit: int = 30) -> List[GitHubRepository]:
        """Search repositories"""
        
        logger.info(f"🔍 Searching repositories: {query}")
        
        search_query = query
        if language:
            search_query += f" language:{language}"
        
        params = {
            "q": search_query,
            "sort": sort,
            "order": order,
            "per_page": min(limit, 100)
        }
        
        async with self.session.get(
            f"{self.base_url}/search/repositories",
            headers=self._get_headers(),
            params=params
        ) as response:
            if response.status == 200:
                search_data = await response.json()
                
                repositories = []
                for repo_data in search_data.get("items", []):
                    repo = GitHubRepository(
                        id=repo_data["id"],
                        name=repo_data["name"],
                        full_name=repo_data["full_name"],
                        description=repo_data.get("description", ""),
                        url=repo_data["html_url"],
                        clone_url=repo_data["clone_url"],
                        ssh_url=repo_data["ssh_url"],
                        default_branch=repo_data["default_branch"],
                        private=repo_data["private"],
                        language=repo_data.get("language", ""),
                        stars=repo_data["stargazers_count"],
                        forks=repo_data["forks_count"],
                        created_at=datetime.fromisoformat(repo_data["created_at"].replace('Z', '+00:00')),
                        updated_at=datetime.fromisoformat(repo_data["updated_at"].replace('Z', '+00:00')),
                        topics=repo_data.get("topics", [])
                    )
                    repositories.append(repo)
                
                logger.info(f"✅ Found {len(repositories)} repositories")
                return repositories
            else:
                logger.error(f"Search failed: {response.status}")
                return []

class GitHubIntegration:
    """Complete GitHub integration with Git and GitHub API"""
    
    def __init__(self, github_token: str = None):
        self.git_manager = GitManager()
        self.github_manager = None
        self.github_token = github_token
        
        self.workflow_history: List[Dict[str, Any]] = []
    
    async def __aenter__(self):
        self.github_manager = GitHubManager(self.github_token)
        await self.github_manager.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.github_manager:
            await self.github_manager.__aexit__(exc_type, exc_val, exc_tb)
    
    async def create_project_with_github(self, 
                                       project_name: str,
                                       local_path: str,
                                       description: str = "",
                                       private: bool = False) -> Dict[str, Any]:
        """Create project locally and on GitHub"""
        
        logger.info(f"🚀 Creating project with GitHub: {project_name}")
        
        workflow = {
            "operation": "create_project_with_github",
            "project_name": project_name,
            "timestamp": datetime.now(),
            "steps": [],
            "status": "in_progress"
        }
        
        try:
            # Step 1: Create GitHub repository
            workflow["steps"].append("Creating GitHub repository")
            github_repo = await self.github_manager.create_repository(
                name=project_name,
                description=description,
                private=private,
                auto_init=True
            )
            
            # Step 2: Clone repository locally
            workflow["steps"].append("Cloning repository locally")
            local_repo = await self.git_manager.clone_repository(
                url=github_repo.clone_url,
                local_path=local_path
            )
            
            workflow["status"] = "completed"
            workflow["github_repo"] = github_repo
            workflow["local_repo"] = local_repo
            
            logger.info(f"✅ Project created successfully: {github_repo.full_name}")
            
        except Exception as e:
            workflow["status"] = "failed"
            workflow["error"] = str(e)
            logger.error(f"Project creation failed: {e}")
            raise
        
        finally:
            self.workflow_history.append(workflow)
        
        return workflow
    
    async def setup_development_workflow(self, 
                                       repo_path: str,
                                       feature_branch: str = "feature/development") -> Dict[str, Any]:
        """Setup development workflow with branch and initial commit"""
        
        logger.info(f"⚙️ Setting up development workflow: {feature_branch}")
        
        workflow = {
            "operation": "setup_development_workflow",
            "repo_path": repo_path,
            "timestamp": datetime.now(),
            "steps": [],
            "status": "in_progress"
        }
        
        try:
            # Step 1: Create feature branch
            workflow["steps"].append("Creating feature branch")
            await self.git_manager.create_branch(repo_path, feature_branch, checkout=True)
            
            # Step 2: Add development files (example)
            workflow["steps"].append("Adding development files")
            dev_files = {
                "src/__init__.py": "",
                "src/main.py": "#!/usr/bin/env python3\n\ndef main():\n    print('Hello, World!')\n\nif __name__ == '__main__':\n    main()\n",
                "tests/__init__.py": "",
                "tests/test_main.py": "import unittest\n\nclass TestMain(unittest.TestCase):\n    def test_main(self):\n        self.assertTrue(True)\n",
                "requirements.txt": "# Add dependencies here\n",
                ".gitignore": "*.pyc\n__pycache__/\n.env\n*.egg-info/\n"
            }
            
            repo_path_obj = Path(repo_path)
            for file_path, content in dev_files.items():
                full_path = repo_path_obj / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                with open(full_path, 'w') as f:
                    f.write(content)
            
            # Step 3: Commit changes
            workflow["steps"].append("Committing initial development setup")
            await self.git_manager.commit_changes(
                repo_path=repo_path,
                message="Initial development setup",
                add_all=True
            )
            
            # Step 4: Push to remote
            workflow["steps"].append("Pushing to remote")
            await self.git_manager.push_changes(repo_path, feature_branch)
            
            workflow["status"] = "completed"
            logger.info("✅ Development workflow setup completed")
            
        except Exception as e:
            workflow["status"] = "failed"
            workflow["error"] = str(e)
            logger.error(f"Development workflow setup failed: {e}")
            raise
        
        finally:
            self.workflow_history.append(workflow)
        
        return workflow
    
    async def automated_code_update_workflow(self, 
                                           repo_path: str,
                                           changes: Dict[str, str],
                                           commit_message: str,
                                           create_pr: bool = True) -> Dict[str, Any]:
        """Automated workflow for code updates with PR creation"""
        
        logger.info(f"🔄 Running automated code update workflow")
        
        workflow = {
            "operation": "automated_code_update",
            "repo_path": repo_path,
            "timestamp": datetime.now(),
            "steps": [],
            "status": "in_progress"
        }
        
        try:
            # Step 1: Get repository info
            repo_status = await self.git_manager.get_repository_status(repo_path)
            
            # Step 2: Create update branch
            update_branch = f"update/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            workflow["steps"].append(f"Creating update branch: {update_branch}")
            await self.git_manager.create_branch(repo_path, update_branch, checkout=True)
            
            # Step 3: Apply changes
            workflow["steps"].append("Applying code changes")
            repo_path_obj = Path(repo_path)
            modified_files = []
            
            for file_path, content in changes.items():
                full_path = repo_path_obj / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                with open(full_path, 'w') as f:
                    f.write(content)
                modified_files.append(file_path)
            
            # Step 4: Commit changes
            workflow["steps"].append("Committing changes")
            await self.git_manager.commit_changes(
                repo_path=repo_path,
                message=commit_message,
                files=modified_files
            )
            
            # Step 5: Push changes
            workflow["steps"].append("Pushing changes")
            await self.git_manager.push_changes(repo_path, update_branch)
            
            # Step 6: Create pull request (if requested)
            if create_pr and self.github_manager:
                workflow["steps"].append("Creating pull request")
                
                # Extract owner/repo from URL
                repo_url = repo_status.url
                if "github.com" in repo_url:
                    parts = repo_url.replace(".git", "").split("/")
                    owner = parts[-2]
                    repo_name = parts[-1]
                    
                    pr = await self.github_manager.create_pull_request(
                        owner=owner,
                        repo=repo_name,
                        title=f"Automated update: {commit_message}",
                        head=update_branch,
                        base=repo_status.branch,
                        description=f"Automated code update\n\nFiles modified:\n" + 
                                  "\n".join(f"- {f}" for f in modified_files)
                    )
                    
                    workflow["pull_request"] = pr
            
            workflow["status"] = "completed"
            workflow["modified_files"] = modified_files
            workflow["update_branch"] = update_branch
            
            logger.info("✅ Automated code update workflow completed")
            
        except Exception as e:
            workflow["status"] = "failed"
            workflow["error"] = str(e)
            logger.error(f"Automated code update workflow failed: {e}")
            raise
        
        finally:
            self.workflow_history.append(workflow)
        
        return workflow
    
    async def sync_repository(self, repo_path: str) -> Dict[str, Any]:
        """Sync repository with remote (pull latest changes)"""
        
        logger.info(f"🔄 Syncing repository: {repo_path}")
        
        workflow = {
            "operation": "sync_repository",
            "repo_path": repo_path,
            "timestamp": datetime.now(),
            "status": "in_progress"
        }
        
        try:
            # Get current status
            before_status = await self.git_manager.get_repository_status(repo_path)
            
            # Pull latest changes
            success = await self.git_manager.pull_changes(repo_path)
            
            if success:
                # Get updated status
                after_status = await self.git_manager.get_repository_status(repo_path)
                
                workflow["status"] = "completed"
                workflow["before_status"] = before_status
                workflow["after_status"] = after_status
                workflow["changes_pulled"] = after_status.behind_commits != before_status.behind_commits
                
                logger.info("✅ Repository synced successfully")
            else:
                workflow["status"] = "failed"
                workflow["error"] = "Pull operation failed"
        
        except Exception as e:
            workflow["status"] = "failed"
            workflow["error"] = str(e)
            logger.error(f"Repository sync failed: {e}")
        
        finally:
            self.workflow_history.append(workflow)
        
        return workflow
    
    def get_workflow_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent workflow history"""
        
        return self.workflow_history[-limit:]

async def main():
    """Demo GitHub integration"""
    
    print("🐙 GitHub Integration Demo")
    print("=" * 50)
    
    async with GitHubIntegration() as github_integration:
        
        # Demo 1: Search repositories
        print("\n1. Searching repositories...")
        repos = await github_integration.github_manager.search_repositories(
            query="python machine learning",
            language="python",
            limit=5
        )
        
        print(f"Found {len(repos)} repositories:")
        for repo in repos[:3]:
            print(f"  • {repo.full_name} ({repo.stars} ⭐) - {repo.description[:50]}...")
        
        # Demo 2: Local git operations
        print("\n2. Local Git operations...")
        
        # Initialize a test repository
        test_repo_path = "./test_git_repo"
        if not Path(test_repo_path).exists():
            repo = await github_integration.git_manager.init_repository(test_repo_path)
            print(f"Initialized repository: {repo.name}")
            
            # Add a test file
            test_file = Path(test_repo_path) / "README.md"
            with open(test_file, 'w') as f:
                f.write("# Test Repository\n\nThis is a test.")
            
            # Commit the file
            await github_integration.git_manager.commit_changes(
                repo_path=test_repo_path,
                message="Add README",
                add_all=True
            )
            print("Added and committed README.md")
        
        # Get repository status
        status = await github_integration.git_manager.get_repository_status(test_repo_path)
        print(f"Repository status: Clean={status.is_clean}, Branch={status.branch}")
        
        # Demo 3: Show workflow history
        print("\n3. Workflow history:")
        history = github_integration.get_workflow_history()
        for workflow in history:
            print(f"  • {workflow['operation']} - {workflow['status']}")

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Secure Configuration Management
Proper handling of sensitive credentials and configuration
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecureConfig:
    """Secure configuration manager for sensitive data"""
    
    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir or Path.home() / ".ideation_assistant")
        self.config_dir.mkdir(exist_ok=True, mode=0o700)  # Restricted permissions
        
        self.config_file = self.config_dir / "config.json"
        self.env_file = self.config_dir / ".env"
        
        self._config_cache = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment"""
        
        # Load from config file
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                self._config_cache.update(file_config)
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
        
        # Load from environment variables
        env_config = {
            "github_username": os.getenv("GITHUB_USERNAME"),
            "github_token": os.getenv("GITHUB_TOKEN"), 
            "deepseek_api_key": os.getenv("DEEPSEEK_API_KEY"),
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "brave_api_key": os.getenv("BRAVE_API_KEY"),
        }
        
        # Only update if environment variables are set
        for key, value in env_config.items():
            if value:
                self._config_cache[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config_cache.get(key, default)
    
    def set(self, key: str, value: Any, persist: bool = True):
        """Set configuration value"""
        self._config_cache[key] = value
        
        if persist:
            self._save_config()
    
    def _save_config(self):
        """Save non-sensitive configuration to file"""
        
        # Only save non-sensitive configuration
        safe_config = {
            key: value for key, value in self._config_cache.items()
            if not self._is_sensitive(key)
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(safe_config, f, indent=2)
            logger.info("Configuration saved")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def _is_sensitive(self, key: str) -> bool:
        """Check if a key contains sensitive data"""
        sensitive_keywords = [
            'token', 'key', 'password', 'secret', 'credential',
            'api_key', 'access_token', 'private_key'
        ]
        return any(keyword in key.lower() for keyword in sensitive_keywords)
    
    def setup_github_credentials(self):
        """Interactive setup for GitHub credentials"""
        
        print("\n🔐 GitHub Credentials Setup")
        print("=" * 40)
        print("IMPORTANT: Never store tokens in code!")
        print("This will guide you to set environment variables safely.")
        print()
        
        current_username = self.get("github_username")
        current_token = self.get("github_token")
        
        if current_username and current_token:
            print(f"✅ GitHub credentials already configured for: {current_username}")
            print("Token: ********** (hidden)")
            return
        
        print("To set up GitHub credentials securely:")
        print()
        print("1. Set environment variables in your shell:")
        print("   export GITHUB_USERNAME='your_username'")
        print("   export GITHUB_TOKEN='your_personal_access_token'")
        print()
        print("2. Or add them to your shell profile (.bashrc, .zshrc, etc.):")
        print("   echo 'export GITHUB_USERNAME=\"your_username\"' >> ~/.bashrc")
        print("   echo 'export GITHUB_TOKEN=\"your_token\"' >> ~/.bashrc")
        print()
        print("3. Create a GitHub Personal Access Token at:")
        print("   https://github.com/settings/tokens")
        print("   Required scopes: repo, user, write:packages")
        print()
        print("4. Restart your terminal or run: source ~/.bashrc")
        print()
        
        # Check for any environment variables that might be set
        if os.getenv("GITHUB_USERNAME"):
            print(f"✅ Found GITHUB_USERNAME: {os.getenv('GITHUB_USERNAME')}")
        else:
            print("❌ GITHUB_USERNAME not found in environment")
        
        if os.getenv("GITHUB_TOKEN"):
            print("✅ Found GITHUB_TOKEN: **********")
        else:
            print("❌ GITHUB_TOKEN not found in environment")
    
    def setup_api_keys(self):
        """Interactive setup for API keys"""
        
        print("\n🔑 API Keys Setup")
        print("=" * 30)
        print("Configure your API keys as environment variables:")
        print()
        
        api_configs = [
            {
                "name": "DeepSeek API",
                "env_var": "DEEPSEEK_API_KEY",
                "description": "For DeepSeek AI reasoning capabilities",
                "url": "https://platform.deepseek.com"
            },
            {
                "name": "OpenAI API",
                "env_var": "OPENAI_API_KEY", 
                "description": "For OpenAI GPT models (optional)",
                "url": "https://platform.openai.com/api-keys"
            },
            {
                "name": "Brave Search API",
                "env_var": "BRAVE_API_KEY",
                "description": "For web search capabilities",
                "url": "https://api.search.brave.com"
            }
        ]
        
        for api in api_configs:
            current_key = self.get(api["env_var"].lower())
            status = "✅ Configured" if current_key else "❌ Not configured"
            
            print(f"{api['name']}: {status}")
            print(f"   Environment variable: {api['env_var']}")
            print(f"   Description: {api['description']}")
            print(f"   Get API key: {api['url']}")
            print()
    
    def validate_configuration(self) -> Dict[str, bool]:
        """Validate current configuration"""
        
        validations = {
            "github_username": bool(self.get("github_username")),
            "github_token": bool(self.get("github_token")),
            "deepseek_api_key": bool(self.get("deepseek_api_key")),
        }
        
        return validations
    
    def create_env_template(self):
        """Create a template .env file"""
        
        template = """# Ideation Assistant Environment Variables
# Copy this to your shell profile (.bashrc, .zshrc, etc.) and fill in your values

# GitHub Configuration
export GITHUB_USERNAME="your_github_username"
export GITHUB_TOKEN="your_github_personal_access_token"

# AI API Keys
export DEEPSEEK_API_KEY="your_deepseek_api_key"
export OPENAI_API_KEY="your_openai_api_key"  # Optional

# Search API Keys
export BRAVE_API_KEY="your_brave_search_api_key"  # Optional

# MCP Configuration
export MCP_CONFIG_DIR="./mcp_config"

# Workspace Configuration
export IDEATION_WORKSPACE="./workspace"
"""
        
        template_file = self.config_dir / "env_template.txt"
        
        with open(template_file, 'w') as f:
            f.write(template)
        
        print(f"📝 Environment template created: {template_file}")
        print("Copy the contents to your shell profile and fill in your values.")
    
    def check_security(self) -> Dict[str, Any]:
        """Check for security issues in configuration"""
        
        issues = []
        warnings = []
        
        # Check for sensitive data in config file
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_content = f.read()
                
                if any(keyword in config_content.lower() for keyword in ['token', 'password', 'secret']):
                    issues.append("Potential sensitive data found in config file")
            except:
                pass
        
        # Check file permissions
        if self.config_file.exists():
            file_mode = oct(self.config_file.stat().st_mode)[-3:]
            if file_mode != '600':
                warnings.append(f"Config file permissions are {file_mode}, should be 600")
        
        # Check environment setup
        missing_env = []
        for key in ['GITHUB_USERNAME', 'GITHUB_TOKEN']:
            if not os.getenv(key):
                missing_env.append(key)
        
        if missing_env:
            warnings.append(f"Missing environment variables: {', '.join(missing_env)}")
        
        return {
            "issues": issues,
            "warnings": warnings,
            "secure": len(issues) == 0
        }

# Global configuration instance
config = SecureConfig()

def get_github_credentials() -> tuple[str, str]:
    """Get GitHub credentials safely"""
    username = config.get("github_username")
    token = config.get("github_token")
    
    if not username or not token:
        logger.warning("GitHub credentials not configured")
        return None, None
    
    return username, token

def get_api_key(service: str) -> Optional[str]:
    """Get API key for a service"""
    key_mapping = {
        "deepseek": "deepseek_api_key",
        "openai": "openai_api_key",
        "brave": "brave_api_key"
    }
    
    key_name = key_mapping.get(service.lower())
    if not key_name:
        return None
    
    return config.get(key_name)

async def main():
    """Demo secure configuration"""
    
    print("🔐 Secure Configuration Demo")
    print("=" * 50)
    
    # Initialize configuration
    secure_config = SecureConfig()
    
    # Setup GitHub credentials
    secure_config.setup_github_credentials()
    
    # Setup API keys
    secure_config.setup_api_keys()
    
    # Create environment template
    secure_config.create_env_template()
    
    # Validate configuration
    print("\n🔍 Configuration Validation:")
    validations = secure_config.validate_configuration()
    for key, valid in validations.items():
        status = "✅ Valid" if valid else "❌ Missing"
        print(f"   {key}: {status}")
    
    # Security check
    print("\n🛡️ Security Check:")
    security = secure_config.check_security()
    
    if security["secure"]:
        print("   ✅ Configuration is secure")
    else:
        print("   ⚠️ Security issues found:")
        for issue in security["issues"]:
            print(f"     • {issue}")
    
    if security["warnings"]:
        print("   Warnings:")
        for warning in security["warnings"]:
            print(f"     • {warning}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
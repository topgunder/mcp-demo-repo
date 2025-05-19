import os
import json
import subprocess
import time
import select
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def read_with_timeout(process: subprocess.Popen, timeout: int = 5) -> Optional[str]:
    """Read process output with timeout"""
    ready, _, _ = select.select([process.stdout], [], [], timeout)
    if ready:
        return process.stdout.readline()
    return None

def send_command(process: subprocess.Popen, command: Dict[str, Any], timeout: int = 5) -> Optional[Dict[str, Any]]:
    """Send a command to the MCP Server and get the response"""
    process.stdin.write(json.dumps(command) + "\n")
    process.stdin.flush()
    
    response = read_with_timeout(process, timeout)
    if not response:
        return None
    
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return None

def test_repository_operations(process: subprocess.Popen) -> None:
    """Test various repository operations"""
    user = os.getenv('GITHUB_USERNAME')
    if not user:
        print("❌ Set GITHUB_USERNAME in .env to test repository operations.")
        return

    # Test creating a repository with different settings
    test_repos = [
        {"name": "mcp-test-public", "private": False},
        {"name": "mcp-test-private", "private": True},
        {"name": "mcp-test-with-desc", "private": False, "description": "Test repository with description"}
    ]

    for repo in test_repos:
        print(f"\n🚀 Testing repository creation: {repo['name']}...")
        command = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "create_repository",
                "arguments": {
                    "name": repo["name"],
                    "private": repo.get("private", False),
                    "description": repo.get("description", ""),
                    "autoInit": True
                }
            }
        }
        
        response = send_command(process, command)
        if response and "error" not in response:
            print(f"✅ Repository {repo['name']} created successfully")
        else:
            print(f"❌ Failed to create repository {repo['name']}")

def test_branch_operations(process: subprocess.Popen) -> None:
    """Test various branch operations"""
    user = os.getenv('GITHUB_USERNAME')
    if not user:
        print("❌ Set GITHUB_USERNAME in .env to test branch operations.")
        return

    repo_name = "mcp-test-public"
    test_branches = [
        "feature/test-1",
        "bugfix/test-2",
        "hotfix/test-3"
    ]

    for branch in test_branches:
        print(f"\n🌿 Testing branch creation: {branch}...")
        command = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "create_branch",
                "arguments": {
                    "owner": user,
                    "repo": repo_name,
                    "branch": branch,
                    "base": "main"
                }
            }
        }
        
        response = send_command(process, command)
        if response and "error" not in response:
            print(f"✅ Branch {branch} created successfully")
        else:
            print(f"❌ Failed to create branch {branch}")

def test_file_operations(process: subprocess.Popen) -> None:
    """Test various file operations"""
    user = os.getenv('GITHUB_USERNAME')
    if not user:
        print("❌ Set GITHUB_USERNAME in .env to test file operations.")
        return

    repo_name = "mcp-test-public"
    branch_name = "feature/test-1"
    
    # Test creating different types of files
    test_files = [
        {
            "path": "docs/README.md",
            "content": "# Documentation\n\nThis is a test documentation file.",
            "message": "Add documentation"
        },
        {
            "path": "src/main.py",
            "content": "def main():\n    print('Hello, MCP!')\n\nif __name__ == '__main__':\n    main()",
            "message": "Add main script"
        },
        {
            "path": "tests/test_main.py",
            "content": "def test_main():\n    assert True  # Placeholder test\n",
            "message": "Add test file"
        }
    ]

    for file in test_files:
        print(f"\n📝 Testing file creation: {file['path']}...")
        command = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "create_or_update_file",
                "arguments": {
                    "owner": user,
                    "repo": repo_name,
                    "path": file["path"],
                    "message": file["message"],
                    "content": file["content"],
                    "branch": branch_name
                }
            }
        }
        
        response = send_command(process, command)
        if response and "error" not in response:
            print(f"✅ File {file['path']} created successfully")
        else:
            print(f"❌ Failed to create file {file['path']}")

def test_pull_request_operations(process: subprocess.Popen) -> None:
    """Test various pull request operations"""
    user = os.getenv('GITHUB_USERNAME')
    if not user:
        print("❌ Set GITHUB_USERNAME in .env to test PR operations.")
        return

    repo_name = "mcp-test-public"
    test_prs = [
        {
            "title": "Feature: Add documentation",
            "body": "This PR adds initial documentation to the project.",
            "head": "feature/test-1",
            "base": "main"
        },
        {
            "title": "Bugfix: Fix main script",
            "body": "This PR fixes issues in the main script.",
            "head": "bugfix/test-2",
            "base": "main"
        }
    ]

    for pr in test_prs:
        print(f"\n🔀 Testing PR creation: {pr['title']}...")
        command = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "create_pull_request",
                "arguments": {
                    "owner": user,
                    "repo": repo_name,
                    "title": pr["title"],
                    "body": pr["body"],
                    "head": pr["head"],
                    "base": pr["base"]
                }
            }
        }
        
        response = send_command(process, command)
        if response and "error" not in response:
            if "result" in response and "content" in response["result"]:
                pr_data = json.loads(response["result"]["content"][0]["text"])
                pr_url = pr_data.get("html_url", "URL not available")
                print(f"✅ PR created successfully: {pr_url}")
            else:
                print(f"✅ PR created successfully")
        else:
            print(f"❌ Failed to create PR: {pr['title']}")

def test_mcp_server() -> None:
    """Test MCP Server with various operations"""
    # Get token from environment
    token = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
    if not token:
        raise ValueError("GITHUB_PERSONAL_ACCESS_TOKEN not defined in .env file")

    # Prepare command to start MCP Server
    cmd = [
        "docker", "run", "--rm", "-i",
        "-e", f"GITHUB_PERSONAL_ACCESS_TOKEN={token}",
        "-w", "/server",
        "ghcr.io/github/github-mcp-server:latest",
        "./github-mcp-server", "stdio",
        "--enable-command-logging",
        "--dynamic-toolsets"
    ]

    print("🚀 Starting MCP Server...")
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    time.sleep(1)

    try:
        if process.poll() is not None:
            print("❌ Error: Server did not start")
            return

        # Enable required toolsets
        toolsets = ["repos", "pull_requests"]
        for toolset in toolsets:
            print(f"\n📦 Enabling {toolset} toolset...")
            command = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "enable_toolset",
                    "arguments": {
                        "toolset": toolset
                    }
                }
            }
            
            response = send_command(process, command)
            if response and "error" not in response:
                print(f"✅ {toolset} toolset enabled successfully")
            else:
                print(f"❌ Failed to enable {toolset} toolset")
                return

        # Run all test operations
        test_repository_operations(process)
        test_branch_operations(process)
        test_file_operations(process)
        test_pull_request_operations(process)

    finally:
        print("\n🛑 Shutting down server...")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_mcp_server() 
# GitHub MCP Server Guide

This guide provides detailed information about using the GitHub Model Context Protocol (MCP) Server for automating GitHub operations.

## Table of Contents

1. [Introduction](#introduction)
2. [Setup](#setup)
3. [Basic Operations](#basic-operations)
4. [Advanced Operations](#advanced-operations)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Introduction

The GitHub MCP Server is a powerful tool that allows you to automate GitHub operations through a simple JSON-RPC interface. It provides a way to interact with GitHub's API in a structured and efficient manner.

### Key Features

- Repository management
- Branch operations
- File operations
- Pull request management
- Dynamic toolsets
- Command logging

## Setup

### Prerequisites

- Python 3.13+
- Docker
- GitHub account
- GitHub Personal Access Token

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd github-mcp-official/python
   ```

2. Create and activate a virtual environment:
   ```bash
   python3.13 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file:
   ```
   GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here
   GITHUB_USERNAME=your_username
   ```

### Token Configuration

Your GitHub Personal Access Token needs the following permissions:
- `repo` (Full control of private repositories)
- `workflow` (Update GitHub Action workflows)

## Basic Operations

### Starting the Server

```python
import subprocess

cmd = [
    "docker", "run", "--rm", "-i",
    "-e", f"GITHUB_PERSONAL_ACCESS_TOKEN={token}",
    "-w", "/server",
    "ghcr.io/github/github-mcp-server:latest",
    "./github-mcp-server", "stdio",
    "--enable-command-logging",
    "--dynamic-toolsets"
]

process = subprocess.Popen(
    cmd,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)
```

### Enabling Toolsets

```python
command = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "enable_toolset",
        "arguments": {
            "toolset": "repos"
        }
    }
}
```

### Creating a Repository

```python
command = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "create_repository",
        "arguments": {
            "name": "my-repo",
            "private": False,
            "description": "My test repository"
        }
    }
}
```

## Advanced Operations

### Repository Management

#### Creating Multiple Repositories

```python
test_repos = [
    {"name": "repo1", "private": False},
    {"name": "repo2", "private": True},
    {"name": "repo3", "private": False, "description": "Test repo"}
]

for repo in test_repos:
    command = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "create_repository",
            "arguments": {
                "name": repo["name"],
                "private": repo.get("private", False),
                "description": repo.get("description", "")
            }
        }
    }
```

### Branch Operations

#### Creating Multiple Branches

```python
test_branches = [
    "feature/new-feature",
    "bugfix/fix-issue",
    "hotfix/critical-fix"
]

for branch in test_branches:
    command = {
        "jsonrpc": "2.0",
        "id": 1,
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
```

### File Operations

#### Creating Multiple Files

```python
test_files = [
    {
        "path": "docs/README.md",
        "content": "# Documentation",
        "message": "Add documentation"
    },
    {
        "path": "src/main.py",
        "content": "def main():\n    pass",
        "message": "Add main script"
    }
]

for file in test_files:
    command = {
        "jsonrpc": "2.0",
        "id": 1,
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
```

### Pull Request Operations

#### Creating Multiple PRs

```python
test_prs = [
    {
        "title": "Feature: Add documentation",
        "body": "This PR adds initial documentation.",
        "head": "feature/docs",
        "base": "main"
    },
    {
        "title": "Bugfix: Fix main script",
        "body": "This PR fixes issues in the main script.",
        "head": "bugfix/main",
        "base": "main"
    }
]

for pr in test_prs:
    command = {
        "jsonrpc": "2.0",
        "id": 1,
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
```

## Best Practices

1. **Error Handling**
   - Always check for errors in responses
   - Implement proper timeout handling
   - Log errors for debugging

2. **Resource Management**
   - Clean up resources properly
   - Use context managers when possible
   - Handle process termination gracefully

3. **Code Organization**
   - Separate concerns into different functions
   - Use type hints for better code clarity
   - Document functions and their parameters

4. **Testing**
   - Write comprehensive tests
   - Test different scenarios
   - Handle edge cases

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify token permissions
   - Check token expiration
   - Ensure correct environment variables

2. **Connection Issues**
   - Check Docker status
   - Verify internet connection
   - Check GitHub API status

3. **Timeout Issues**
   - Increase timeout values
   - Check network latency
   - Verify server response times

### Debugging Tips

1. Enable command logging:
   ```bash
   ./github-mcp-server stdio --enable-command-logging
   ```

2. Check response format:
   ```python
   print(json.dumps(response, indent=2))
   ```

3. Monitor process status:
   ```python
   if process.poll() is not None:
       print("Process terminated unexpectedly")
   ```

## Examples

See the following files for complete examples:
- `test_mcp.py`: Basic MCP Server operations
- `test_mcp_advanced.py`: Advanced operations and testing

## Support

For more information:
- [GitHub MCP Documentation](https://docs.github.com/en/enterprise/mcp)
- [API Reference](https://docs.github.com/en/enterprise/mcp/api-reference)
- [GitHub Issues](https://github.com/github/mcp-server/issues) 
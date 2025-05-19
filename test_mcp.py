import os
import json
import subprocess
import time
import select
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def read_with_timeout(process: subprocess.Popen, timeout: int = 5) -> Optional[str]:
    """Read process output with timeout"""
    ready, _, _ = select.select([process.stdout], [], [], timeout)
    if ready:
        return process.stdout.readline()
    return None

def list_available_commands(process: subprocess.Popen) -> Optional[list]:
    """List available commands in MCP Server"""
    print("\n📋 Listing available commands...")
    command = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    process.stdin.write(json.dumps(command) + "\n")
    process.stdin.flush()
    
    response = read_with_timeout(process)
    if response:
        try:
            response_data = json.loads(response)
            if "result" in response_data and "tools" in response_data["result"]:
                tools = response_data["result"]["tools"]
                print("\n🔧 Available tools:")
                for tool in tools:
                    print(f"- {tool['name']}: {tool.get('description', 'No description')}")
                return tools
            else:
                print("❌ Unexpected response format when listing commands")
                print(f"Response received: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError as e:
            print(f"❌ Error processing response: {str(e)}")
            print(f"Response received: {response}")
    else:
        print("❌ Timeout while listing commands")
    return None

def list_available_toolsets(process: subprocess.Popen) -> None:
    """List available toolsets in MCP Server"""
    print("\n📦 Listing available toolsets...")
    command = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "list_available_toolsets",
            "arguments": {}
        }
    }
    process.stdin.write(json.dumps(command) + "\n")
    process.stdin.flush()
    
    response = read_with_timeout(process)
    if response:
        try:
            response_data = json.loads(response)
            if "result" in response_data and "content" in response_data["result"]:
                content = response_data["result"]["content"][0]["text"]
                toolsets = json.loads(content)
                print("\n🔧 Available toolsets:")
                for toolset in toolsets:
                    print(f"\n- {toolset['name']}: {toolset.get('description', 'No description')}")
                    print(f"  Status: {'Enabled' if toolset.get('enabled', False) else 'Disabled'}")
                    
                    # Get tools for this toolset
                    get_tools_command = {
                        "jsonrpc": "2.0",
                        "id": 5,
                        "method": "tools/call",
                        "params": {
                            "name": "get_toolset_tools",
                            "arguments": {
                                "toolset": toolset['name']
                            }
                        }
                    }
                    process.stdin.write(json.dumps(get_tools_command) + "\n")
                    process.stdin.flush()
                    
                    tools_response = read_with_timeout(process)
                    if tools_response:
                        try:
                            tools_data = json.loads(tools_response)
                            if "result" in tools_data and "content" in tools_data["result"]:
                                tools_content = tools_data["result"]["content"][0]["text"]
                                tools = json.loads(tools_content)
                                print("  Tools:")
                                for tool in tools:
                                    print(f"    - {tool['name']}: {tool.get('description', 'No description')}")
                        except json.JSONDecodeError:
                            print("    ❌ Error processing toolset tools")
            else:
                print("❌ Unexpected response format when listing toolsets")
                print(f"Response received: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError as e:
            print(f"❌ Error processing response: {str(e)}")
            print(f"Response received: {response}")
    else:
        print("❌ Timeout while listing toolsets")

def test_full_repository_flow(process: subprocess.Popen, repo_name: str = "mcp-demo-repo") -> None:
    """Complete flow: create repo, initial commit, branch, file and PR"""
    user = os.getenv('GITHUB_USERNAME')
    if not user:
        print("❌ Set GITHUB_USERNAME in .env to create the repository.")
        return
    full_repo = f"{user}/{repo_name}"
    print(f"\n🚀 Creating repository {full_repo}...")
    
    # 1. Create repository
    command = {
        "jsonrpc": "2.0",
        "id": 10,
        "method": "tools/call",
        "params": {
            "name": "create_repository",
            "arguments": {
                "name": repo_name,
                "private": False,
                "autoInit": False
            }
        }
    }
    process.stdin.write(json.dumps(command) + "\n")
    process.stdin.flush()
    response = read_with_timeout(process, timeout=10)
    if not response:
        print("❌ Timeout while creating repository")
        return
    try:
        response_data = json.loads(response)
        if "error" in response_data:
            print(f"❌ Error creating repository: {response_data['error']}")
            return
        print("✅ Repository created successfully")
    except json.JSONDecodeError as e:
        print(f"❌ Error processing response: {str(e)}")
        return
    time.sleep(2)

    # 2. Initial commit in main
    print("\n📝 Creating initial commit in main branch...")
    file_content = """# MCP Demo Repository\n\nThis repository was automatically created to test the complete MCP Server flow.\n"""
    command = {
        "jsonrpc": "2.0",
        "id": 11,
        "method": "tools/call",
        "params": {
            "name": "create_or_update_file",
            "arguments": {
                "owner": user,
                "repo": repo_name,
                "path": "README.md",
                "message": "Initial commit via MCP Server",
                "content": file_content,
                "branch": "main"
            }
        }
    }
    process.stdin.write(json.dumps(command) + "\n")
    process.stdin.flush()
    response = read_with_timeout(process)
    if not response:
        print("❌ Timeout while creating initial file")
        return
    try:
        response_data = json.loads(response)
        if "error" in response_data:
            print(f"❌ Error creating initial file: {response_data['error']}")
            return
        print("✅ Initial commit created successfully")
    except json.JSONDecodeError as e:
        print(f"❌ Error processing response: {str(e)}")
        return
    time.sleep(2)

    # 3. Create a new branch
    branch_name = "feature/test-mcp"
    print(f"\n🌿 Creating branch {branch_name}...")
    command = {
        "jsonrpc": "2.0",
        "id": 12,
        "method": "tools/call",
        "params": {
            "name": "create_branch",
            "arguments": {
                "owner": user,
                "repo": repo_name,
                "branch": branch_name,
                "base": "main"
            }
        }
    }
    process.stdin.write(json.dumps(command) + "\n")
    process.stdin.flush()
    response = read_with_timeout(process)
    if not response:
        print("❌ Timeout while creating branch")
        return
    try:
        response_data = json.loads(response)
        if "error" in response_data:
            print(f"❌ Error creating branch: {response_data['error']}")
            return
        print("✅ Branch created successfully")
    except json.JSONDecodeError as e:
        print(f"❌ Error processing response: {str(e)}")
        return
    time.sleep(2)

    # 4. Create a file in the feature branch
    print("\n📝 Creating test file in feature branch...")
    file_content = """# MCP Server Test\n\nFile automatically created in the feature branch.\n"""
    command = {
        "jsonrpc": "2.0",
        "id": 13,
        "method": "tools/call",
        "params": {
            "name": "create_or_update_file",
            "arguments": {
                "owner": user,
                "repo": repo_name,
                "path": "test-mcp.md",
                "message": "Add test file via MCP Server",
                "content": file_content,
                "branch": branch_name
            }
        }
    }
    process.stdin.write(json.dumps(command) + "\n")
    process.stdin.flush()
    response = read_with_timeout(process)
    if not response:
        print("❌ Timeout while creating test file")
        return
    try:
        response_data = json.loads(response)
        if "error" in response_data:
            print(f"❌ Error creating test file: {response_data['error']}")
            return
        print("✅ Test file created successfully")
    except json.JSONDecodeError as e:
        print(f"❌ Error processing response: {str(e)}")
        return
    time.sleep(2)

    # 5. Create a PR
    print("\n🔀 Creating Pull Request...")
    command = {
        "jsonrpc": "2.0",
        "id": 14,
        "method": "tools/call",
        "params": {
            "name": "create_pull_request",
            "arguments": {
                "owner": user,
                "repo": repo_name,
                "title": "MCP Server Test",
                "body": "This PR was automatically created to test the complete MCP Server flow.",
                "head": branch_name,
                "base": "main"
            }
        }
    }
    process.stdin.write(json.dumps(command) + "\n")
    process.stdin.flush()
    response = read_with_timeout(process)
    if not response:
        print("❌ Timeout while creating PR")
        return
    try:
        response_data = json.loads(response)
        if "error" in response_data:
            print(f"❌ Error creating PR: {response_data['error']}")
            return
        if "result" in response_data and "content" in response_data["result"]:
            pr_data = json.loads(response_data["result"]["content"][0]["text"])
            pr_url = pr_data.get("html_url", "URL not available")
            print(f"✅ PR created successfully: {pr_url}")
        else:
            print("✅ PR created successfully")
    except json.JSONDecodeError as e:
        print(f"❌ Error processing response: {str(e)}")
        return

def test_mcp_command() -> None:
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

        # Enable repos toolset
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
        process.stdin.write(json.dumps(command) + "\n")
        process.stdin.flush()
        
        response = read_with_timeout(process)
        if not response:
            print("❌ Timeout while enabling repos toolset")
            return

        # Enable pull_requests toolset
        command = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "enable_toolset",
                "arguments": {
                    "toolset": "pull_requests"
                }
            }
        }
        process.stdin.write(json.dumps(command) + "\n")
        process.stdin.flush()
        
        response = read_with_timeout(process)
        if not response:
            print("❌ Timeout while enabling pull_requests toolset")
            return

        # Execute complete flow
        test_full_repository_flow(process)

    finally:
        print("\n🛑 Shutting down server...")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_mcp_command() 
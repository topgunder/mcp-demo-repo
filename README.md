# GitHub MCP Official Demo

This project demonstrates how to use GitHub's official Model Context Protocol (MCP) to manage AI model context.

## Requirements

- Python 3.7+
- GitHub Access
- GitHub Personal Access Token with MCP permissions
- Docker

## Step-by-Step Setup

1. Clone the repository:
   ```bash
   git clone <your-repository>
   cd github-mcp-official/python
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root:
   ```
   # GitHub Configuration
   GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here
   GITHUB_USERNAME=your_username
   ```

   To get the token:
   1. Go to GitHub
   2. Navigate to Settings > Developer settings > Personal access tokens
   3. Generate a new token with the following permissions:
      - `repo` (Full control of private repositories)
      - `workflow` (Update GitHub Action workflows)

5. Run the test script:
   ```bash
   python test_mcp.py
   ```

## Testing the MCP Server

The script will:
1. Start the MCP Server using Docker
2. Create a new repository
3. Make an initial commit
4. Create a feature branch
5. Add a test file
6. Create a pull request

### Example Output
```
🚀 Starting MCP Server...
🚀 Creating repository username/mcp-demo-repo...
✅ Repository created successfully
📝 Creating initial commit in main branch...
✅ Initial commit created successfully
🌿 Creating branch feature/test-mcp...
✅ Branch created successfully
📝 Creating test file in feature branch...
✅ Test file created successfully
🔀 Creating Pull Request...
✅ PR created successfully: https://github.com/username/mcp-demo-repo/pull/1
```

## Project Structure

```
python/
├── test_mcp.py          # Main test script for MCP Server operations
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Docker configuration for MCP Server
└── README.md          # This file
```

## Troubleshooting

1. Authentication Error:
   - Verify your token in the `.env` file
   - Confirm the token has the required permissions

2. Connection Error:
   - Check if Docker is running
   - Verify your internet connection

3. Dependency Error:
   - Try reinstalling dependencies: `pip install -r requirements.txt --force-reinstall`

## Support

For more information about GitHub MCP, see:
- [GitHub MCP Documentation](https://docs.github.com/en/enterprise/mcp)
- [API Reference](https://docs.github.com/en/enterprise/mcp/api-reference) 
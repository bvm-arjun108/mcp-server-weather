# Running Local MCP Servers in Claude Desktop

Claude Desktop serves as a good testing ground for your custom MCP servers. Installing local MCP servers in Claude Desktop is done the same way published MCP servers are installed. The main difference is in the args property.

To add your own variant of the open-meteo-weather server or the one provided in the exercise files repository for this course to Claude Desktop, add a new weather object to the mcpServers object in claude_desktop_config.json like this:

```json
{
  "mcpServers": {
    "weather": {
      "command": "/Users/your-username/.local/bin/uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "/Users/your-username/path/to/open-meteo-weather/server.py"
      ]
    }
  }
}
```

## Different ways of spinning up MCP servers

Note the args property in the open-meteo-weather server is far more complex than the ones you added for fetch and filesystem earlier. This is because Claude Desktop needs to know how to spin up the local server in its virtual environment. args holds an array of commands to run the open-meteo-weather MCP server in a virtual environment:

```
uv run --with mcp[cli] mcp run /Users/your-username/path/to/open-meteo-weather/server.py
```

Here's a breakdown of this command:

- `uv run` starts up uv
- `--with mcp[cli]` adds the mcp[cli] dependency to uv
- `mcp run <path-to-file>` uses the mcp cli to run the specified file

This allows Claude Desktop to spin up the server in its own virtual environment without your involvement. And yes, that means the LLM is running software inside itself!

For a broad range of examples of how to implement and run MCP servers using Python and TypeScript, explore the reference servers provided in the modelcontextprotocol/servers GitHub repository.

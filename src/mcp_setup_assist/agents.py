# Copyright (c) 2026 Christian Ekiza

"""Generic agent configuration: MCP server registration for supported IDEs."""
import json
import shutil
from pathlib import Path

MCP_SERVER_CONFIG = {
    "mcpServers": {
        "codebase-memory": {
            "command": "codebase-memory-mcp",
            "args": [],
            "disabled": False
        }
    }
}

AGENT_CONFIGS = {
    "amazonq": {
        "mcp_dir": ".amazonq",
        "mcp_file": "mcp.json",
        "rules_dir": ".amazonq/rules",
    },
    "claude": {
        "mcp_dir": ".claude",
        "mcp_file": "settings.json",
        "rules_dir": ".claude",
    },
    "cursor": {
        "mcp_dir": ".cursor",
        "mcp_file": "mcp.json",
        "rules_dir": ".cursor/rules",
    },
}


def run_init(agents: list[str], rules_file: Path, cbmignore_file: Path):
    """Set up MCP server config, agent rules, and .cbmignore for a project."""
    project_root = Path.cwd()

    for agent in agents:
        write_mcp_config(project_root, agent)
        write_rules(project_root, agent, rules_file)
        print(f"[OK] {agent} configured")

    write_cbmignore(project_root, cbmignore_file)
    print("[OK] .cbmignore created")
    print("\nDone. Restart your IDE to activate the MCP server.")


def write_mcp_config(project_root: Path, agent: str):
    config = AGENT_CONFIGS[agent]
    mcp_dir = project_root / config["mcp_dir"]
    mcp_dir.mkdir(parents=True, exist_ok=True)
    mcp_file = mcp_dir / config["mcp_file"]

    if agent == "claude" and mcp_file.exists():
        existing = json.loads(mcp_file.read_text())
        existing.setdefault("mcpServers", {}).update(MCP_SERVER_CONFIG["mcpServers"])
        mcp_file.write_text(json.dumps(existing, indent=2) + "\n")
    else:
        mcp_file.write_text(json.dumps(MCP_SERVER_CONFIG, indent=2) + "\n")

def write_rules(project_root: Path, agent: str, rules_file: Path):
    config = AGENT_CONFIGS[agent]
    rules_dir = project_root / config["rules_dir"]
    rules_dir.mkdir(parents=True, exist_ok=True)
    dst = rules_dir / rules_file.name
    shutil.copy2(rules_file, dst)

    if agent == "claude":
        claude_md = project_root / "CLAUDE.md"
        import_line = f"@.claude/{rules_file.name}\n"
        if claude_md.exists():
            if import_line.strip() not in claude_md.read_text():
                with claude_md.open("a") as f:
                    f.write(f"\n{import_line}")
        else:
            claude_md.write_text(import_line)

def write_cbmignore(project_root: Path, cbmignore_file: Path):
    dst = project_root / ".cbmignore"
    shutil.copy2(cbmignore_file, dst)

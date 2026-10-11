"""Offline check that mirrors the Hermes portable-package loader rules for this repo.

It follows hermes_cli/agent_plugins.py in NousResearch/hermes-agent (plugin.json fields,
Agent Skills frontmatter, mcp.json shape, trust declaration). It is not a replacement for
`hermes plugins validate`, which CI runs on the catalog PR.
Run: python3 tests/validate.py
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
PLUGIN_FIELDS = {"$schema", "name", "version", "description", "author", "homepage",
                 "repository", "license", "keywords", "extensions"}
PLUGIN_NAME = re.compile(r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
SKILL_NAME = re.compile(r"^(?!.*--)[a-z0-9]+(?:-[a-z0-9]+)*$")
errors = []


def check(ok, msg):
    if not ok:
        errors.append(msg)


plugin = json.loads((ROOT / "plugin.json").read_text())
check(plugin.get("$schema") == PLUGIN_SCHEMA, "plugin.json $schema")
check(not set(plugin) - PLUGIN_FIELDS, f"unknown plugin.json keys {set(plugin) - PLUGIN_FIELDS}")
check(bool(PLUGIN_NAME.fullmatch(plugin.get("name", ""))), "plugin name")
for key in ("version", "description", "homepage", "repository", "license"):
    check(isinstance(plugin.get(key), str) and plugin[key], f"plugin.json {key}")

mcp = json.loads((ROOT / "mcp.json").read_text())
check(set(mcp) == {"$schema", "mcpServers"}, "mcp.json keys")
check(mcp.get("$schema") == MCP_SCHEMA, "mcp.json $schema")
for name, cfg in mcp["mcpServers"].items():
    check(set(cfg) <= {"type", "url", "headers"}, f"{name}: unknown keys")
    check(cfg.get("type") == "streamable-http", f"{name}: type")
    u = urlsplit(cfg.get("url", ""))
    check(u.scheme == "https" and u.netloc and not u.username and not u.fragment, f"{name}: url")
    check("headers" not in cfg, f"{name}: no credentials in mcp.json")

servers = plugin.get("extensions", {}).get("com.nousresearch.hermes", {}).get("servers", {})
for name, decl in servers.items():
    check(name in mcp["mcpServers"], f"declaration {name} has no mcp.json server")
    check(set(decl) <= {"app", "requires", "liveness", "trust"}, f"{name}: declaration keys")
    check(decl.get("trust") in ("full", "untrusted"), f"{name}: trust value")

skills = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
check(len(skills) == 21, f"expected 21 skills, found {len(skills)}")
for d in skills:
    text = (d / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    check(m is not None, f"{d.name}: frontmatter")
    if not m:
        continue
    fm = dict(re.findall(r"^(\w+):\s*(.*)$", m.group(1), re.M))
    desc = fm.get("description", "").strip().strip('"')
    check(fm.get("name") == d.name, f"{d.name}: name must match directory")
    check(bool(SKILL_NAME.fullmatch(d.name)), f"{d.name}: name pattern")
    check(1 <= len(desc) <= 1024, f"{d.name}: description length {len(desc)}")

bad = [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts
       and p.suffix in {".pyc", ".pyo", ".so", ".dylib", ".exe", ".wasm", ".zip", ".gz", ".tgz"}]
check(not bad, f"binary or archive files: {bad}")

if errors:
    print("FAIL")
    print("\n".join(" - " + e for e in errors))
    sys.exit(1)
print(f"OK: plugin.json, mcp.json, {len(skills)} skills")

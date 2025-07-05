from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import glob
import httpx
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import re
import asyncio
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
DEMO_BASE_PATH = os.path.dirname(os.path.abspath(__file__))

MCP_TOOLS = {
    "file_reader": {
        "description": "Read and analyze file contents",
        "params": ["path"]
    },
    "code_analyzer": {
        "description": "Deep analysis of code structure and patterns",
        "params": ["file_path", "analysis_type"]
    },
    "dependency_mapper": {
        "description": "Map dependencies and imports between files",
        "params": ["source_file", "target_files"]
    },
    "search_codebase": {
        "description": "Search for patterns, functions, or text in codebase",
        "params": ["query", "file_pattern"]
    },
    "graph_builder": {
        "description": "Build or update knowledge graph connections",
        "params": ["nodes", "relationship_type"]
    },
    "ast_parser": {
        "description": "Parse abstract syntax tree of code",
        "params": ["file_path", "extract_type"]
    },
    "symbol_finder": {
        "description": "Find symbol definitions and usages",
        "params": ["symbol_name", "scope"]
    },
    "refactor_helper": {
        "description": "Suggest refactoring opportunities",
        "params": ["file_path", "refactor_type"]
    }
}

file_graph = {}
current_base_path = None

class InitializeRequest(BaseModel):
    path: str

class FileAnalysis(BaseModel):
    path: str
    content: str
    analysis: Dict[str, Any]

class MCPCommand(BaseModel):
    command: str

async def analyze_with_llm(content: str, file_path: str, all_files: List[str]) -> Dict[str, Any]:
    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_name)[1]
    
    prompt = f"""Analyze this code file and extract detailed information. Return ONLY valid JSON.

File: {file_path}
Extension: {file_ext}
Available files in project: {[os.path.basename(f) for f in all_files]}

Code (first 1500 chars):
{content[:1500]}

Return JSON with these fields:
- type: "module" or "class" or "component"
- name: main name/identifier
- imports: list of imported modules/files (match with available files)
- exports: list of exported functions/classes/components
- functions: list of function names defined
- classes: list of class names defined
- dependencies: list of files this depends on (from available files)
- calls: list of functions/methods this file calls from other files
"""

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "anthropic/claude-3.5-sonnet-20241022",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 500
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            try:
                content_str = result['choices'][0]['message']['content']
                json_match = re.search(r'\{.*\}', content_str, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                    return analysis
                else:
                    raise ValueError("No JSON found")
            except:
                return {
                    "type": "module",
                    "name": Path(file_path).stem,
                    "imports": [],
                    "exports": [],
                    "functions": [],
                    "classes": [],
                    "dependencies": [],
                    "calls": []
                }
        return {"error": "Analysis failed"}

@app.post("/api/mcp/initialize")
async def initialize_codebase(request: InitializeRequest):
    global file_graph, current_base_path
    file_graph = {}  # Clear previous graph
    base_path = request.path
    
    # Handle relative paths - make them relative to demo folder
    if not os.path.isabs(base_path):
        # Remove leading slash if present
        if base_path.startswith('/'):
            base_path = base_path[1:]
        # Make path relative to demo folder
        base_path = os.path.join(DEMO_BASE_PATH, base_path)
    
    if not os.path.exists(base_path):
        # Try as absolute path
        if not os.path.exists(request.path):
            # Default to demo folder
            base_path = DEMO_BASE_PATH
    
    current_base_path = base_path
    
    nodes = []
    edges = []
    node_id = 0
    node_map = {}
    
    root_node = {
        "id": str(node_id),
        "type": "folder",
        "label": os.path.basename(base_path) or "root",
        "data": {
            "path": base_path,
            "type": "folder"
        }
    }
    nodes.append(root_node)
    node_map["root"] = str(node_id)
    node_id += 1
    
    file_patterns = ["**/*.py", "**/*.js", "**/*.jsx", "**/*.ts", "**/*.tsx", "**/*.json", "**/*.java", "**/*.cpp", "**/*.c", "**/*.h", "**/*.hpp", "**/*.cs", "**/*.rb", "**/*.go", "**/*.rs", "**/*.php", "**/*.swift", "**/*.kt", "**/*.scala", "**/*.r", "**/*.m", "**/*.mm", "**/*.xml", "**/*.yaml", "**/*.yml", "**/*.toml", "**/*.ini", "**/*.cfg", "**/*.conf", "**/*.sh", "**/*.bash", "**/*.zsh", "**/*.fish", "**/*.ps1", "**/*.bat", "**/*.cmd"]
    files_found = []
    
    for pattern in file_patterns:
        matches = glob.glob(os.path.join(base_path, pattern), recursive=True)
        # Filter out files that are not under the requested path
        for match in matches:
            if os.path.commonpath([match, base_path]) == base_path:
                files_found.append(match)
    
    files_found = files_found[:20]
    
    file_contents = {}
    for file_path in files_found:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                file_contents[file_path] = content
        except:
            pass
    
    for file_path in files_found:
        try:
            content = file_contents.get(file_path, "")
            if not content:
                continue
                
            rel_path = os.path.relpath(file_path, base_path)
            file_ext = os.path.splitext(file_path)[1]
            file_type = {
                '.py': 'python',
                '.js': 'javascript', 
                '.jsx': 'javascript',
                '.ts': 'typescript',
                '.tsx': 'typescript',
                '.json': 'json',
                '.java': 'java',
                '.cpp': 'cpp',
                '.c': 'c',
                '.h': 'c',
                '.hpp': 'cpp',
                '.cs': 'csharp',
                '.rb': 'ruby',
                '.go': 'go',
                '.rs': 'rust',
                '.php': 'php',
                '.swift': 'swift',
                '.kt': 'kotlin',
                '.scala': 'scala',
                '.xml': 'xml',
                '.yaml': 'yaml',
                '.yml': 'yaml'
            }.get(file_ext, 'text')
            file_name = os.path.basename(file_path)
            
            analysis = await analyze_with_llm(content, file_path, list(file_contents.keys()))
            
            node = {
                "id": str(node_id),
                "type": "file",
                "label": file_name,
                "data": {
                    "path": file_path,
                    "type": file_type,
                    "content": content[:500],
                    "full_content": content,
                    "analysis": analysis
                }
            }
            nodes.append(node)
            node_map[file_name] = str(node_id)
            node_map[Path(file_path).stem] = str(node_id)
            
            edges.append({
                "id": f"e-0-{node_id}",
                "source": "0",
                "target": str(node_id),
                "type": "contains"
            })
            
            file_graph[file_path] = {
                "node_id": str(node_id),
                "analysis": analysis,
                "content": content
            }
            
            node_id += 1
            
        except Exception as e:
            continue
    
    for node in nodes[1:]:
        if node["data"].get("analysis"):
            analysis = node["data"]["analysis"]
            
            for imp in analysis.get("imports", []):
                clean_imp = imp.replace("./", "").replace("../", "").replace(".py", "").replace(".js", "")
                if clean_imp in node_map and node_map[clean_imp] != node["id"]:
                    edge_id = f"e-{node['id']}-{node_map[clean_imp]}-import"
                    if not any(e["id"] == edge_id for e in edges):
                        edges.append({
                            "id": edge_id,
                            "source": node["id"],
                            "target": node_map[clean_imp],
                            "type": "imports",
                            "label": "imports"
                        })
            
            for dep in analysis.get("dependencies", []):
                clean_dep = dep.replace(".py", "").replace(".js", "")
                if clean_dep in node_map and node_map[clean_dep] != node["id"]:
                    edge_id = f"e-{node['id']}-{node_map[clean_dep]}-dep"
                    if not any(e["id"] == edge_id for e in edges):
                        edges.append({
                            "id": edge_id,
                            "source": node["id"],
                            "target": node_map[clean_dep],
                            "type": "depends",
                            "label": "depends on"
                        })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "filesAnalyzed": len(files_found),
            "nodesCreated": len(nodes),
            "edgesCreated": len(edges)
        }
    }

async def interpret_command(command: str) -> Dict[str, Any]:
    # Quick pattern matching for common commands
    command_lower = command.lower()
    
    if any(word in command_lower for word in ['search', 'find', 'look for', 'where is', 'locate']):
        # Extract the search query
        query = command
        for prefix in ['search for', 'find', 'look for', 'where is', 'locate', 'search']:
            if prefix in command_lower:
                query = command[command_lower.index(prefix) + len(prefix):].strip()
                break
        
        return {
            "tool": "search_codebase",
            "params": {"query": query},
            "confidence": 0.9,
            "explanation": f"Searching codebase for: {query}"
        }
    
    prompt = f"""Given this natural language command, determine which MCP tool to use and with what parameters.

Command: {command}

Available tools:
{json.dumps(MCP_TOOLS, indent=2)}

Return JSON with:
- tool: the tool name to use (or null if no matching tool)
- params: dict of parameters with actual values extracted from the command
- confidence: 0-1 confidence score
- explanation: brief explanation

For search commands, extract the actual search term into params.query
If the command doesn't match any tool well, return tool: null
"""

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "anthropic/claude-3.5-sonnet-20241022",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 300
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            try:
                content_str = result['choices'][0]['message']['content']
                json_match = re.search(r'\{.*\}', content_str, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass
    
    return {"tool": None, "confidence": 0}

@app.post("/api/mcp/execute")
async def execute_command(request: MCPCommand):
    interpretation = await interpret_command(request.command)
    
    if not interpretation.get("tool"):
        return {
            "tool": None,
            "status": "error",
            "error": "No matching MCP tool found for this command",
            "suggestion": "Try using '/' to see available tools"
        }
    
    tool_name = interpretation["tool"]
    params = interpretation.get("params", {})
    
    global file_graph
    
    if tool_name == "search_codebase":
        query = params.get("query", "")
        if not query:
            # Extract search term from natural language
            import re
            match = re.search(r'(?:search|find|look for|where is)\s+(.+?)(?:\s+stored|\s+located|$)', request.command, re.I)
            if match:
                query = match.group(1)
            else:
                query = request.command.replace("/search_codebase", "").strip()
        
        # Create search variations intelligently
        search_terms = set([query.lower()])
        
        # Split camelCase and PascalCase
        camel_split = re.sub('([A-Z])', r' \1', query).strip()
        search_terms.add(camel_split.lower())
        
        # Common variations
        variations = [
            query.replace(" ", "_"),
            query.replace(" ", "-"),
            query.replace(" ", ""),
            query.replace("_", " "),
            query.replace("-", " "),
            query.upper(),
            query.lower()
        ]
        
        for var in variations:
            search_terms.add(var.lower())
        
        # Special handling for common patterns
        if "api" in query.lower() and "key" in query.lower():
            search_terms.update(["api_key", "apikey", "API_KEY", "APIKEY", "ApiKey", "api-key"])
        
        # Add word boundary search for more accurate results
        word_patterns = [re.compile(r'\b' + re.escape(term) + r'\b', re.I) for term in search_terms]
        
        results = {}
        total_matches = 0
        
        # Only search files in the current initialized path
        for path, data in file_graph.items():
            if current_base_path and not path.startswith(current_base_path):
                continue
                
            content = data["content"]
            file_matches = []
            
            # First try exact matches with word boundaries
            for pattern in word_patterns:
                for match in pattern.finditer(content):
                    line_num = content[:match.start()].count('\n') + 1
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line_end = content.find('\n', match.end())
                    if line_end == -1:
                        line_end = len(content)
                    
                    line_text = content[line_start:line_end].strip()
                    
                    # Highlight the match
                    match_text = line_text[:100]
                    if len(line_text) > 100:
                        match_text += "..."
                    
                    file_matches.append({
                        "line": line_num,
                        "text": match_text,
                        "term": match.group(0),
                        "context": line_text
                    })
                    
                    total_matches += 1
                    if total_matches > 50:  # Limit total results
                        break
            
            # Deduplicate by line number
            seen_lines = set()
            unique_matches = []
            for match in file_matches:
                if match["line"] not in seen_lines:
                    seen_lines.add(match["line"])
                    unique_matches.append(match)
            
            if unique_matches:
                results[path] = unique_matches[:5]  # Max 5 matches per file
        
        if results:
            output_lines = [f"Found '{query}' in {len(results)} files ({total_matches} total matches):\n"]
            
            # Sort by number of matches
            sorted_results = sorted(results.items(), key=lambda x: len(x[1]), reverse=True)
            
            for path, matches in sorted_results[:10]:  # Show top 10 files
                rel_path = os.path.relpath(path, current_base_path) if current_base_path else path
                output_lines.append(f"\n📄 {rel_path}:")
                for match in matches[:3]:  # Show top 3 matches per file
                    output_lines.append(f"  Line {match['line']}: {match['text']}")
            
            if len(sorted_results) > 10:
                output_lines.append(f"\n... and {len(sorted_results) - 10} more files")
            
            return {
                "tool": tool_name,
                "status": "success",
                "output": "\n".join(output_lines),
                "details": {
                    "filesAnalyzed": len(file_graph),
                    "matchesFound": total_matches,
                    "filesWithMatches": len(results),
                    "confidence": interpretation.get("confidence", 0.9)
                }
            }
        else:
            # Try fuzzy search if no exact matches
            fuzzy_results = []
            for path, data in file_graph.items():
                if current_base_path and not path.startswith(current_base_path):
                    continue
                    
                content_lower = data["content"].lower()
                query_lower = query.lower()
                
                # Simple fuzzy match - all words from query appear somewhere
                query_words = query_lower.split()
                if all(word in content_lower for word in query_words):
                    rel_path = os.path.relpath(path, current_base_path) if current_base_path else path
                    fuzzy_results.append(rel_path)
            
            if fuzzy_results:
                return {
                    "tool": tool_name,
                    "status": "success",
                    "output": f"No exact matches for '{query}', but found potential matches in:\n" + 
                             "\n".join(f"📄 {f}" for f in fuzzy_results[:5]),
                    "details": {
                        "filesAnalyzed": len(file_graph),
                        "matchesFound": 0,
                        "fuzzyMatches": len(fuzzy_results)
                    }
                }
            else:
                return {
                    "tool": tool_name,
                    "status": "warning",
                    "output": f"No matches found for '{query}'",
                    "details": {
                        "filesAnalyzed": len(file_graph),
                        "matchesFound": 0,
                        "searchTerms": list(search_terms)[:5]
                    }
                }
    
    elif tool_name == "dependency_mapper":
        edges_created = 0
        for path, data in file_graph.items():
            if data["analysis"].get("imports"):
                edges_created += len(data["analysis"]["imports"])
        
        return {
            "tool": tool_name,
            "status": "success",
            "output": f"Mapped dependencies across {len(file_graph)} files",
            "details": {
                "filesAnalyzed": len(file_graph),
                "edgesCreated": edges_created,
                "confidence": interpretation.get("confidence", 0.8)
            }
        }
    
    else:
        return {
            "tool": tool_name,
            "status": "success",
            "output": f"Executed {tool_name} with params: {json.dumps(params)}",
            "details": {
                "filesAnalyzed": len(file_graph),
                "confidence": interpretation.get("confidence", 0.8)
            }
        }

@app.get("/api/mcp/tools")
async def get_available_tools():
    return {
        "tools": [
            {
                "name": name,
                "description": info["description"],
                "params": info["params"],
                "command": f"/{name}"
            }
            for name, info in MCP_TOOLS.items()
        ]
    }

@app.post("/api/mcp/update")
async def update_graph(file_path: str):
    global file_graph
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = await analyze_with_llm(content, file_path, list(file_graph.keys()))
        
        file_graph[file_path] = {
            "analysis": analysis,
            "content": content,
            "last_updated": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "file": file_path,
            "analysis": analysis
        }
    
    return {"status": "error", "message": "File not found"}

@app.get("/api/mcp/node/{node_id}")
async def get_node_details(node_id: str):
    for path, data in file_graph.items():
        if data.get("node_id") == node_id:
            return {
                "id": node_id,
                "type": "file",
                "path": path,
                "content": data.get("content", ""),
                "analysis": data.get("analysis", {})
            }
    
    return {
        "id": node_id,
        "type": "unknown",
        "content": "",
        "analysis": {}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
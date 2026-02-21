# 
# Copyright (C) 2026 Romashka
# 
# This file is part of Telekit.
# 
# Telekit is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version.
# 
# Telekit is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty 
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See 
# the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License 
# along with Telekit. If not, see <https://www.gnu.org/licenses/>.
# 

"""
Canvas to Telekit DSL executable model parser.

Rules:
  - Each text node = one scene
  - Node text format:

    - WITH header:
        ```
        Button Label & Title
        ---
        Scene message text
        ```
        produces: title=, message=, button_label (label = first line = title)

    - WITHOUT header:
        ```
        Scene text only
        ```
        produces: text=, button_label = auto (first 10 chars)

  - Edges: fromNode to toNode = button in fromNode's scene pointing to toNode's scene
  - Back edges (toNode to fromNode where toNode already points to fromNode) = "back" button
  - Groups are ignored
  - Colors are ignored
"""

import json
import re




import json
import re
import sys


def parse_node_text(raw: str) -> tuple[str | None, str | None, str]:
    """
    Returns (button_label, title, body).

    With --- separator:
      button_label = title = text before ---
      body         = text after ---

    Without --- separator:
      button_label = None  (will be auto-generated)
      title        = None
      body         = full text  (stored as "text" in scene)

    Obsidian sometimes prepends garbage --- lines — stripped first.
    """
    raw = raw.strip()
    # Remove leading garbage: lines that are just --- before real content
    raw = re.sub(r'^(---\s*\n)+', '', raw).strip()

    if "---" in raw:
        parts = raw.split("---", 1)
        label_and_title = parts[0].strip()
        message = parts[1].strip()
        return label_and_title, label_and_title, message
    else:
        return None, None, raw


def auto_label(text: str, max_len: int = 24) -> str:
    """Generate button label from first line, trimmed to max_len at word boundary."""
    first_line = text.splitlines()[0].strip() if text else "..."
    if len(first_line) <= max_len:
        return first_line
    trimmed = first_line[:max_len]
    last_space = trimmed.rfind(" ")
    if last_space > 0:
        return trimmed[:last_space]
    return trimmed


def canvas_to_model(canvas: dict) -> dict:
    nodes = canvas.get("nodes", [])
    edges = canvas.get("edges", [])

    # Filter: only text nodes (skip groups, files, etc.)
    text_nodes = {n["id"]: n for n in nodes if n.get("type") == "text"}

    # Parse each node
    parsed: dict[str, dict] = {}
    for nid, node in text_nodes.items():
        raw_text = node.get("text", "")
        button_label, title, body = parse_node_text(raw_text)
        parsed[nid] = {
            "button_label": button_label,  # how THIS node appears as a button in parent scenes
            "title":        title,         # None if no --- separator
            "body":         body,          # message (if title exists) or text (if not)
        }

    # Build adjacency: fromNode → list of toNode ids
    adjacency: dict[str, list[str]] = {nid: [] for nid in text_nodes}
    for edge in edges:
        fn = edge.get("fromNode")
        tn = edge.get("toNode")
        if fn in text_nodes and tn in text_nodes:
            adjacency[fn].append(tn)


    # Topological BFS from roots (nodes with no incoming forward edges)
    incoming: dict[str, int] = {nid: 0 for nid in text_nodes}
    for fn, targets in adjacency.items():
        for tn in targets:
            incoming[tn] += 1

    # Among roots, lowest Y = main
    roots = [nid for nid, cnt in incoming.items() if cnt == 0]
    roots.sort(key=lambda nid: text_nodes[nid].get("y", 0))
    if not roots:
        roots = sorted(text_nodes.keys(), key=lambda nid: text_nodes[nid].get("y", 0))

    visited = []
    seen = set()
    q = list(roots)
    while q:
        cur = q.pop(0)
        if cur in seen:
            continue
        seen.add(cur)
        visited.append(cur)
        for nxt in adjacency.get(cur, []):
            if nxt not in seen:
                q.append(nxt)
    for nid in text_nodes:
        if nid not in seen:
            visited.append(nid)

    # Name scenes: slug from title (if exists) or first line of body
    used_names: set[str] = set()
    id_to_name: dict[str, str] = {}

    for i, nid in enumerate(visited):
        p = parsed[nid]
        source_text = p["title"] or p["body"]
        first_line = source_text.splitlines()[0].strip() if source_text else ""
        slug = re.sub(r"[^a-z0-9]+", "_", first_line.lower()).strip("_")
        if not slug:
            slug = f"scene_{i}"
        base = slug
        counter = 1
        while slug in used_names:
            slug = f"{base}_{counter}"
            counter += 1
        used_names.add(slug)
        id_to_name[nid] = slug

    # First scene → "main"
    if visited:
        first_id = visited[0]
        old_name = id_to_name[first_id]
        if old_name != "main" and "main" not in used_names:
            used_names.discard(old_name)
            id_to_name[first_id] = "main"
            used_names.add("main")

    # Assemble scenes
    scenes: dict[str, dict] = {}

    for nid in visited:
        scene_name = id_to_name[nid]
        p = parsed[nid]
        buttons: dict[str, dict] = {}

        for tn in adjacency.get(nid, []):
            target_name = id_to_name[tn]
            btn_label = parsed[tn]["button_label"]
            if not btn_label:
                btn_label = auto_label(parsed[tn]["body"])
            buttons[btn_label] = {"type": "scene", "target": target_name}

        # title+message vs plain text
        if p["title"] is not None:
            scene: dict = {
                "name":    scene_name,
                "title":   p["title"],
                "message": p["body"],
            }
        else:
            scene: dict = {
                "name": scene_name,
                "text": p["body"],
            }

        if buttons:
            scene["buttons"] = buttons

        scenes[scene_name] = scene
        scene["parse_mode"] = "markdown"

    order = [id_to_name[nid] for nid in visited]

    return {
        "order": order,
        "config": {
            "next_order": order,
        },
        "scenes": scenes,
    }


def parse(path: str):
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    canvas = json.loads(raw)
    model = canvas_to_model(canvas)

    return model

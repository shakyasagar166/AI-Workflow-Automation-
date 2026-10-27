import re
import os
from typing import Dict, Any, List, Set, Tuple, Optional
from collections import defaultdict, deque

class DependencyResolver:
    """Handles DAG analysis, topological sequencing, cycle detection, and variable interpolation."""

    @staticmethod
    def validate_dag(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        """Checks for cycle detection and verifies edge integrity."""
        node_ids = {n.get("id") for n in nodes if isinstance(n, dict)}
        
        # Verify edge endpoints exist
        for edge in edges:
            src = edge.get("source")
            tgt = edge.get("target")
            if src not in node_ids:
                return False, f"Edge references nonexistent source node: {src}"
            if tgt not in node_ids:
                return False, f"Edge references nonexistent target node: {tgt}"

        # Kahn's algorithm for cycle detection
        in_degree = {nid: 0 for nid in node_ids}
        adj = defaultdict(list)
        for edge in edges:
            src = edge.get("source")
            tgt = edge.get("target")
            adj[src].append(tgt)
            in_degree[tgt] += 1

        queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
        visited_count = 0

        while queue:
            curr = queue.popleft()
            visited_count += 1
            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if visited_count != len(node_ids):
            return False, "Cycle detected in workflow graph. Workflows must be Directed Acyclic Graphs (DAG)."

        return True, None

    @staticmethod
    def build_dependency_graph(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, Set[str]]:
        """Returns a map of node_id -> set of prerequisite node_ids that must complete first."""
        node_ids = {n["id"] for n in nodes}
        dependencies: Dict[str, Set[str]] = {nid: set() for nid in node_ids}

        for edge in edges:
            src = edge.get("source")
            tgt = edge.get("target")
            if src in node_ids and tgt in node_ids:
                dependencies[tgt].add(src)

        return dependencies

    @staticmethod
    def interpolate_value(val: Any, context: Dict[str, Any]) -> Any:
        """Recursively interpolates {{path.to.variable}} expressions against context."""
        if isinstance(val, str):
            pattern = re.compile(r"\{\{([^{}]+)\}\}")
            
            # Exact match replacement (preserves object/list/bool types)
            exact_match = re.fullmatch(r"\{\{([^{}]+)\}\}", val.strip())
            if exact_match:
                expr = exact_match.group(1).strip()
                resolved = DependencyResolver._extract_by_path(expr, context)
                return resolved if resolved is not None else val

            # Substring replacement for strings
            def replacer(match):
                expr = match.group(1).strip()
                res = DependencyResolver._extract_by_path(expr, context)
                return str(res) if res is not None else match.group(0)

            return pattern.sub(replacer, val)

        elif isinstance(val, dict):
            return {k: DependencyResolver.interpolate_value(v, context) for k, v in val.items()}
        elif isinstance(val, list):
            return [DependencyResolver.interpolate_value(item, context) for item in val]
        return val

    @staticmethod
    def _extract_by_path(path_expr: str, context: Dict[str, Any]) -> Any:
        """Extracts value using dot notation like 'steps.node_1.output.sentiment' or 'env.SOME_KEY'."""
        parts = path_expr.split(".")
        first = parts[0]

        if first == "env" and len(parts) > 1:
            return os.getenv(parts[1], "")

        curr = context
        for part in parts:
            if isinstance(curr, dict) and part in curr:
                curr = curr[part]
            elif isinstance(curr, list) and part.isdigit() and int(part) < len(curr):
                curr = curr[int(part)]
            else:
                return None
        return curr

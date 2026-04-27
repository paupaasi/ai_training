"""
Agent Message Tracing Module

Provides structured tracing for agent messages to enable debugging,
performance analysis, and message flow visualization.

Usage:
    from trace import trace_message, trace_function_call, get_trace
    
    trace_message("user", "Hello")
    trace_function_call("google_search", {"query": "AI news"})
    for msg in get_trace():
        print(msg)
"""

import uuid
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class TraceEntry:
    """Single trace entry for an agent message."""
    id: str
    timestamp: str
    direction: str  # "in" | "out" | "call" | "response"
    role: str  # "user" | "model" | "function"
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentTracer:
    """Simple in-memory tracer for agent messages."""
    
    def __init__(self):
        self._entries: List[TraceEntry] = []
        self._enabled = True
    
    def disable(self):
        self._enabled = False
    
    def enable(self):
        self._enabled = True
    
    def clear(self):
        self._entries.clear()
    
    def log(self, direction: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Log a message entry. Returns the trace ID."""
        if not self._enabled:
            return ""
        
        entry = TraceEntry(
            id=str(uuid.uuid4())[:8],
            timestamp=datetime.now().isoformat(),
            direction=direction,
            role=role,
            content=content[:500] if content else "",  # Truncate long content
            metadata=metadata or {},
        )
        self._entries.append(entry)
        return entry.id
    
    def get_entries(self) -> List[TraceEntry]:
        """Get all trace entries."""
        return self._entries.copy()
    
    def get_json(self) -> str:
        """Get trace as JSON string."""
        return json.dumps([asdict(e) for e in self._entries], indent=2)
    
    def summary(self) -> Dict[str, Any]:
        """Get trace summary statistics."""
        directions = {}
        roles = {}
        for e in self._entries:
            directions[e.direction] = directions.get(e.direction, 0) + 1
            roles[e.role] = roles.get(e.role, 0) + 1
        return {
            "total": len(self._entries),
            "directions": directions,
            "roles": roles,
        }


_global_tracer = AgentTracer()


def trace_message(role: str, content: str, direction: str = "in", metadata: Optional[Dict[str, Any]] = None) -> str:
    """Log a message in the trace."""
    return _global_tracer.log(direction, role, content, metadata)


def trace_function_call(name: str, args: Dict[str, Any], direction: str = "call") -> str:
    """Log a function call in the trace."""
    args_preview = json.dumps(args)[:200]
    return _global_tracer.log(direction, "function", f"{name}({args_preview})", {"function": name, "args": args})


def trace_function_response(name: str, result: Dict[str, Any]) -> str:
    """Log a function response in the trace."""
    result_preview = json.dumps(result)[:200]
    is_error = not result.get("ok", True) if isinstance(result, dict) else False
    return _global_tracer.log("response", "function", f"{name} -> {result_preview}", {"function": name, "result": result, "error": is_error})


def trace_event(event_type: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
    """Log a generic event in the trace."""
    return _global_tracer.log("event", event_type, content, metadata)


def get_trace() -> List[TraceEntry]:
    """Get all trace entries."""
    return _global_tracer.get_entries()


def get_trace_json() -> str:
    """Get trace as JSON."""
    return _global_tracer.get_json()


def get_trace_summary() -> Dict[str, Any]:
    """Get trace summary."""
    return _global_tracer.summary()


def clear_trace() -> None:
    """Clear the trace."""
    _global_tracer.clear()


def enable_trace() -> None:
    """Enable tracing."""
    _global_tracer.enable()


def disable_trace() -> None:
    """Disable tracing."""
    _global_tracer.disable()
#!/usr/bin/env python3
"""
Activity Selection Agent Web UI - Flask Application

Simple web interface for the activity selection agent.
Provides: search, view activities, manage family profile, record visits
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS

# Add parent directory to path
AGENT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(AGENT_DIR))
sys.path.insert(0, str(AGENT_DIR / "memory"))
sys.path.insert(0, str(AGENT_DIR / "tools"))

from agent_env import load_agent_environment
load_agent_environment()

from memory import MemoryStore

# Initialize Flask app
app = Flask(__name__, template_folder="templates")
CORS(app)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")

# Initialize memory store
memory = MemoryStore()

# In-memory conversation history per session
conversation_history = {}


# ============================================================================
# Helper Functions
# ============================================================================

def run_agent_query(query: str, profile: Dict[str, Any] = None) -> str:
    """Run a query through the main agent."""
    agent_path = AGENT_DIR / "activity_agent.py"
    
    try:
        cmd = ["python3", str(agent_path), query]
        print(f"DEBUG: Running command: {' '.join(cmd)}", file=sys.stderr)
        print(f"DEBUG: Working directory: {str(AGENT_DIR)}", file=sys.stderr)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(AGENT_DIR)
        )
        
        print(f"DEBUG: Return code: {result.returncode}", file=sys.stderr)
        print(f"DEBUG: Stdout length: {len(result.stdout)}", file=sys.stderr)
        print(f"DEBUG: Stderr length: {len(result.stderr)}", file=sys.stderr)
        
        if result.returncode == 0:
            if result.stdout:
                return result.stdout
            else:
                print(f"DEBUG: Stdout is empty, stderr: {result.stderr[:200]}", file=sys.stderr)
                return "No output from agent"
        else:
            return f"Error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Request timed out (30s)"
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# Routes: Status & Health
# ============================================================================

@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "agent": "activity-selection"
    })


@app.route("/")
def index():
    """Main dashboard page."""
    profile = memory.get_family_profile()
    return render_template("index.html", profile=profile)


# ============================================================================
# Routes: Profile Management
# ============================================================================

@app.route("/api/profile", methods=["GET"])
def get_profile():
    """Get family profile."""
    profile = memory.get_family_profile()
    return jsonify(profile or {"error": "No profile found"})


@app.route("/api/profile", methods=["POST"])
def update_profile():
    """Update family profile."""
    data = request.get_json()
    
    # Get current profile or create new
    current = memory.get_family_profile() or {
        "name": "Our Family",
        "family_members": [],
        "home_city": "Helsinki",
        "home_country": "FI"
    }
    
    # Update fields
    for key in ["home_city", "home_country", "family_members", "budget_preference", "preferred_categories", 
                "indoor_outdoor_preference", "max_travel_minutes"]:
        if key in data:
            current[key] = data[key]
    
    if memory.set_family_profile(current):
        return jsonify({"status": "success", "profile": current})
    else:
        return jsonify({"status": "error", "message": "Failed to update profile"}), 500


# ============================================================================
# Routes: Activity Search & Enrichment
# ============================================================================

@app.route("/api/search", methods=["POST"])
def search_activities():
    """Search for activities - adds to conversation history so chat can follow up."""
    data = request.get_json()
    city = data.get("city")
    category = data.get("category")
    
    if not city:
        return jsonify({"error": "City is required"}), 400
    
    # Build user-friendly query for conversation history
    query = f"Find {category or 'fun'} activities in {city}"
    result = run_agent_query(query)
    
    # Add search to conversation history so follow-ups in chat have context
    session_id = request.remote_addr
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    
    conversation_history[session_id].append({
        "user": query,
        "agent": result,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Keep history from growing too large
    if len(conversation_history[session_id]) > 20:
        conversation_history[session_id] = conversation_history[session_id][-10:]
    
    return jsonify({
        "query": query,
        "result": result,
        "city": city,
        "category": category
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    """Chat with the activity agent, maintaining conversation history."""
    data = request.get_json()
    message = data.get("message")
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    # Get or create session conversation history
    session_id = request.remote_addr  # Simple session ID based on IP
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    
    # Build query with conversation context
    history_context = ""
    if conversation_history[session_id]:
        history_context = "\n\nPrevious conversation:\n"
        for entry in conversation_history[session_id][-4:]:  # Last 4 exchanges
            history_context += f"- User: {entry['user']}\n"
            history_context += f"- Agent: {entry['agent'][:200]}...\n" if len(entry['agent']) > 200 else f"- Agent: {entry['agent']}\n"
        history_context += f"\nNew user message: {message}"
        query = message + history_context
    else:
        query = message
    
    # Run agent query
    result = run_agent_query(query)
    
    # Store in conversation history
    conversation_history[session_id].append({
        "user": message,
        "agent": result,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Keep history from growing too large
    if len(conversation_history[session_id]) > 20:
        conversation_history[session_id] = conversation_history[session_id][-10:]
    
    return jsonify({
        "response": result,
        "message": message
    })


@app.route("/api/chat/clear", methods=["POST"])
def clear_chat():
    """Clear conversation history for new chat."""
    session_id = request.remote_addr
    if session_id in conversation_history:
        conversation_history[session_id] = []
    
    return jsonify({"status": "success", "message": "Chat history cleared"})


@app.route("/api/activities", methods=["GET"])
def get_activities():
    """Get activities from database."""
    city = request.args.get("city")
    category = request.args.get("category")
    limit = int(request.args.get("limit", 20))
    
    activities = memory.get_activities(city=city, category=category, limit=limit)
    
    return jsonify({
        "activities": activities,
        "count": len(activities)
    })


@app.route("/api/activities/<activity_id>", methods=["GET"])
def get_activity(activity_id):
    """Get specific activity."""
    # This would need implementation in memory.py
    return jsonify({"activity_id": activity_id, "status": "not implemented yet"})


# ============================================================================
# Routes: Visit Tracking
# ============================================================================

@app.route("/api/activities/<activity_id>/visit", methods=["POST"])
def record_visit(activity_id):
    """Record a visit to an activity."""
    data = request.get_json()
    rating = data.get("rating")
    notes = data.get("notes")
    
    memory.record_visit(activity_id, rating, notes)
    
    return jsonify({
        "status": "success",
        "activity_id": activity_id,
        "rating": rating,
        "notes": notes
    })


@app.route("/api/visits", methods=["GET"])
def get_visits():
    """Get visit history."""
    limit = int(request.args.get("limit", 50))
    visits = memory.get_visit_history(limit=limit)
    
    return jsonify({
        "visits": visits,
        "count": len(visits)
    })


# ============================================================================
# Routes: Recommendations
# ============================================================================

@app.route("/api/recommendations", methods=["GET"])
def get_recommendations():
    """Get personalized activity recommendations."""
    profile = memory.get_family_profile()
    
    if not profile:
        return jsonify({"error": "No family profile found"}), 400
    
    query = "Based on my preferences and past visits, what activities would you recommend?"
    result = run_agent_query(query, profile)
    
    return jsonify({
        "query": query,
        "result": result,
        "profile": profile
    })


# ============================================================================
# Routes: Semantic Search
# ============================================================================

@app.route("/api/search-semantic", methods=["POST"])
def search_semantic():
    """Semantic search for activities."""
    data = request.get_json()
    query = data.get("query")
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    results = memory.search_activities(query)
    
    return jsonify({
        "query": query,
        "results": results,
        "count": len(results)
    })


# ============================================================================
# Routes: Stats & Analytics
# ============================================================================

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get system statistics."""
    all_activities = memory.get_activities(limit=1000)
    visits = memory.get_visit_history(limit=1000)
    profile = memory.get_family_profile()
    
    # Calculate stats
    categories = {}
    cities = {}
    
    for activity in all_activities:
        cat = activity.get("category", "unknown")
        # Handle both string and array categories
        cat_list = cat if isinstance(cat, list) else [cat]
        for c in cat_list:
            categories[c] = categories.get(c, 0) + 1
        
        city = activity.get("city", "unknown")
        cities[city] = cities.get(city, 0) + 1
    
    avg_rating = None
    if visits and any(v.get("rating") for v in visits):
        ratings = [v.get("rating") for v in visits if v.get("rating")]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
    
    return jsonify({
        "total_activities": len(all_activities),
        "total_visits": len(visits),
        "avg_rating": avg_rating,
        "categories": categories,
        "cities": cities,
        "family_members": len(profile.get("family_members", [])) if profile else 0
    })


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """404 handler."""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 handler."""
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  Activity Selection Agent - Web UI")
    print("=" * 70)
    print("\n🚀 Starting Flask server...")
    print("📱 Open your browser at: http://localhost:5000")
    print("📖 API docs at: http://localhost:5000/api/")
    print("🔌 Health check: http://localhost:5000/health")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(debug=True, host="localhost", port=5000)

#!/usr/bin/env python3
"""
Creator Content Monitor - REST API Server

Run a local API server to query creator responses programmatically.

Usage:
    python creator_api.py [--port PORT] [--host HOST]

Endpoints:
    GET  /                     - API info and available endpoints
    GET  /creators             - List all creators
    GET  /creators/<name>      - Get specific creator profile
    POST /ask                  - Ask a question (JSON body: {"question": "...", "creator": "optional"})
    GET  /ask?q=<question>     - Quick ask via query parameter
    GET  /books/<topic>        - Get book recommendations
    GET  /compare/<topic>      - Compare philosophies on a topic
"""

import json
import argparse
from pathlib import Path

# Try to import Flask
try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from content_monitor import CreatorContentMonitor, get_response_data


def create_app(config_path: str = "creators.json") -> "Flask":
    """Create and configure the Flask application."""
    if not FLASK_AVAILABLE:
        raise ImportError("Flask is required for API server. Install with: pip install flask")

    app = Flask(__name__)

    # Find config file
    path = Path(config_path)
    if not path.exists():
        path = Path(__file__).parent / config_path

    monitor = CreatorContentMonitor(str(path))

    @app.route('/')
    def index():
        """API information and available endpoints."""
        return jsonify({
            "name": "Creator Content Monitor API",
            "version": "1.0.0",
            "description": "Query thought leaders and predict their responses",
            "creators": [c['name'] for c in monitor.creators['creators']],
            "endpoints": {
                "GET /": "This help message",
                "GET /creators": "List all creators with summaries",
                "GET /creators/<name>": "Get detailed creator profile",
                "POST /ask": "Ask a question (body: {question, creator?})",
                "GET /ask?q=<question>&creator=<name>": "Quick ask via query params",
                "GET /books/<topic>": "Get book recommendations",
                "GET /compare/<topic>": "Compare creator philosophies"
            },
            "example_questions": [
                "How do I overcome fear of failure?",
                "Should I quit my job to start a business?",
                "How do I find my life's purpose?",
                "What's the key to productivity?"
            ]
        })

    @app.route('/creators')
    def list_creators():
        """List all creators with basic info."""
        creators_list = []
        for c in monitor.creators['creators']:
            creators_list.append({
                "name": c['name'],
                "slug": c['slug'],
                "tagline": c['tagline'],
                "background": c['background'],
                "signature_concepts": c.get('signature_concepts', []),
                "books_count": len(c.get('content_sources', {}).get('books', []))
            })
        return jsonify({"creators": creators_list})

    @app.route('/creators/<name>')
    def get_creator(name: str):
        """Get detailed profile for a creator."""
        creator = monitor.get_creator(name)
        if not creator:
            return jsonify({"error": f"Creator '{name}' not found"}), 404

        return jsonify({
            "name": creator['name'],
            "tagline": creator['tagline'],
            "background": creator['background'],
            "philosophy": creator['philosophy'],
            "signature_concepts": creator.get('signature_concepts', []),
            "content_sources": creator.get('content_sources', {})
        })

    @app.route('/ask', methods=['GET', 'POST'])
    def ask_question():
        """
        Ask a question and get predicted responses.

        POST body: {"question": "your question", "creator": "optional name"}
        GET params: ?q=your+question&creator=optional+name
        """
        if request.method == 'POST':
            data = request.get_json() or {}
            question = data.get('question', '')
            creator_name = data.get('creator')
        else:
            question = request.args.get('q', '')
            creator_name = request.args.get('creator')

        if not question:
            return jsonify({
                "error": "No question provided",
                "usage": {
                    "POST": {"question": "your question", "creator": "optional"},
                    "GET": "?q=your+question&creator=optional"
                }
            }), 400

        result = get_response_data(question, creator_name, str(path))

        if "error" in result:
            return jsonify(result), 404

        return jsonify(result)

    @app.route('/books/<topic>')
    def get_books(topic: str):
        """Get book recommendations for a topic."""
        topic_lower = topic.lower()
        recommendations = []

        for creator in monitor.creators['creators']:
            books = creator.get('content_sources', {}).get('books', [])
            matching = []

            for book in books:
                themes = [t.lower() for t in book.get('key_themes', [])]
                if any(topic_lower in theme or theme in topic_lower for theme in themes):
                    matching.append(book)
                elif topic_lower in book.get('summary', '').lower():
                    matching.append(book)

            if matching:
                recommendations.append({
                    "creator": creator['name'],
                    "books": matching
                })

        return jsonify({
            "topic": topic,
            "recommendations": recommendations
        })

    @app.route('/compare/<topic>')
    def compare_topic(topic: str):
        """Compare how different creators approach a topic."""
        category = monitor._categorize_question(f"What about {topic}?")
        comparisons = []

        for creator in monitor.creators['creators']:
            responses = creator['philosophy'].get('likely_responses', {})

            if category in responses:
                perspective = responses[category]
            else:
                perspective = "; ".join(creator['philosophy']['core_beliefs'][:2])

            comparisons.append({
                "creator": creator['name'],
                "perspective": perspective,
                "core_beliefs": creator['philosophy']['core_beliefs'][:3]
            })

        return jsonify({
            "topic": topic,
            "category": category,
            "comparisons": comparisons
        })

    return app


def main():
    """Run the API server."""
    parser = argparse.ArgumentParser(description="Creator Content Monitor API Server")
    parser.add_argument('--port', '-p', type=int, default=5000, help='Port to run on')
    parser.add_argument('--host', '-H', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--config', '-c', default='creators.json', help='Config file path')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    if not FLASK_AVAILABLE:
        print("Error: Flask is required for API server.")
        print("Install with: pip install flask")
        return 1

    app = create_app(args.config)

    print(f"\n{'='*60}")
    print("CREATOR CONTENT MONITOR - API SERVER")
    print(f"{'='*60}")
    print(f"\nServer running at: http://{args.host}:{args.port}")
    print("\nEndpoints:")
    print(f"  http://{args.host}:{args.port}/          - API info")
    print(f"  http://{args.host}:{args.port}/creators  - List creators")
    print(f"  http://{args.host}:{args.port}/ask?q=... - Ask a question")
    print("\nExample:")
    print(f'  curl "http://{args.host}:{args.port}/ask?q=How+do+I+overcome+fear"')
    print(f"\nPress Ctrl+C to stop\n")

    app.run(host=args.host, port=args.port, debug=args.debug)
    return 0


if __name__ == '__main__':
    exit(main())

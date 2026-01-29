#!/usr/bin/env python3
"""
Creator Content Monitor & Response Predictor

A system to monitor content from thought leaders and predict their likely
responses to your questions based on their philosophies and published content.

Creators: James Altucher, Martha Beck, Tim Ferriss, Itamar Marani
"""

import json
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path
import argparse
import textwrap

# Optional imports for RSS feed monitoring
try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class CreatorContentMonitor:
    """Monitor and interact with creator content and philosophies."""

    def __init__(self, config_path: str = "creators.json"):
        self.config_path = Path(config_path)
        self.creators = self._load_config()
        self.rss_feeds = self._get_rss_feeds()

    def _load_config(self) -> dict:
        """Load creator configuration from JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def _get_rss_feeds(self) -> dict:
        """Extract RSS feeds from creator config."""
        feeds = {}
        for creator in self.creators['creators']:
            name = creator['name']
            # Check for single podcast
            if 'podcast' in creator.get('content_sources', {}):
                podcast = creator['content_sources']['podcast']
                if 'rss_feed' in podcast:
                    feeds[name] = {
                        'url': podcast['rss_feed'],
                        'type': 'podcast',
                        'name': podcast['name']
                    }
            # Check for multiple podcasts
            if 'podcasts' in creator.get('content_sources', {}):
                for podcast in creator['content_sources']['podcasts']:
                    if 'rss_feed' in podcast:
                        feeds[f"{name} - {podcast['name']}"] = {
                            'url': podcast['rss_feed'],
                            'type': 'podcast',
                            'name': podcast['name']
                        }
        return feeds

    def list_creators(self) -> None:
        """Display all monitored creators."""
        print("\n" + "="*60)
        print("MONITORED CONTENT CREATORS")
        print("="*60)

        for creator in self.creators['creators']:
            print(f"\n{creator['name']}")
            print(f"  {creator['tagline']}")
            print(f"  Background: {creator['background'][:80]}...")

            # Content sources
            sources = creator.get('content_sources', {})
            if 'podcast' in sources:
                print(f"  Podcast: {sources['podcast']['name']}")
            if 'podcasts' in sources:
                for p in sources['podcasts']:
                    print(f"  Podcast: {p['name']}")
            if 'books' in sources:
                print(f"  Books: {len(sources['books'])} published")
            if 'blog' in sources:
                print(f"  Blog: {sources['blog'].get('url', 'Available')}")

    def get_creator(self, name: str) -> Optional[dict]:
        """Get a creator by name (case-insensitive partial match)."""
        name_lower = name.lower()
        for creator in self.creators['creators']:
            if name_lower in creator['name'].lower():
                return creator
        return None

    def show_creator_profile(self, name: str) -> None:
        """Display detailed profile for a creator."""
        creator = self.get_creator(name)
        if not creator:
            print(f"Creator '{name}' not found.")
            return

        print("\n" + "="*60)
        print(f"{creator['name'].upper()}")
        print(f"{creator['tagline']}")
        print("="*60)

        print(f"\nBackground:\n{creator['background']}")

        print("\n" + "-"*40)
        print("CORE BELIEFS & PHILOSOPHY")
        print("-"*40)
        for belief in creator['philosophy']['core_beliefs']:
            print(f"  - {belief}")

        print("\n" + "-"*40)
        print("SIGNATURE CONCEPTS")
        print("-"*40)
        for concept in creator.get('signature_concepts', []):
            print(f"  - {concept}")

        print("\n" + "-"*40)
        print("BOOKS")
        print("-"*40)
        for book in creator.get('content_sources', {}).get('books', []):
            print(f"\n  '{book['title']}' ({book['year']})")
            print(f"    Themes: {', '.join(book['key_themes'])}")
            wrapped = textwrap.wrap(book['summary'], width=55)
            for line in wrapped:
                print(f"    {line}")

    def predict_response(self, question: str, creator_name: Optional[str] = None) -> None:
        """
        Predict how creator(s) would respond to a question based on their philosophy.
        If no creator specified, show predictions from all creators.
        """
        print("\n" + "="*60)
        print("QUESTION:")
        wrapped = textwrap.wrap(question, width=56)
        for line in wrapped:
            print(f"  {line}")
        print("="*60)

        # Determine question category
        category = self._categorize_question(question)

        if creator_name:
            creators_to_check = [self.get_creator(creator_name)]
            if not creators_to_check[0]:
                print(f"Creator '{creator_name}' not found.")
                return
        else:
            creators_to_check = self.creators['creators']

        for creator in creators_to_check:
            print(f"\n{'-'*60}")
            print(f"{creator['name'].upper()}'s Likely Response:")
            print(f"{'-'*60}")

            # Get response based on category
            responses = creator['philosophy'].get('likely_responses', {})

            if category in responses:
                response = responses[category]
            else:
                # Generate a general response based on core beliefs
                response = self._generate_general_response(creator, question)

            wrapped = textwrap.wrap(response, width=56)
            for line in wrapped:
                print(f"  {line}")

            # Add relevant signature concepts
            concepts = creator.get('signature_concepts', [])
            if concepts:
                print(f"\n  Relevant concepts: {', '.join(concepts[:3])}")

    def _categorize_question(self, question: str) -> str:
        """Categorize a question to match likely_responses keys."""
        question_lower = question.lower()

        categories = {
            'career_advice': ['career', 'job', 'work', 'profession', 'quit', 'promotion'],
            'fear': ['fear', 'afraid', 'scared', 'anxious', 'worry', 'nervous'],
            'anxiety': ['anxiety', 'anxious', 'stress', 'overwhelm', 'panic'],
            'money': ['money', 'income', 'salary', 'wealth', 'rich', 'financial'],
            'starting_business': ['start', 'business', 'entrepreneur', 'startup', 'company', 'launch'],
            'scaling_business': ['scale', 'grow', 'expand', 'growth', '7 figure', '8 figure'],
            'productivity': ['productive', 'efficiency', 'time', 'output', 'accomplish'],
            'learning_skills': ['learn', 'skill', 'master', 'study', 'improve'],
            'failure': ['fail', 'failure', 'mistake', 'wrong', 'mess up'],
            'life_purpose': ['purpose', 'meaning', 'passion', 'calling', 'direction'],
            'relationships': ['relationship', 'partner', 'friend', 'family', 'connect'],
            'self_doubt': ['doubt', 'confidence', 'believe', 'worthy', 'imposter'],
            'stress': ['stress', 'pressure', 'burnout', 'overwhelm'],
            'decision_making': ['decide', 'decision', 'choose', 'choice', 'option']
        }

        for category, keywords in categories.items():
            if any(keyword in question_lower for keyword in keywords):
                return category

        return 'general'

    def _generate_general_response(self, creator: dict, question: str) -> str:
        """Generate a response based on core beliefs when no specific category matches."""
        beliefs = creator['philosophy']['core_beliefs']
        name = creator['name']

        # Create a response that weaves in their core philosophy
        response = f"Based on {name}'s philosophy: "
        response += beliefs[0] + ". "
        if len(beliefs) > 1:
            response += "Remember: " + beliefs[1].lower() + ". "
        response += "Apply these principles to your specific situation."

        return response

    def fetch_latest_content(self, days: int = 7) -> None:
        """Fetch and display latest podcast episodes from RSS feeds."""
        print("\n" + "="*60)
        print(f"LATEST CONTENT (Last {days} days)")
        print("="*60)

        if not FEEDPARSER_AVAILABLE:
            print("\nNote: Install 'feedparser' for RSS feed monitoring:")
            print("  pip install feedparser")
            print("\nManual content links:")
            for creator in self.creators['creators']:
                sources = creator.get('content_sources', {})
                if 'podcast' in sources:
                    print(f"\n{creator['name']}:")
                    print(f"  {sources['podcast']['name']}: {sources['podcast'].get('url', 'N/A')}")
                if 'podcasts' in sources:
                    print(f"\n{creator['name']}:")
                    for p in sources['podcasts']:
                        print(f"  {p['name']}")
            return

        cutoff_date = datetime.now() - timedelta(days=days)

        for feed_name, feed_info in self.rss_feeds.items():
            print(f"\n{feed_name}:")
            print(f"  Source: {feed_info['name']}")

            try:
                feed = feedparser.parse(feed_info['url'])
                recent_episodes = []

                for entry in feed.entries[:10]:  # Check last 10 entries
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                        if pub_date > cutoff_date:
                            recent_episodes.append({
                                'title': entry.title,
                                'date': pub_date.strftime('%Y-%m-%d'),
                                'link': entry.link if hasattr(entry, 'link') else ''
                            })

                if recent_episodes:
                    for ep in recent_episodes[:3]:  # Show max 3
                        print(f"\n  [{ep['date']}] {ep['title'][:50]}...")
                        if ep['link']:
                            print(f"    Link: {ep['link'][:60]}...")
                else:
                    print(f"  No new episodes in the last {days} days")

            except Exception as e:
                print(f"  Unable to fetch feed: {str(e)[:50]}")

    def get_book_recommendations(self, topic: str) -> None:
        """Get book recommendations from all creators on a topic."""
        print("\n" + "="*60)
        print(f"BOOK RECOMMENDATIONS: {topic.upper()}")
        print("="*60)

        topic_lower = topic.lower()

        for creator in self.creators['creators']:
            books = creator.get('content_sources', {}).get('books', [])
            matching_books = []

            for book in books:
                themes = [t.lower() for t in book.get('key_themes', [])]
                if any(topic_lower in theme or theme in topic_lower for theme in themes):
                    matching_books.append(book)
                elif topic_lower in book.get('summary', '').lower():
                    matching_books.append(book)

            if matching_books:
                print(f"\n{creator['name']}:")
                for book in matching_books:
                    print(f"  - '{book['title']}' ({book['year']})")
                    print(f"    {book['summary'][:70]}...")

    def compare_philosophies(self, topic: str) -> None:
        """Compare how different creators approach a topic."""
        print("\n" + "="*60)
        print(f"PHILOSOPHY COMPARISON: {topic.upper()}")
        print("="*60)

        category = self._categorize_question(f"What about {topic}?")

        for creator in self.creators['creators']:
            print(f"\n{creator['name']}:")

            responses = creator['philosophy'].get('likely_responses', {})
            if category in responses:
                wrapped = textwrap.wrap(responses[category], width=54)
                for line in wrapped:
                    print(f"  {line}")
            else:
                # Show relevant core beliefs
                for belief in creator['philosophy']['core_beliefs'][:2]:
                    print(f"  - {belief}")

    def generate_summary_report(self) -> None:
        """Generate a comprehensive summary report of all creators."""
        print("\n" + "="*60)
        print("CREATOR CONTENT MONITOR - SUMMARY REPORT")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60)

        for creator in self.creators['creators']:
            print(f"\n{'='*60}")
            print(f"{creator['name']}")
            print(f"{'='*60}")
            print(f"\nTagline: {creator['tagline']}")

            # Key philosophy points
            print("\nKey Philosophy Points:")
            for belief in creator['philosophy']['core_beliefs'][:3]:
                print(f"  - {belief}")

            # Content sources summary
            sources = creator.get('content_sources', {})
            print("\nContent Sources:")

            if 'podcast' in sources:
                p = sources['podcast']
                print(f"  Podcast: {p['name']}")
                print(f"    URL: {p.get('url', 'N/A')}")

            if 'podcasts' in sources:
                for p in sources['podcasts']:
                    print(f"  Podcast: {p['name']}")

            if 'books' in sources:
                print(f"  Books: {len(sources['books'])} titles")
                latest = max(sources['books'], key=lambda x: x.get('year', 0))
                print(f"    Latest: '{latest['title']}' ({latest['year']})")

            if 'blog' in sources:
                print(f"  Blog: {sources['blog'].get('url', 'Available')}")

            if 'newsletter' in sources:
                print(f"  Newsletter: {sources['newsletter'].get('name', 'Available')}")


def interactive_mode(monitor: CreatorContentMonitor) -> None:
    """Run the monitor in interactive mode."""
    print("\n" + "="*60)
    print("CREATOR CONTENT MONITOR - INTERACTIVE MODE")
    print("="*60)
    print("\nCommands:")
    print("  list          - List all creators")
    print("  profile NAME  - Show detailed creator profile")
    print("  ask QUESTION  - Get predicted responses from all creators")
    print("  ask NAME: Q   - Get predicted response from specific creator")
    print("  latest        - Show latest content (requires internet)")
    print("  books TOPIC   - Get book recommendations on a topic")
    print("  compare TOPIC - Compare philosophies on a topic")
    print("  report        - Generate full summary report")
    print("  help          - Show this help message")
    print("  quit          - Exit")
    print()

    while True:
        try:
            user_input = input("\n> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        parts = user_input.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if command == 'quit' or command == 'exit':
            print("Goodbye!")
            break
        elif command == 'list':
            monitor.list_creators()
        elif command == 'profile':
            if args:
                monitor.show_creator_profile(args)
            else:
                print("Usage: profile NAME")
        elif command == 'ask':
            if ':' in args:
                name, question = args.split(':', 1)
                monitor.predict_response(question.strip(), name.strip())
            elif args:
                monitor.predict_response(args)
            else:
                print("Usage: ask QUESTION or ask NAME: QUESTION")
        elif command == 'latest':
            days = int(args) if args.isdigit() else 7
            monitor.fetch_latest_content(days)
        elif command == 'books':
            if args:
                monitor.get_book_recommendations(args)
            else:
                print("Usage: books TOPIC")
        elif command == 'compare':
            if args:
                monitor.compare_philosophies(args)
            else:
                print("Usage: compare TOPIC")
        elif command == 'report':
            monitor.generate_summary_report()
        elif command == 'help':
            print("\nCommands:")
            print("  list          - List all creators")
            print("  profile NAME  - Show detailed creator profile")
            print("  ask QUESTION  - Get predicted responses from all creators")
            print("  ask NAME: Q   - Get predicted response from specific creator")
            print("  latest [DAYS] - Show latest content")
            print("  books TOPIC   - Get book recommendations")
            print("  compare TOPIC - Compare philosophies")
            print("  report        - Generate summary report")
            print("  quit          - Exit")
        else:
            print(f"Unknown command: {command}. Type 'help' for commands.")


def main():
    parser = argparse.ArgumentParser(
        description="Monitor content creators and predict their responses"
    )
    parser.add_argument(
        '--config', '-c',
        default='creators.json',
        help='Path to creators config file'
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List all creators'
    )
    parser.add_argument(
        '--profile', '-p',
        metavar='NAME',
        help='Show profile for a creator'
    )
    parser.add_argument(
        '--ask', '-a',
        metavar='QUESTION',
        help='Get predicted responses to a question'
    )
    parser.add_argument(
        '--creator',
        metavar='NAME',
        help='Specify creator for --ask'
    )
    parser.add_argument(
        '--latest',
        type=int,
        nargs='?',
        const=7,
        metavar='DAYS',
        help='Fetch latest content (default: 7 days)'
    )
    parser.add_argument(
        '--books',
        metavar='TOPIC',
        help='Get book recommendations on a topic'
    )
    parser.add_argument(
        '--compare',
        metavar='TOPIC',
        help='Compare creator philosophies on a topic'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate full summary report'
    )
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )

    args = parser.parse_args()

    # Find config file
    config_path = Path(args.config)
    if not config_path.exists():
        # Try looking in script directory
        script_dir = Path(__file__).parent
        config_path = script_dir / args.config

    try:
        monitor = CreatorContentMonitor(str(config_path))
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    # Handle commands
    if args.interactive:
        interactive_mode(monitor)
    elif args.list:
        monitor.list_creators()
    elif args.profile:
        monitor.show_creator_profile(args.profile)
    elif args.ask:
        monitor.predict_response(args.ask, args.creator)
    elif args.latest is not None:
        monitor.fetch_latest_content(args.latest)
    elif args.books:
        monitor.get_book_recommendations(args.books)
    elif args.compare:
        monitor.compare_philosophies(args.compare)
    elif args.report:
        monitor.generate_summary_report()
    else:
        # Default to interactive mode if no args
        interactive_mode(monitor)

    return 0


if __name__ == '__main__':
    exit(main())

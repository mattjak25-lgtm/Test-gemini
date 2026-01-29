# Creator Content Monitor

A system to monitor content from thought leaders and predict their likely responses to your questions based on their philosophies and published content.

## Monitored Creators

| Creator | Focus | Key Concepts |
|---------|-------|--------------|
| **James Altucher** | Entrepreneurship & Self-Reliance | 10 Ideas a Day, Choose Yourself, Skip the Line |
| **Martha Beck** | Life Coaching & Integrity | Way of Integrity, Wayfinder, Essential Self |
| **Tim Ferriss** | Lifestyle Design & Optimization | Fear-Setting, 4-Hour Framework, Minimum Effective Dose |
| **Itamar Marani** | Elite Performance & Mindset | Internal Drag, Performance Ceilings, Identity Evolution |

---

## Quick Start

### Option 1: Direct Usage (No Installation)
```bash
# Ask all creators
python content_monitor.py --ask "How do I overcome fear?"

# Ask specific creator
python content_monitor.py --ask "Should I start a business?" --creator Tim

# Interactive mode
python content_monitor.py
```

### Option 2: Install as Package
```bash
pip install -e .

# Now use from anywhere
creator-monitor --ask "How do I find my purpose?"
ask-creators "What about fear of failure?"
```

### Option 3: Run as API Server
```bash
pip install flask
python creator_api.py

# Query via HTTP
curl "http://localhost:5000/ask?q=How+do+I+overcome+fear"
```

---

## Installation Options

### Basic (CLI only)
```bash
git clone <repo>
cd creator-monitor
# No dependencies needed for core features
```

### With RSS Feed Monitoring
```bash
pip install feedparser requests
# or
pip install -e ".[rss]"
```

### With API Server
```bash
pip install flask
# or
pip install -e ".[api]"
```

### Everything
```bash
pip install -e ".[all]"
```

---

## Usage Methods

### 1. Command Line Interface

```bash
# List creators
python content_monitor.py --list

# Show creator profile
python content_monitor.py --profile "Martha Beck"

# Ask a question (all respond)
python content_monitor.py --ask "How should I handle career change?"

# Ask specific creator
python content_monitor.py --ask "How do I scale my business?" --creator Itamar

# Get book recommendations
python content_monitor.py --books productivity

# Compare philosophies
python content_monitor.py --compare fear

# Latest podcast episodes (requires feedparser)
python content_monitor.py --latest 7

# Full report
python content_monitor.py --report
```

### 2. Interactive Mode

```bash
python content_monitor.py
```

Commands:
| Command | Description |
|---------|-------------|
| `list` | List all creators |
| `profile NAME` | Show detailed creator profile |
| `ask QUESTION` | Get responses from all creators |
| `ask NAME: QUESTION` | Get response from specific creator |
| `books TOPIC` | Book recommendations |
| `compare TOPIC` | Compare philosophies |
| `latest [DAYS]` | Recent content |
| `report` | Full summary |
| `quit` | Exit |

### 3. Python Library

```python
from content_monitor import CreatorContentMonitor, get_response_data

# Get structured response data
result = get_response_data("How do I overcome fear?")
print(result['responses'][0]['response'])

# Or use the monitor directly
monitor = CreatorContentMonitor("creators.json")
creator = monitor.get_creator("Tim Ferriss")
print(creator['philosophy']['core_beliefs'])
```

### 4. REST API Server

```bash
python creator_api.py --port 5000
```

**Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info and help |
| `/creators` | GET | List all creators |
| `/creators/<name>` | GET | Get creator profile |
| `/ask` | POST | Ask question (JSON body) |
| `/ask?q=...` | GET | Quick ask via query param |
| `/books/<topic>` | GET | Book recommendations |
| `/compare/<topic>` | GET | Compare philosophies |

**Examples:**

```bash
# List creators
curl http://localhost:5000/creators

# Ask a question (GET)
curl "http://localhost:5000/ask?q=How+do+I+overcome+fear"

# Ask a question (POST)
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Should I quit my job?", "creator": "James"}'

# Get book recommendations
curl http://localhost:5000/books/productivity

# Compare philosophies
curl http://localhost:5000/compare/fear
```

### 5. Shell Script

```bash
# Quick ask from terminal
./ask "How do I find my purpose?"
./ask "Handle stress better" --creator Itamar
```

---

## Example Questions

**Career & Business:**
- "Should I quit my job to start a business?"
- "How do I scale from 6 to 7 figures?"
- "What should I do about a career transition?"

**Fear & Anxiety:**
- "How do I overcome fear of failure?"
- "How do I handle anxiety about the future?"
- "What if I'm too scared to take risks?"

**Purpose & Meaning:**
- "How do I find my life's purpose?"
- "What should I do if I feel stuck?"
- "How do I know if I'm on the right path?"

**Productivity & Performance:**
- "What's the key to productivity?"
- "How do I perform better under pressure?"
- "How do I learn new skills faster?"

---

## How It Works

### Response Prediction Pipeline

1. **Question Analysis** - Your question is categorized by topic (career, fear, business, etc.)

2. **Philosophy Lookup** - Each creator's documented philosophy is searched for relevant responses

3. **Response Generation** - Matching responses or core beliefs are returned

4. **Concept Tagging** - Relevant signature concepts are highlighted

### Supported Categories

- `career_advice` - Jobs, work, profession
- `fear` - Fear, anxiety, worry
- `money` - Income, wealth, finances
- `starting_business` - Entrepreneurship, startups
- `scaling_business` - Growth, expansion
- `productivity` - Efficiency, time management
- `learning_skills` - Education, mastery
- `failure` - Mistakes, setbacks
- `life_purpose` - Meaning, direction
- `relationships` - Connections, family
- `self_doubt` - Confidence, imposter syndrome
- `stress` - Pressure, burnout
- `decision_making` - Choices, options

---

## Customization

### Adding New Creators

Edit `creators.json`:

```json
{
  "name": "New Creator",
  "slug": "new-creator",
  "tagline": "Their specialty",
  "philosophy": {
    "core_beliefs": ["Belief 1", "Belief 2"],
    "likely_responses": {
      "fear": "Their typical advice on fear...",
      "career_advice": "Their career guidance..."
    }
  },
  "content_sources": {
    "podcast": {"name": "Podcast Name", "url": "..."},
    "books": [{"title": "Book", "year": 2024, "key_themes": [...]}]
  },
  "signature_concepts": ["Concept 1", "Concept 2"]
}
```

### Adding Response Categories

In `content_monitor.py`, update `_categorize_question()`:

```python
categories = {
    'new_category': ['keyword1', 'keyword2'],
    ...
}
```

Then add corresponding `likely_responses` in `creators.json`.

---

## File Structure

```
.
├── content_monitor.py   # Main CLI application
├── creator_api.py       # REST API server
├── creators.json        # Creator profiles & philosophies
├── setup.py            # Package installation
├── requirements.txt    # Python dependencies
├── ask                 # Shell wrapper script
└── README.md          # This documentation
```

---

## Content Sources

Each creator profile includes links to:

- **Podcasts** - With RSS feeds for automatic monitoring
- **Books** - Catalog with themes and summaries
- **Blogs/Websites** - Direct links
- **Newsletters** - Subscription info
- **Coaching/Courses** - Training programs

Use `--latest` to fetch recent podcast episodes (requires `feedparser`).

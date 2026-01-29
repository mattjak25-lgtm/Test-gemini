# Creator Content Monitor

A system to monitor content from thought leaders and predict their likely responses to your questions based on their philosophies and published content.

## Monitored Creators

1. **James Altucher** - Choose Yourself Pioneer & Serial Entrepreneur
   - Podcast: The James Altucher Show
   - Key concepts: 10 Ideas a Day, Choose Yourself, Skip the Line

2. **Martha Beck** - Harvard-trained Sociologist & Life Coach Pioneer
   - Podcasts: The Gathering Room, Bewildered
   - Key concepts: Way of Integrity, Wayfinder, Essential Self vs Social Self

3. **Tim Ferriss** - Author, Investor & Human Guinea Pig
   - Podcast: The Tim Ferriss Show (1B+ downloads)
   - Key concepts: 4-Hour Framework, Fear-Setting, Lifestyle Design

4. **Itamar Marani** - Ex-Special Forces Tactical Mental Performance Coach
   - Podcast: The Elite Performance Podcast
   - Key concepts: Internal Drag, Performance Ceilings, Identity Evolution

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Interactive Mode (default)
```bash
python content_monitor.py
```

### Command Line Options

```bash
# List all creators
python content_monitor.py --list

# Show creator profile
python content_monitor.py --profile "Tim Ferriss"

# Ask a question (all creators respond)
python content_monitor.py --ask "How do I overcome fear of starting a business?"

# Ask a specific creator
python content_monitor.py --ask "How do I handle stress?" --creator "Itamar"

# Get latest podcast episodes
python content_monitor.py --latest 7

# Get book recommendations
python content_monitor.py --books "productivity"

# Compare philosophies on a topic
python content_monitor.py --compare "fear"

# Generate full report
python content_monitor.py --report
```

### Interactive Commands

| Command | Description |
|---------|-------------|
| `list` | List all creators |
| `profile NAME` | Show detailed creator profile |
| `ask QUESTION` | Get predicted responses from all creators |
| `ask NAME: Q` | Get predicted response from specific creator |
| `latest [DAYS]` | Show latest content (requires internet) |
| `books TOPIC` | Get book recommendations on a topic |
| `compare TOPIC` | Compare philosophies on a topic |
| `report` | Generate full summary report |
| `help` | Show help message |
| `quit` | Exit |

## Example Questions to Ask

- "How should I handle a career transition?"
- "What's the best way to overcome fear of failure?"
- "How do I find my life's purpose?"
- "Should I start my own business?"
- "How do I deal with anxiety about the future?"
- "What's the key to productivity?"
- "How do I scale my business to the next level?"

## How Response Prediction Works

The system categorizes your question and matches it against each creator's documented philosophy:

1. **Question Categorization**: Your question is analyzed for key themes (career, fear, anxiety, business, etc.)

2. **Philosophy Matching**: The system looks up the creator's likely response patterns for that category

3. **Core Beliefs Integration**: If no direct match, responses are generated from the creator's core beliefs

4. **Signature Concepts**: Relevant concepts from each creator are highlighted

## Content Sources Tracked

- **Podcasts**: RSS feeds for automatic episode monitoring
- **Books**: Full catalog with themes and summaries
- **Blogs**: Links to creator blogs and archives
- **Newsletters**: Subscription information
- **Courses/Programs**: Coaching and training offerings

## Customization

Edit `creators.json` to:
- Add new creators
- Update philosophies and likely responses
- Add new content sources
- Modify response categories

## File Structure

```
.
├── content_monitor.py   # Main application
├── creators.json        # Creator profiles and configuration
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

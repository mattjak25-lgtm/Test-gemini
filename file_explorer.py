"""
File Explorer Agent — Beginner's Guide to Agentic Workflows
===========================================================

This agent uses Claude and the Agent SDK to explore files in any directory.
Claude has access to built-in tools:
  - Read  → read the contents of a file
  - Glob  → find files by pattern (e.g. "**/*.py")
  - Grep  → search file contents for a keyword

How it works (the "agentic loop"):
  1. You give Claude a task in plain English
  2. Claude decides which tools to call and in what order
  3. Each tool result feeds back to Claude
  4. Claude keeps going until it has a complete answer

Usage:
  python3 file_explorer.py
  python3 file_explorer.py "find all Python files and summarize what they do"
"""

import anyio
import sys
import os

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, AssistantMessage


async def explore(prompt: str, directory: str) -> None:
    """Run the file explorer agent with the given prompt."""

    print(f"\n Working directory: {directory}")
    print(f" Task: {prompt}")
    print("-" * 50)

    # Configure the agent:
    #   - cwd: the directory Claude will work in
    #   - allowed_tools: which built-in tools Claude can use
    #   - max_turns: safety limit so it doesn't run forever
    options = ClaudeAgentOptions(
        cwd=directory,
        allowed_tools=["Read", "Glob", "Grep"],
        max_turns=10,
    )

    # query() runs the agentic loop — Claude decides how many tool
    # calls to make before returning a final answer.
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, ResultMessage):
            # This is Claude's final answer
            print("\n Claude's answer:")
            print(message.result)
        elif isinstance(message, AssistantMessage):
            # Intermediate messages show Claude's reasoning steps
            # (optional — comment out if you want less output)
            for block in message.content:
                if hasattr(block, "type") and block.type == "tool_use":
                    print(f"  → using tool: {block.name}")


def main() -> None:
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.")
        print("Get your key at https://console.anthropic.com")
        print("Then run:  export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    # Default task if none provided on the command line
    default_prompt = (
        "Look at the files in this directory. "
        "Tell me what's here and give a one-line description of each file."
    )
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else default_prompt

    # Run the agent in the current directory (or change to any path you like)
    directory = os.getcwd()

    anyio.run(explore, prompt, directory)


if __name__ == "__main__":
    main()

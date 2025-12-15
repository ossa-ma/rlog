# rlog

A frictionless, public reading log manager that lives in your keyboard.

**rlog** (reading log) is a publicly shareable record of everything you read online. It's designed for developers and writers who want to track and share their reading on their personal blogs without the friction of traditional reading trackers.

## What's a rlog?

A rlog is like a commit history for your reading. It tracks articles, posts, discussions, and everything else you consume online. The log lives on your blog (e.g., `ossa-ma.github.io/reading`) as a simple, portable JSON file.

**Why does this matter?**

- **Knowledge Sharing**: Readers of your blog can see what shaped your thinking. `example.com/reading` ← Share your intellectual journey.
- **Discovery and Community**: A recommendation system without the data harvesting and algorithms. 
- **Research Trails**: Never lose a reference. Every article is catalogued with metadata, dates, and optional notes.
- **Rabbit Hole Documentation**: Track your 3am deep-dives. See what research sessions led where.
- **Citation Machine**: All your sources are already logged with proper metadata—dates, authors, titles.
- **AI Context Building**: Score articles by usefulness. Let agents mine your reading log to build personalized knowledge bases.
- **Logging Things Feels Nice**: You want to feel productive, you want to comment on an article, you may want to run some analysis on things you've read, Reading Wrapped maybe? Whats one more thing to micromanage.


## Features

- **Smart Browser Integration**: Automatically detects and fetches the URL from your active browser tab.
  - **Chrome**: Full support for multiple profiles using JXA.
  - **Safari**: Native AppleScript support.
  - **Firefox**: Advanced session reading to capture all tabs.
  - **Clipboard Fallback**: If no browser is detected, seamlessly grabs the URL from your clipboard.
- **Log Read**: Instantly add the current article to your 'read' history (`reading.json`).
- **Read Later**: Save articles to your private queue (`reading_list.json`).
- **Log Window**: Bulk-save **all open tabs** in the active window to your public history.
- **Read Window Later**: Bulk-save **all open tabs** to your private queue.
- **Auto-Metadata**: Fetches Title, Author, and Date from the URL automatically.
- **Comments**: Add notes and thoughts to any logged article.
- **View Read Log**: Open a window showing your reading history (`reading.json`).
- **View Reading List**: Open a window showing your saved “read later” items (`reading_list.json`).
- **Open Random Article**: Open a random article from your reading list in the browser.
- **Blog Setup**: One-click setup to inject the reading list page into your Next.js app.
- **Git Integration**: Optionally commit and push changes to your blog's repository immediately.

## Prerequisites

- [Raycast](https://www.raycast.com/) (macOS)
- A static blog (Next.js recommended for auto-setup, but any static site works)
- Node.js installed

## Installation

Install directly from the [Raycast Store](https://raycast.com/extensions).

Alternatively:
1. Clone this repository.
2. Run `npm install`.
3. Run `npm run dev` to start the development server.
4. Open Raycast and search for "rlog".

## Configuration

Go to Raycast Preferences → Extensions → rlog, then set:
- **Blog Repository Path**: Absolute path to your blog repo (e.g., `/Users/you/projects/my-blog`).
- **Data File Path**: Relative path to the JSON file for your main reading log (default: `data/reading.json`).
  - Note: The "Read Later" list is always saved to `data/reading_list.json` in the same directory as your main log.

## Usage

### Log Read
1. Have an article open in your browser.
2. Open Raycast (`Option+Space`).
3. Run "Log Read".
4. The URL is fetched, metadata extracted, and you can add thoughts before saving.

### Read Later
1. Run "Read Later" to instantly save the current tab to your private queue.

### Log Window / Read Window Later
1. Have a window full of research tabs open.
2. Run "Log Window" to save them all to your history, or "Read Window Later" to queue them up.
3. Works across Chrome, Safari, and Firefox.

### Setup rlog
Run "Setup rlog" to automatically create the `data/reading.json` file and inject a basic `/reading` page into your Next.js project at `app/reading/page.tsx`.

## Privacy

rlog is **local-first and privacy-focused**:
- All data (`reading.json`, `reading_list.json`) is stored locally on your machine.
- No data is sent to external servers (unless you use "Push to Git", which sends to *your* repo).
- Browser automation runs entirely on your machine.

## Data Format

Your `reading.json` is simple, portable JSON:

```json
[
  {
    "url": "https://example.com/article",
    "title": "How to Build Better Software",
    "author": "John Developer",
    "publishedDate": "2025-12-10",
    "dateRead": "2025-12-14T10:30:00Z",
    "thoughts": "Great insights on testing strategies"
  }
]
```

Use it however you want—build your own display page, analyze it, feed it to LLMs, whatever.

## Troubleshooting

- **"No valid tabs found"**: Ensure you have Chrome, Safari, or Firefox open and active.
- **Firefox Issues**: Ensure you have a default profile set up. rlog reads from the default profile's session store.
- **Permissions**: Raycast may ask for permission to control your browser or System Events. You must allow this.

## Manual Usage / Scripting

Don't want to use Raycast? The core logic is standard Node.js:

1. **Fetch Metadata**: Use `src/utils/metadata.ts` in your own scripts.
2. **Browser Automation**: `src/utils/browser.ts` contains JXA/AppleScript logic. Run directly with `osascript`.
3. **Data Format**: Write to `reading.json` from any source—CLI tools, other extensions, custom scripts.

## Roadmap

- [ ] Browser extension (Chrome, Firefox, Edge)
- [ ] Mobile share targets (iOS/Android)
- [ ] Reading habits heatmap
- [ ] AI-powered summaries and insights (Pro tier)
- [ ] Cloud sync for cross-device access (Pro tier)

## Contributing

Pull requests welcome! This is early-stage—lots of room for improvements. Check [issues](https://github.com/ossa-ma/rlog/issues) for ideas.

## License

MIT

---

**Built by [@ossa-ma](https://github.com/ossa-ma)** | [Blog](https://ossa-ma.github.io/blog) | [Reading Log](https://ossa-ma.github.io/reading)
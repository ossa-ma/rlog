# rlog

A frictionless reading log manager that lives in your keyboard.

## Why a reading log is so important

- **Knowledge Sharing**: Someone comes across your blog, respects your opinions, wants to know what you read to be so informed and intelligent (look at you!). How did they do this? example.com/reading <- It's that easy!
We inject (scary word) the reading list page into your (currently only supporting) Next.js app, but you can handle this yourself if you want, all you need is a `reading.json`!
- **Keeping Track**: Reading management, developers lose track of what they read.
- **Logging Things Feels Nice**: You want to feel productive, you want to comment on a post, you may want to run some analysis on things you've read, Reading Wrapped maybe? Another thing to micromanage, who isn't micromanaging everything these days!
- **Research and References**: Tracking everything (or nearly everything) you've ever read will ensure you never lose references and can easily and accurately cite source materials. A wise man once said 'A research trail is as important as the outcome of the research'. I said that. Just now.
- **Rabbit holes**: How fun is it to see what rabbit holes someone went down one particular night?
- **Context Engineering**: Build an extension to score items in your reading list by usefulness, have an agent iterate through, categorise them, determine whether they should be added to your existing context or memory by default!
For example you read a new post on 'How to decrease freq of lambda cold starts', you found this useful, give it a score of 10. Your agent can look at your reading log and extract that information in your personal 'Serverless Best Practices' that another agent then uses to help you!


## Features

- **Smart Browser Integration**: Automatically detects and fetches the URL from your active browser tab.
  - **Chrome**: Full support for multiple profiles using JXA.
  - **Safari**: Native AppleScript support.
  - **Firefox**: Advanced session reading to capture all tabs.
  - **Clipboard Fallback**: If no browser is detected, it seamlessly grabs the URL from your clipboard.
- **Log Read**: Instantly add the current article to your 'read' history (`reading.json`).
- **Comments**: Can add comments related to reading item.
- **Read Later**: A reading list, but convenient! And portable! Save the current tab to your private queue (`reading_list.json`).
- **Log Window**: Bulk-save **all open tabs** in the active window to your public history.
- **Read Window Later**: Bulk-save **all open tabs** in the active window to your private queue.
- **Auto-Metadata**: Fetches Title, Author, and Date from the URL automatically.
- **Blog Setup**: One-click setup to inject the reading list page into your Next.js app.
- **Git Integration**: Optionally commit and push changes to your blog's repository immediately.

## Prerequisites

- [Raycast](https://www.raycast.com/)
- A static blog (Next.js recommended for the auto-setup feature)
- Node.js installed

## Installation

1. Clone this repository.
2. Run `npm install`.
3. Run `npm run dev` to start the development server.
4. Open Raycast and search for "rlog".

## Configuration

Go to Raycast Preferences -> Extensions -> rlog then set:
- **Blog Repository Path**: The absolute path to your local blog repository (e.g., `/Users/you/projects/my-blog`).
- **Data File Path**: Relative path to the JSON file (default: `data/reading.json`).

## Usage

0. Open Raycast (`option + Space`).

### Log Read
1. Have an article open.
2. Run "Log Read".
3. The URL is fetched, metadata extracted, and you can add thoughts before saving.

### Read Later
1. Run "Read Later" to instantly save the current tab to your private queue.

### Log Window / Read Window Later
1. Have a window full of research tabs open.
2. Run "Log Window" to save them all to your history, or "Read Window Later" to queue them up.
3. Works across Chrome, Safari, and Firefox.

### Setup rlog
Run "Setup rlog" to automatically create the `data/reading.json` file and a basic `app/reading/page.tsx` page in your Next.js project.

## Privacy

rlog is designed to be **local-first and privacy-focused**.
- All data (`reading.json`, `reading_list.json`) is stored locally on your machine in your specified blog repository.
- No data is sent to any external server (unless you explicitly use the "Push to Git" feature, which sends it to your own repository).
- Browser automation runs locally on your machine.

## Troubleshooting

- **"No valid tabs found"**: Ensure you have a supported browser (Chrome, Safari, Firefox) open and active.
- **Firefox Issues**: If Firefox tabs aren't being detected, ensure you have a default profile set up. rlog reads from the default profile's session store.
- **Permissions**: Raycast may ask for permission to control your browser or System Events. You must allow this for the extension to work.

## Manual Usage / Scripting

If you prefer not to use Raycast, you can still use the core logic! The project is built with standard Node.js scripts.

1.  **Fetch Metadata**: You can use `src/utils/metadata.ts` in your own scripts to fetch title/author/date from any URL.
2.  **Browser Automation**: `src/utils/browser.ts` contains the JXA/AppleScript logic to fetch URLs from Chrome, Safari, and Firefox. You can run these snippets directly in your terminal using `osascript`.
3.  **Data Format**: The `reading.json` format is simple JSON. You can write your own scripts to append to it from any source (CLI, other extensions, etc.).

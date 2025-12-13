# rlog

A frictionless reading log manager for static blogs, built as a Raycast Extension.

## Why a reading log is so important

- **Knowledge Sharing**: Someone comes across your blog, respects your opinions, wants to know what you read to be so informed and intelligent (look at you!), how did they do this before? Impossible unless they go on your substack subscribed or whatever idk I don't use substack maybe you don't use it either. Now? example.com/reading <- It's that easy! We literally inject (scary word) the reading list page into your (currently only supporting) Next.js app, but you can handle this yourself if you want, all you need is a `reading.json`!
- **Logging Things Feels Nice**: You want to feel productive, you want to comment on a post, you may want to run some analysis on things you've read, Reading Wrapped maybe? Another thing to micromanage, who isn't micromanaging everything these days!
- **Research and References**: Tracking everything (or nearly everything) you've ever read will ensure you never lose references and can easily and accurately cite source materials. A wise man once said 'A research trail is as important as the outcome of the research'. I said that. Just now.
- **Rabbit holes**: How fun is it to see what rabbit holes someone went down one particular night?
- **Context Engineering**: Build an extension to score items in your reading list by usefulness, have an agent iterate through, categorise them, determine whether they should be added to your 'Second Brain' by default! E.g. you read a new post on 'How to decrease freq of lambda cold starts', you found this useful, give it a score of 10. Your agent can scrape your reading log and extract that information in your personal 'Serverless Best Practices' that another agent then uses to help you!

## Features

- **Smart Browser Integration**: Automatically detects and fetches the URL from your active browser tab.
  - **Chrome**: Full support for multiple profiles using JXA.
  - **Safari & Firefox**: Native AppleScript support.
  - **Clipboard Fallback**: If no browser is detected, it seamlessly grabs the URL from your clipboard.
- **Log Read**: Instantly add articles/pages/posts you've read to your 'read' list.
- **Auto-Metadata**: Automatically fetches Title, Author, and Date from the URL. Can add comments related to reading item.
- **Git Integration**: Optionally commit and push changes to your blog's repository immediately.
- **Blog Setup**: One-click setup to inject the reading list page into your Next.js app.
- **Read Later**: A reading list, but convenient! And portable!

## Prerequisites

- [Raycast](https://www.raycast.com/)
- A static blog (Next.js recommended)
- Node.js installed

## Installation

1. Clone this repository.
2. Run `npm install`.
3. Run `npm run dev` to start the development server.
4. Open Raycast and search for "Log Read".

## Configuration

Go to Raycast Preferences -> Extensions -> rlog and set:
- **Blog Repository Path**: The absolute path to your local blog repository (e.g., `/Users/you/projects/my-blog`).
- **Data File Path**: Relative path to the JSON file (default: `data/reading.json`).

## Usage

### Log Read (`Cmd + R`)
1. Have an article open in Chrome, Safari, or Firefox (or copy a URL).
2. Open Raycast and run "Log Read".
3. The URL field will auto-populate from your active browser tab.
4. Add your thoughts (optional).
5. Check "Push to Git" if you want to deploy immediately.

### Setup Blog
Run "Setup Blog" to automatically create the `data/reading.json` file and a basic `app/reading/page.tsx` page in your Next.js project.

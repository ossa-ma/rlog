# RLog (Reading Log)

A frictionless reading log manager for static blogs, built as a Raycast Extension.

## Features

- **Add Reading**: Instantly add the current browser tab to your reading list.
- **Auto-Metadata**: Automatically fetches Title, Author, and Date from the URL.
- **Git Integration**: Optionally commit and push changes to your blog's repository immediately.
- **Blog Setup**: One-click setup to inject the reading list page into your Next.js app.

## Prerequisites

- [Raycast](https://www.raycast.com/)
- A static blog (Next.js recommended)
- Node.js installed

## Installation

1. Clone this repository.
2. Run `npm install`.
3. Run `npm run dev` to start the development server.
4. Open Raycast and search for "Add Reading".

## Configuration

Go to Raycast Preferences -> Extensions -> RLog and set:
- **Blog Repository Path**: The absolute path to your local blog repository (e.g., `/Users/you/projects/my-blog`).
- **Data File Path**: Relative path to the JSON file (default: `data/reading.json`).

## Usage

### Add Reading (`Cmd + R`)
1. Copy a URL or have it open in your browser.
2. Open Raycast and run "Add Reading".
3. Paste the URL (if not auto-detected).
4. Add your thoughts (optional).
5. Check "Push to Git" if you want to deploy immediately.

### Setup Blog
Run "Setup Blog" to automatically create the `data/reading.json` file and a basic `app/reading/page.tsx` page in your Next.js project.

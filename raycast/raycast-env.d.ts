/// <reference types="@raycast/api">

/* 🚧 🚧 🚧
 * This file is auto-generated from the extension's manifest.
 * Do not modify manually. Instead, update the `package.json` file.
 * 🚧 🚧 🚧 */

/* eslint-disable @typescript-eslint/ban-types */

type ExtensionPreferences = {
  /** Blog Repository Path - Absolute path to your static blog repository. Not needed for the Capture Read command. */
  "blogPath"?: string,
  /** Data File Path - Relative path to your reading.json file (default: data/reading.json). */
  "dataPath": string
}

/** Preferences accessible in all the extension's commands */
declare type Preferences = ExtensionPreferences

declare namespace Preferences {
  /** Preferences accessible in the `log-read` command */
  export type LogRead = ExtensionPreferences & {}
  /** Preferences accessible in the `capture` command */
  export type Capture = ExtensionPreferences & {
  /** Inbox File Path - Local JSONL file captures are appended to. */
  "inboxPath": string
}
  /** Preferences accessible in the `sync` command */
  export type Sync = ExtensionPreferences & {
  /** Inbox File Path - Fallback inbox file when no Finder item is selected. */
  "inboxPath": string,
  /** Auto Push - When enabled, sync commits and pushes reading.json to your blog repo. */
  "autoPush": boolean
}
  /** Preferences accessible in the `setup-rlog` command */
  export type SetupRlog = ExtensionPreferences & {}
  /** Preferences accessible in the `read-later` command */
  export type ReadLater = ExtensionPreferences & {}
  /** Preferences accessible in the `log-window` command */
  export type LogWindow = ExtensionPreferences & {}
  /** Preferences accessible in the `read-window-later` command */
  export type ReadWindowLater = ExtensionPreferences & {}
  /** Preferences accessible in the `view-read-log` command */
  export type ViewReadLog = ExtensionPreferences & {}
  /** Preferences accessible in the `view-reading-list` command */
  export type ViewReadingList = ExtensionPreferences & {}
  /** Preferences accessible in the `open-random-article` command */
  export type OpenRandomArticle = ExtensionPreferences & {}
}

declare namespace Arguments {
  /** Arguments passed to the `log-read` command */
  export type LogRead = {}
  /** Arguments passed to the `capture` command */
  export type Capture = {}
  /** Arguments passed to the `sync` command */
  export type Sync = {}
  /** Arguments passed to the `setup-rlog` command */
  export type SetupRlog = {}
  /** Arguments passed to the `read-later` command */
  export type ReadLater = {}
  /** Arguments passed to the `log-window` command */
  export type LogWindow = {}
  /** Arguments passed to the `read-window-later` command */
  export type ReadWindowLater = {}
  /** Arguments passed to the `view-read-log` command */
  export type ViewReadLog = {}
  /** Arguments passed to the `view-reading-list` command */
  export type ViewReadingList = {}
  /** Arguments passed to the `open-random-article` command */
  export type OpenRandomArticle = {}
}


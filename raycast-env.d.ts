/// <reference types="@raycast/api">

/* 🚧 🚧 🚧
 * This file is auto-generated from the extension's manifest.
 * Do not modify manually. Instead, update the `package.json` file.
 * 🚧 🚧 🚧 */

/* eslint-disable @typescript-eslint/ban-types */

type ExtensionPreferences = {
  /** Blog Repository Path - Absolute path to your static blog repository. */
  "blogPath": string,
  /** Data File Path - Relative path to your reading.json file (default: data/reading.json). */
  "dataPath": string
}

/** Preferences accessible in all the extension's commands */
declare type Preferences = ExtensionPreferences

declare namespace Preferences {
  /** Preferences accessible in the `log-read` command */
  export type LogRead = ExtensionPreferences & {}
  /** Preferences accessible in the `setup-blog` command */
  export type SetupBlog = ExtensionPreferences & {}
  /** Preferences accessible in the `read-later` command */
  export type ReadLater = ExtensionPreferences & {}
}

declare namespace Arguments {
  /** Arguments passed to the `log-read` command */
  export type LogRead = {}
  /** Arguments passed to the `setup-blog` command */
  export type SetupBlog = {}
  /** Arguments passed to the `read-later` command */
  export type ReadLater = {}
}


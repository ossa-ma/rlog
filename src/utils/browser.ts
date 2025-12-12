import { runAppleScript } from "@raycast/utils";
import { Clipboard } from "@raycast/api";

export async function getActiveUrl(): Promise<string | null> {
  console.log("Starting getActiveUrl...");

  // Try to get URL from the frontmost browser
  try {
    // First, detect which browser is currently active
    const frontmostApp = await runAppleScript(
      'tell application "System Events" to get name of first application process whose frontmost is true',
    );
    console.log("Frontmost app:", frontmostApp);

    let browserUrl = "";

    // Only query the active browser
    if (frontmostApp === "Google Chrome") {
      try {
        browserUrl = await runAppleScript(
          'Application("Google Chrome").windows[0].activeTab.url()',
          { language: "JavaScript" },
        );
        console.log("Chrome URL:", browserUrl);
      } catch (e) {
        console.log("Chrome error:", e);
      }
    } else if (frontmostApp === "Safari") {
      try {
        browserUrl = await runAppleScript(
          'tell application "Safari" to return URL of current tab of front window',
        );
        console.log("Safari URL:", browserUrl);
      } catch (e) {
        console.log("Safari error:", e);
      }
    } else if (frontmostApp === "Firefox") {
      try {
        browserUrl = await runAppleScript(
          'tell application "Firefox" to return URL of active tab of front window',
        );
        console.log("Firefox URL:", browserUrl);
      } catch (e) {
        console.log("Firefox error:", e);
      }
    } else {
      console.log("Frontmost app is not a supported browser:", frontmostApp);
    }

    if (
      browserUrl &&
      (browserUrl.startsWith("http") || browserUrl.startsWith("https"))
    ) {
      return browserUrl;
    }
  } catch (e) {
    console.error("Browser detection error:", e);
  }

  // Fallback to Clipboard
  try {
    const text = await Clipboard.readText();
    console.log("Clipboard content:", text);
    if (text && (text.startsWith("http://") || text.startsWith("https://"))) {
      return text;
    } else {
      console.log("Clipboard content is not a valid URL");
    }
  } catch (e) {
    console.error("Clipboard error:", e);
  }

  return null;
}

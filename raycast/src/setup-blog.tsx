import {
  Action,
  ActionPanel,
  Form,
  getPreferenceValues,
  showToast,
  Toast,
} from "@raycast/api";
import fs from "fs";
import path from "path";
import { useState } from "react";

interface Preferences {
  blogPath: string;
  dataPath: string;
}

const PAGE_TEMPLATE = `
import { promises as fs } from 'fs';
import path from 'path';

interface ReadingEntry {
  url: string;
  title: string;
  author: string | null;
  publishedDate: string | null;
  addedDate: string;
  thoughts?: string;
}

async function getReadings(): Promise<ReadingEntry[]> {
  const dataPath = path.join(process.cwd(), 'data', 'reading.json');
  try {
    const fileContent = await fs.readFile(dataPath, 'utf-8');
    return JSON.parse(fileContent);
  } catch (error) {
    return [];
  }
}

export default async function ReadingPage() {
  const readings = await getReadings();

  return (
    <div className="prose dark:prose-invert mx-auto max-w-2xl py-8">
      <h1 className="mb-8 text-3xl font-bold">Reading Log</h1>
      <div className="space-y-8">
        {readings.map((entry, index) => (
          <div key={index} className="border-b border-gray-200 dark:border-gray-800 pb-8 last:border-0">
            <h2 className="text-xl font-semibold mb-2">
              <a href={entry.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                {entry.title}
              </a>
            </h2>
            <div className="text-sm text-gray-500 mb-4">
              Added on {entry.addedDate} {entry.author && \`• by \${entry.author}\`}
            </div>
            {entry.thoughts && (
              <p className="text-gray-700 dark:text-gray-300 italic">
                "{entry.thoughts}"
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
`;

export default function Command() {
  const preferences = getPreferenceValues<Preferences>();
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit() {
    setIsLoading(true);
    const toast = await showToast({
      style: Toast.Style.Animated,
      title: "Setting up...",
    });

    try {
      const blogPath = preferences.blogPath;

      // 1. Create Data File
      const dataDir = path.join(blogPath, path.dirname(preferences.dataPath));
      const dataFile = path.join(blogPath, preferences.dataPath);

      if (!fs.existsSync(dataDir)) {
        fs.mkdirSync(dataDir, { recursive: true });
      }

      if (!fs.existsSync(dataFile)) {
        fs.writeFileSync(dataFile, "[]");
        toast.message = "Created data/reading.json";
      }

      // 2. Create Page File
      // Assuming Next.js App Router structure
      const pageDir = path.join(blogPath, "app", "reading");
      const pageFile = path.join(pageDir, "page.tsx");

      if (!fs.existsSync(pageDir)) {
        fs.mkdirSync(pageDir, { recursive: true });
      }

      if (!fs.existsSync(pageFile)) {
        fs.writeFileSync(pageFile, PAGE_TEMPLATE.trim());
        toast.style = Toast.Style.Success;
        toast.title = "Setup Complete!";
        toast.message = "Created app/reading/page.tsx";
      } else {
        toast.style = Toast.Style.Success;
        toast.title = "Already Setup";
        toast.message = "Files already exist.";
      }
    } catch (error) {
      toast.style = Toast.Style.Failure;
      toast.title = "Setup Failed";
      toast.message = String(error);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Form
      isLoading={isLoading}
      actions={
        <ActionPanel>
          <Action.SubmitForm title="Run Setup" onSubmit={handleSubmit} />
        </ActionPanel>
      }
    >
      <Form.Description text="This will create 'data/reading.json' and 'app/reading/page.tsx' in your blog repository if they don't exist." />
    </Form>
  );
}

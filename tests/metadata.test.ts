import { fetchMetadata } from "../src/utils/metadata";
import fetch from "node-fetch";

// Mock node-fetch
jest.mock("node-fetch");
const { Response } = jest.requireActual("node-fetch");

const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

describe("fetchMetadata", () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  it("extracts metadata from JSON-LD", async () => {
    const html = `
      <html>
        <head>
          <script type="application/ld+json">
            {
              "@type": "Article",
              "headline": "JSON-LD Title",
              "author": { "@type": "Person", "name": "JSON-LD Author" },
              "datePublished": "2023-01-01"
            }
          </script>
        </head>
      </html>
    `;
    mockFetch.mockResolvedValue(new Response(html));

    const metadata = await fetchMetadata("https://example.com");
    expect(metadata).toEqual({
      title: "JSON-LD Title",
      author: "JSON-LD Author",
      publishedDate: "2023-01-01",
    });
  });

  it("extracts metadata from Open Graph tags", async () => {
    const html = `
      <html>
        <head>
          <meta property="og:title" content="OG Title" />
          <meta property="og:author" content="OG Author" />
          <meta property="article:published_time" content="2023-02-02" />
        </head>
      </html>
    `;
    mockFetch.mockResolvedValue(new Response(html));

    const metadata = await fetchMetadata("https://example.com");
    expect(metadata).toEqual({
      title: "OG Title",
      author: "OG Author",
      publishedDate: "2023-02-02",
    });
  });

  it("handles Nabeel's blog structure (Title in H2)", async () => {
    const html = `
      <html>
        <head>
          <title>Nabeel S. Qureshi</title>
          <meta property="og:title" content="Nabeel S. Qureshi" />
        </head>
        <body>
          <h1>Nabeel S. Qureshi</h1>
          <h2>Reflections on Palantir</h2>
          <div class="content">
            Published: October 15, 2024
          </div>
        </body>
      </html>
    `;
    mockFetch.mockResolvedValue(new Response(html));

    const metadata = await fetchMetadata("https://nabeelqu.co/reflections");
    expect(metadata).toEqual({
      title: "Reflections on Palantir",
      author: null, // No author found in this snippet
      publishedDate: "2024-10-15",
    });
  });

  it("handles Charles' blog structure (Title in H1 with ID)", async () => {
    const html = `
      <html>
        <head>
          <title>Python Project Progression - Charles' Blog</title>
        </head>
        <body>
          <h1 class="menu-title">Charles' Blog</h1>
          <h1 id="python-project-progression">Python project progression</h1>
        </body>
      </html>
    `;
    mockFetch.mockResolvedValue(new Response(html));

    const metadata = await fetchMetadata("https://charles.gitlab-pages.computer.surgery/blog/python-project-progression.html");
    expect(metadata).toEqual({
      title: "Python project progression",
      author: null,
      publishedDate: null,
    });
  });

  it("extracts date from body text regex", async () => {
    const html = `
      <html>
        <body>
          <p>Some content...</p>
          <p>Published: December 25, 2024</p>
        </body>
      </html>
    `;
    mockFetch.mockResolvedValue(new Response(html));

    const metadata = await fetchMetadata("https://example.com");
    expect(metadata.publishedDate).toBe("2024-12-25");
  });

  it("returns default values on error", async () => {
    mockFetch.mockRejectedValue(new Error("Network error"));

    const metadata = await fetchMetadata("https://example.com");
    expect(metadata).toEqual({
      title: "Untitled",
      author: null,
      publishedDate: null,
    });
  });
});

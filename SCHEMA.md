# Reading Entry Schema - Single Source of Truth

**Based on the working Raycast implementation in `raycast/src/utils/utils.ts`**

This schema is used by:

- ✅ Raycast extension (reference implementation)
- ✅ Next.js blog (consumes this format)
- ⚠️ FastAPI backend (MUST match this)
- ⚠️ iOS app (MUST match this)

## ReadingEntry Interface

```typescript
interface ReadingEntry {
  url: string;
  title: string;
  author: string | null;
  publishedDate: string | null; // YYYY-MM-DD format
  addedDate: string; // YYYY-MM-DD format
  thoughts?: string; // Optional user notes
  rating?: number; // Optional 1-5 rating
}
```

## File Structure

`reading.json` is a **flat array** (JSON array at top level):

```json
[
  {
    "url": "https://example.com/article",
    "title": "Example Article",
    "author": "John Doe",
    "publishedDate": "2024-01-15",
    "addedDate": "2024-01-20",
    "thoughts": "Great read",
    "rating": 4
  }
]
```

**NOT a nested object like `{"entries": [...]}`**

## Field Requirements

### Required Fields

- `url`: string - Must be valid HTTP/HTTPS URL
- `title`: string - Article title (never empty)
- `author`: string | null - Use `null` if unknown (NOT empty string)
- `publishedDate`: string | null - YYYY-MM-DD format or `null`
- `addedDate`: string - Today's date in YYYY-MM-DD format

### Optional Fields

- `thoughts`: string - Omit key entirely if no thoughts (don't use empty string)
- `rating`: number - Omit key entirely if not rated

## Date Format Rules

**ALL dates MUST be YYYY-MM-DD strings:**

- ✅ `"2024-01-20"`
- ❌ `"2024-01-20T10:30:00Z"` (no timestamps)
- ❌ `"Invalid Date"` (use `null` instead)
- ❌ datetime objects (backend must convert to string)

## Implementation Rules

### For API (FastAPI)

1. **Field names MUST use camelCase** in JSON (not snake_case)
2. Use Pydantic `alias` to map Python snake_case → JSON camelCase
3. Serialize dates as `YYYY-MM-DD` strings (use `datetime.strftime("%Y-%m-%d")`)
4. Use `Optional[str]` for nullable fields, set to `None` not `""`
5. Serialize with `model_dump(by_alias=True, exclude_none=True)`

### For iOS (Swift)

1. Use exact field names (camelCase): `publishedDate`, `addedDate`
2. Dates are `String` type (not `Date` objects)
3. Use `Codable` for JSON serialization
4. Omit optional fields if `nil` when encoding

### For Raycast (TypeScript)

- **This is the reference implementation - don't change it**

## Metadata Extraction

Reference: `raycast/src/utils/metadata.ts`

Priority order for extraction (from Raycast):

**Title:**

1. JSON-LD `headline` or `name`
2. arXiv `h1.title`
3. `<meta name="citation_title">`
4. `<meta property="og:title">`
5. `<h1>` (filtered)
6. `<title>`

**Author:**

1. JSON-LD `author`
2. `<meta name="citation_author">` (academic papers)
3. `<meta name="author">`
4. Fallback to `null`

**Date:**

1. JSON-LD `datePublished`
2. `<meta name="citation_publication_date">`
3. `<meta property="article:published_time">`
4. `<time datetime>`
5. Fallback to `null`

**Always normalize to YYYY-MM-DD format. If parsing fails, use `null`.**

## DO NOT

- ❌ Use snake_case field names in JSON (API must use camelCase)
- ❌ Wrap the array in `{"entries": [...]}` (must be flat array)
- ❌ Use datetime objects or ISO 8601 timestamps
- ❌ Use empty strings for missing values (use `null` or omit)
- ❌ Return "Invalid Date" strings (use `null`)

## WHY This Schema

This schema works in production:

- Blog renders dates correctly from Raycast entries
- Raycast has robust metadata extraction
- Field names match JavaScript conventions (camelCase)
- Format is simple and portable

**If it ain't broke, don't fix it.**

# rlog API

Backend service for rlog - frictionless reading log management with GitHub integration.

## Features

### Free Tier (Current)
- GitHub OAuth authentication
- Reading log CRUD operations
- Automatic metadata extraction (title, author, date)
- Direct commit to user's GitHub repository
- Cross-platform support (browser extensions, mobile apps)

### Pro Tier (Future)
- AI-powered summaries (OpenAI integration)
- Semantic search (vector embeddings)
- Cross-device sync
- Analytics and insights

## Architecture

**Tech Stack:**
- FastAPI (async Python)
- Pydantic for validation
- aiohttp for async HTTP
- GitHub API for repository operations
- JWT authentication

**Design Principles:**
- Functional over class-based (following best practices)
- Async-first (non-blocking I/O)
- Flat project structure (no `src/`)
- Type-safe with comprehensive hints

## Project Structure

```
api/
├── main.py              # FastAPI application
├── config.py            # Environment configuration
├── routers/
│   ├── auth.py         # GitHub OAuth endpoints
│   ├── reading.py      # Reading log CRUD
│   └── health.py       # Health check
├── services/
│   ├── github.py       # GitHub API client
│   └── metadata.py     # URL metadata fetching
├── models/
│   ├── user.py         # User models
│   └── reading.py      # Reading entry models
├── middleware/
│   └── auth.py         # JWT authentication
└── pyproject.toml      # Dependencies (uv)
```

## Setup

### Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager
- GitHub OAuth App ([create one](https://github.com/settings/developers))

### Installation

1. **Sync dependencies with uv:**
```bash
cd api
uv sync
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your GitHub OAuth credentials
```

3. **Create GitHub OAuth App:**
   - Go to https://github.com/settings/developers
   - New OAuth App
   - **Authorization callback URL:** `http://localhost:8000/auth/callback`
   - Copy Client ID and Client Secret to `.env`

### Running Locally

**Quick start:**
```bash
./run.sh
```

**Or manually:**
```bash
uv run uvicorn main:app --reload
```

**Production mode (no reload):**
```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

API will be available at: http://localhost:8000

**Interactive docs:** http://localhost:8000/docs

## API Endpoints

### Authentication

**GET /auth/url**
- Get GitHub OAuth authorization URL
- Returns URL to redirect user for GitHub login

**GET /auth/callback?code={code}**
- GitHub OAuth callback
- Exchanges code for JWT access token
- Returns: `{ access_token, user }`

### Reading Log

**POST /reading/log** (requires auth)
```json
{
  "url": "https://example.com/article",
  "comment": "Great insights on async Python",
  "tags": ["python", "async"],
  "fetch_metadata": true
}
```

Plus repository config:
```json
{
  "owner": "ossama",
  "repo": "blog",
  "branch": "main",
  "reading_json_path": "data/reading.json"
}
```

**GET /reading/history?repo_owner=X&repo_name=Y** (requires auth)
- Fetch reading history from GitHub repo

### Health

**GET /health**
- Service health check
- Returns: `{ status: "healthy", environment: "development" }`

## Authentication Flow

1. **Client requests auth URL:**
   ```
   GET /auth/url
   → { auth_url: "https://github.com/login/oauth/authorize?..." }
   ```

2. **User authorizes on GitHub, redirected back:**
   ```
   GET /auth/callback?code=abc123
   → { access_token: "eyJ...", user: {...} }
   ```

3. **Client stores JWT and uses for authenticated requests:**
   ```
   POST /reading/log
   Authorization: Bearer eyJ...
   ```

## Usage Examples

### Browser Extension Integration

```javascript
// 1. Authenticate user
const authUrl = await fetch('http://localhost:8000/auth/url').then(r => r.json());
// Redirect user to authUrl.auth_url

// 2. After callback, store JWT
const { access_token } = await fetch(`http://localhost:8000/auth/callback?code=${code}`)
  .then(r => r.json());

chrome.storage.local.set({ jwt: access_token });

// 3. Log reading
const jwt = await chrome.storage.local.get('jwt');

await fetch('http://localhost:8000/reading/log', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${jwt}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    url: window.location.href,
    comment: 'Interesting article',
    tags: ['web'],
    fetch_metadata: true,
    // Repo config
    owner: 'ossama',
    repo: 'blog',
    branch: 'main',
    reading_json_path: 'data/reading.json'
  })
});
```

### Mobile App Integration

Same flow as browser extension - authenticate via OAuth, store JWT, make authenticated requests.

## Development

### Code Style
Following [development best practices](../blog/app/blog/posts/development-best-practices.mdx):
- Functional over class-based
- Async everywhere
- Comprehensive type hints
- Pydantic for validation

## Deployment

**Recommended platforms:**
- Railway (easiest)
- Fly.io (great free tier)
- Render (simple setup)

**Environment variables to set:**
- All variables from `.env.example`
- Set `ENVIRONMENT=production`
- Update `CORS_ORIGINS` with your frontend domain
- Update `GITHUB_REDIRECT_URI` with production URL

**Example Railway deployment:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

## Roadmap

- [ ] Browser extension (Chrome/Firefox/Safari)
- [ ] iOS Share Extension
- [ ] Android Share Target
- [ ] AI summarization (Pro tier)
- [ ] Semantic search with vector DB (Pro tier)
- [ ] Cross-device sync (Pro tier)
- [ ] Analytics dashboard (Pro tier)

## Contributing

This is the Free tier API - fully open source. Contributions welcome!

1. Fork the repo
2. Create feature branch
3. Follow code style (functional, async, typed)
4. Submit PR

## License

MIT License - see LICENSE file

---

**Questions?** Open an issue on [GitHub](https://github.com/ossama/rlog)

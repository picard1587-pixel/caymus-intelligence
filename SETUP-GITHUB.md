# GitHub Setup Instructions for Live RSS Feeds

## Overview
This setup uses GitHub Actions to automatically fetch RSS feeds every 3 hours and save them as JSON files. Your HTML page then loads these local JSON files - no CORS issues, no demo mode needed.

## Step-by-Step Setup

### 1. Create a GitHub Repository
1. Go to https://github.com/new
2. Name it something like `caymus-market-intelligence`
3. Set it to **Public** (required for GitHub Pages free hosting)
4. Click "Create repository"

### 2. Upload Your Files
You can do this via GitHub web interface or git:

**Option A: GitHub Web (easiest)**
1. Click "uploading an existing file" link on your new repo
2. Drag and drop these files/folders:
   - `news.html` (rename to `index.html` for default page)
   - `scripts/fetch-rss.js`
   - `.github/workflows/fetch-rss.yml`
   - Create empty folder `data/` (or upload a placeholder empty file)
3. Commit message: "Initial upload"

**Option B: Using Git (if you have git installed)**
```bash
cd "C:\Users\Picard\Projects\Caymus AI"
git init
git remote add origin https://github.com/YOUR_USERNAME/caymus-market-intelligence.git
git add news.html scripts/ .github/workflows/
git commit -m "Initial upload"
git push -u origin main
```

### 3. Enable GitHub Actions
1. Go to your repo → "Actions" tab
2. If you see "I understand my workflows..." button, click it
3. The workflow `fetch-rss.yml` should appear

### 4. Run the Workflow First Time
1. Go to "Actions" tab
2. Click "Fetch RSS Feeds" workflow
3. Click "Run workflow" → "Run workflow" (dropdown)
4. Wait 1-2 minutes for it to complete
5. Check the "data" folder now has `rss-feeds.json`

### 5. Enable GitHub Pages
1. Go to Settings → Pages (left sidebar)
2. Source: select "GitHub Actions"
3. The site will be at: `https://YOUR_USERNAME.github.io/caymus-market-intelligence/`

### 6. Access Your Live Site
- **Your URL:** `https://YOUR_USERNAME.github.io/caymus-market-intelligence/`
- The Market Intelligence section will show real RSS data
- Updates automatically every 3 hours via GitHub Actions

## How It Works

1. **GitHub Actions** runs `scripts/fetch-rss.js` every 3 hours
2. **Script** fetches all RSS feeds server-side (no CORS blocks)
3. **Script** categorizes articles by relevance (executive, funding, layoffs)
4. **JSON** saved to `data/rss-feeds.json` in your repo
5. **HTML** loads local JSON file with `fetch('data/rss-feeds.json')`
6. **Result:** Live data with timestamps, no proxies needed

## Troubleshooting

### Workflow Fails
- Check "Actions" tab for error messages
- Common issue: Feed URL changed or is down
- Edit `scripts/fetch-rss.js` to fix URLs

### Data Not Showing
- Check `data/rss-feeds.json` exists in your repo
- Check browser console (F12) for fetch errors
- Try refreshing the page

### Want More Feeds?
Edit `scripts/fetch-rss.js` → `RSS_FEEDS` object, add more feeds to any category:
```javascript
local: [
  ...existing feeds...
  { name: 'Your New Feed', url: 'https://example.com/feed/', source: 'example' }
]
```

## Files Summary
- `scripts/fetch-rss.js` - Fetches and parses RSS, saves JSON
- `.github/workflows/fetch-rss.yml` - Runs the script on schedule
- `data/rss-feeds.json` - Output file (auto-generated)
- `news.html` (rename to `index.html`) - Your dashboard page

## Optional: Custom Domain
1. Buy a domain (e.g., Namecheap, Google Domains)
2. Add DNS record: CNAME pointing to `YOUR_USERNAME.github.io`
3. In repo Settings → Pages, add your custom domain
4. Create `CNAME` file in repo with your domain name

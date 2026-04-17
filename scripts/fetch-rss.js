const https = require('https');
const fs = require('fs');
const path = require('path');
const xml2js = require('xml2js');

// RSS Feed Configuration - matching your HTML feeds
const RSS_FEEDS = {
  local: [
    { name: 'Startland News', url: 'https://www.startlandnews.com/feed/', source: 'startland' },
    { name: 'Silicon Prairie', url: 'https://siliconprairienews.com/feed/', source: 'siliconprairie' },
    { name: 'BizJournals KC', url: 'https://www.bizjournals.com/kansascity/inno/feed/rss/', source: 'bizjournals' },
    { name: 'Missouri Partnership', url: 'https://www.missouripartnership.com/feed/', source: 'missouripartnership' }
  ],
  executive: [
    { name: 'TechCrunch Executive', url: 'https://techcrunch.com/tag/executive-moves/feed/', source: 'techcrunch' },
    { name: 'TechCrunch Leadership', url: 'https://techcrunch.com/category/enterprise/feed/', source: 'techcrunch' }
  ],
  funding: [
    { name: 'TechCrunch Startups', url: 'https://techcrunch.com/startups/feed/', source: 'techcrunch' },
    { name: 'Crunchbase News', url: 'https://news.crunchbase.com/feed/', source: 'crunchbase' },
    { name: 'VentureBeat', url: 'https://venturebeat.com/feed/', source: 'venturebeat' }
  ],
  layoffs: [
    { name: 'TechCrunch Layoffs', url: 'https://techcrunch.com/tag/layoffs/feed/', source: 'techcrunch' },
    { name: 'TechCrunch TC', url: 'https://techcrunch.com/category/startups/feed/', source: 'techcrunch' }
  ]
};

// Keywords for filtering
const EXECUTIVE_KEYWORDS = ['ceo', 'cto', 'cio', 'chief', 'vp', 'vice president', 'executive', 'appointed', 'named', 'steps down', 'resigns', 'leadership'];
const FUNDING_KEYWORDS = ['series a', 'series b', 'series c', 'funding', 'raises', 'venture', 'investment', 'seed', 'acquisition'];
const LAYOFF_KEYWORDS = ['layoff', 'laid off', 'workforce reduction', 'job cuts', 'restructuring', 'furlough', 'downsizing'];

function fetchRSS(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

async function parseRSS(xmlText, sourceName, category) {
  const items = [];
  try {
    const parser = new xml2js.Parser({ explicitArray: false });
    const result = await parser.parseStringPromise(xmlText);

    const rssItems = result.rss?.channel?.item || [];
    const itemsArray = Array.isArray(rssItems) ? rssItems : [rssItems];

    for (const item of itemsArray.slice(0, 20)) {
      const title = item.title || '';
      const link = item.link || '';
      const description = item.description || '';
      const pubDate = item.pubDate || '';

      // Parse date
      let dateStr = '';
      try {
        const date = new Date(pubDate);
        if (!isNaN(date)) {
          dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        }
      } catch (e) {}

      // Check relevance
      const text = (title + ' ' + description).toLowerCase();
      let relevance = 'general';

      if (EXECUTIVE_KEYWORDS.some(kw => text.includes(kw))) relevance = 'executive';
      else if (FUNDING_KEYWORDS.some(kw => text.includes(kw))) relevance = 'funding';
      else if (LAYOFF_KEYWORDS.some(kw => text.includes(kw))) relevance = 'layoffs';

      items.push({
        title: title.trim(),
        link: link.trim(),
        description: description.trim().replace(/\u003c[^\u003e]+\u003e/g, '').substring(0, 200),
        date: dateStr,
        source: sourceName,
        category: category,
        relevance: relevance,
        fetched: new Date().toISOString()
      });
    }
  } catch (e) {
    console.error(`Error parsing RSS for ${sourceName}:`, e.message);
  }
  return items;
}

function categorizeArticles(allItems) {
  const result = {
    local: [],
    executive: [],
    funding: [],
    layoffs: []
  };

  // Track seen titles to avoid duplicates
  const seen = new Set();

  for (const item of allItems) {
    if (seen.has(item.title)) continue;
    seen.add(item.title);

    // Local sources
    const localSources = ['startland', 'siliconprairie', 'bizjournals', 'missouripartnership'];
    const isLocal = localSources.some(s => item.source.toLowerCase().includes(s));

    if (isLocal && result.local.length < 10) {
      result.local.push(item);
    }

    // Sort into categories by relevance
    if (item.relevance === 'executive' && result.executive.length < 10) {
      result.executive.push(item);
    } else if (item.relevance === 'funding' && result.funding.length < 10) {
      result.funding.push(item);
    } else if (item.relevance === 'layoffs' && result.layoffs.length < 10) {
      result.layoffs.push(item);
    }
  }

  return result;
}

async function main() {
  console.log('Fetching RSS feeds...');

  const allItems = [];

  for (const [category, feeds] of Object.entries(RSS_FEEDS)) {
    for (const feed of feeds) {
      try {
        console.log(`Fetching: ${feed.name}...`);
        const xmlText = await fetchRSS(feed.url);
        const items = await parseRSS(xmlText, feed.name, category);
        allItems.push(...items);
        console.log(`  ✓ Got ${items.length} items from ${feed.name}`);
      } catch (error) {
        console.error(`  ✗ Failed to fetch ${feed.name}:`, error.message);
      }
    }
  }

  // Categorize
  const categorized = categorizeArticles(allItems);

  // Ensure data directory exists
  const dataDir = path.join(__dirname, '..', 'data');
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }

  // Save to JSON file
  const outputPath = path.join(dataDir, 'rss-feeds.json');
  fs.writeFileSync(outputPath, JSON.stringify(categorized, null, 2));

  console.log(`\n✓ Saved ${allItems.length} articles to ${outputPath}`);
  console.log(`  - Local: ${categorized.local.length}`);
  console.log(`  - Executive: ${categorized.executive.length}`);
  console.log(`  - Funding: ${categorized.funding.length}`);
  console.log(`  - Layoffs: ${categorized.layoffs.length}`);
}

main().catch(console.error);

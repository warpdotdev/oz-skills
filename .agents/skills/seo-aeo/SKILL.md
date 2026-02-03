---
name: seo-aeo
description: Optimize for search engine visibility, ranking, and AI citations. Covers traditional SEO (Google rankings) and AEO (AI agent visibility in ChatGPT, Perplexity, Gemini). Use when asked to "improve SEO", "optimize for search", "fix meta tags", "add structured data", "AEO", "AI visibility", or "answer engine optimization".
license: MIT
metadata:
  version: "2.0"
---

# SEO optimization

Search engine optimization based on Lighthouse SEO audits and Google Search guidelines. Focus on technical SEO, on-page optimization, and structured data.

## Technical SEO

### Crawlability

**robots.txt:**
```text
# /robots.txt
User-agent: *
Allow: /

# Block admin/private areas
Disallow: /admin/
Disallow: /api/
Disallow: /private/

# Don't block resources needed for rendering
# ❌ Disallow: /static/

Sitemap: https://example.com/sitemap.xml
```

**Meta robots:**
```html
<!-- Default: indexable, followable -->
<meta name="robots" content="index, follow">

<!-- Noindex specific pages -->
<meta name="robots" content="noindex, nofollow">

<!-- Indexable but don't follow links -->
<meta name="robots" content="index, nofollow">

<!-- Control snippets -->
<meta name="robots" content="max-snippet:150, max-image-preview:large">
```

**Canonical URLs:**
```html
<!-- Prevent duplicate content issues -->
<link rel="canonical" href="https://example.com/page">

<!-- Self-referencing canonical (recommended) -->
<link rel="canonical" href="https://example.com/current-page">

<!-- For paginated content -->
<link rel="canonical" href="https://example.com/products">
<!-- Or use rel="prev" / rel="next" for explicit pagination -->
```

### XML sitemap

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2024-01-15</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://example.com/products</loc>
    <lastmod>2024-01-14</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```

**Sitemap best practices:**
- Maximum 50,000 URLs or 50MB per sitemap
- Use sitemap index for larger sites
- Include only canonical, indexable URLs
- Update `lastmod` when content changes
- Submit to Google Search Console

### URL structure

```
✅ Good URLs:
https://example.com/products/blue-widget
https://example.com/blog/how-to-use-widgets

❌ Poor URLs:
https://example.com/p?id=12345
https://example.com/products/item/category/subcategory/blue-widget-2024-sale-discount
```

**URL guidelines:**
- Use hyphens, not underscores
- Lowercase only
- Keep short (< 75 characters)
- Include target keywords naturally
- Avoid parameters when possible
- Use HTTPS always

### HTTPS & security

```html
<!-- Ensure all resources use HTTPS -->
<img src="https://example.com/image.jpg">

<!-- Not: -->
<img src="http://example.com/image.jpg">
```

**Security headers for SEO trust signals:**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
```

---

## On-page SEO

### Title tags

```html
<!-- ❌ Missing or generic -->
<title>Page</title>
<title>Home</title>

<!-- ✅ Descriptive with primary keyword -->
<title>Blue Widgets for Sale | Premium Quality | Example Store</title>
```

**Title tag guidelines:**
- 50-60 characters (Google truncates ~60)
- Primary keyword near the beginning
- Unique for every page
- Brand name at end (unless homepage)
- Action-oriented when appropriate

### Meta descriptions

```html
<!-- ❌ Missing or duplicate -->
<meta name="description" content="">

<!-- ✅ Compelling and unique -->
<meta name="description" content="Shop premium blue widgets with free shipping. 30-day returns. Rated 4.9/5 by 10,000+ customers. Order today and save 20%.">
```

**Meta description guidelines:**
- 150-160 characters
- Include primary keyword naturally
- Compelling call-to-action
- Unique for every page
- Matches page content

### Heading structure

```html
<!-- ❌ Poor structure -->
<h2>Welcome to Our Store</h2>
<h4>Products</h4>
<h1>Contact Us</h1>

<!-- ✅ Proper hierarchy -->
<h1>Blue Widgets - Premium Quality</h1>
  <h2>Product Features</h2>
    <h3>Durability</h3>
    <h3>Design</h3>
  <h2>Customer Reviews</h2>
  <h2>Pricing</h2>
```

**Heading guidelines:**
- Single `<h1>` per page (the main topic)
- Logical hierarchy (don't skip levels)
- Include keywords naturally
- Descriptive, not generic

### Image SEO

```html
<!-- ❌ Poor image SEO -->
<img src="IMG_12345.jpg">

<!-- ✅ Optimized image -->
<img src="blue-widget-product-photo.webp"
     alt="Blue widget with chrome finish, side view showing control panel"
     width="800"
     height="600"
     loading="lazy">
```

**Image guidelines:**
- Descriptive filenames with keywords
- Alt text describes the image content
- Compressed and properly sized
- WebP/AVIF with fallbacks
- Lazy load below-fold images

### Internal linking

```html
<!-- ❌ Non-descriptive -->
<a href="/products">Click here</a>
<a href="/widgets">Read more</a>

<!-- ✅ Descriptive anchor text -->
<a href="/products/blue-widgets">Browse our blue widget collection</a>
<a href="/guides/widget-maintenance">Learn how to maintain your widgets</a>
```

**Linking guidelines:**
- Descriptive anchor text with keywords
- Link to relevant internal pages
- Reasonable number of links per page
- Fix broken links promptly
- Use breadcrumbs for hierarchy

---

## Structured data (JSON-LD)

### Organization

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Example Company",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "sameAs": [
    "https://twitter.com/example",
    "https://linkedin.com/company/example"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+1-555-123-4567",
    "contactType": "customer service"
  }
}
</script>
```

### Article

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "How to Choose the Right Widget",
  "description": "Complete guide to selecting widgets for your needs.",
  "image": "https://example.com/article-image.jpg",
  "author": {
    "@type": "Person",
    "name": "Jane Smith",
    "url": "https://example.com/authors/jane-smith"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Example Blog",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    }
  },
  "datePublished": "2024-01-15",
  "dateModified": "2024-01-20"
}
</script>
```

### Product

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Blue Widget Pro",
  "image": "https://example.com/blue-widget.jpg",
  "description": "Premium blue widget with advanced features.",
  "brand": {
    "@type": "Brand",
    "name": "WidgetCo"
  },
  "offers": {
    "@type": "Offer",
    "price": "49.99",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "url": "https://example.com/products/blue-widget"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "reviewCount": "1250"
  }
}
</script>
```

### FAQ

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What colors are available?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Our widgets come in blue, red, and green."
      }
    },
    {
      "@type": "Question",
      "name": "What is the warranty?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "All widgets include a 2-year warranty."
      }
    }
  ]
}
</script>
```

### Breadcrumbs

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://example.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Products",
      "item": "https://example.com/products"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Blue Widgets",
      "item": "https://example.com/products/blue-widgets"
    }
  ]
}
</script>
```

### Validation

Test structured data at:
- [Google Rich Results Test](https://search.google.com/test/rich-results)
- [Schema.org Validator](https://validator.schema.org/)

---

## Mobile SEO

### Responsive design

```html
<!-- ❌ Not mobile-friendly -->
<meta name="viewport" content="width=1024">

<!-- ✅ Responsive viewport -->
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Tap targets

```css
/* ❌ Too small for mobile */
.small-link {
  padding: 4px;
  font-size: 12px;
}

/* ✅ Adequate tap target */
.mobile-friendly-link {
  padding: 12px;
  font-size: 16px;
  min-height: 48px;
  min-width: 48px;
}
```

### Font sizes

```css
/* ❌ Too small on mobile */
body {
  font-size: 10px;
}

/* ✅ Readable without zooming */
body {
  font-size: 16px;
  line-height: 1.5;
}
```

---

## International SEO

### Hreflang tags

```html
<!-- For multi-language sites -->
<link rel="alternate" hreflang="en" href="https://example.com/page">
<link rel="alternate" hreflang="es" href="https://example.com/es/page">
<link rel="alternate" hreflang="fr" href="https://example.com/fr/page">
<link rel="alternate" hreflang="x-default" href="https://example.com/page">
```

### Language declaration

```html
<html lang="en">
<!-- or -->
<html lang="es-MX">
```

---

## SEO audit checklist

### Critical
- [ ] HTTPS enabled
- [ ] robots.txt allows crawling
- [ ] No `noindex` on important pages
- [ ] Title tags present and unique
- [ ] Single `<h1>` per page

### High priority
- [ ] Meta descriptions present
- [ ] Sitemap submitted
- [ ] Canonical URLs set
- [ ] Mobile-responsive
- [ ] Core Web Vitals passing

### Medium priority
- [ ] Structured data implemented
- [ ] Internal linking strategy
- [ ] Image alt text
- [ ] Descriptive URLs
- [ ] Breadcrumb navigation

### Ongoing
- [ ] Fix crawl errors in Search Console
- [ ] Update sitemap when content changes
- [ ] Monitor ranking changes
- [ ] Check for broken links
- [ ] Review Search Console insights

---

## Audit workflow

1. Baseline: run Lighthouse and PageSpeed on key templates (home, category, detail, blog).
2. Crawl: verify indexability, canonicals, and duplicate content (use Search Console + crawler).
3. Fix blockers: `noindex`, `robots.txt`, canonical mismatches, redirect chains.
4. On-page: titles, meta descriptions, headings, internal linking, image alt.
5. Structured data: add JSON-LD and validate rich results.
6. Re-verify: re-run Lighthouse/PageSpeed and check Search Console coverage.

---

## Common pitfalls

- `noindex` or `X-Robots-Tag` accidentally set on important pages
- `robots.txt` blocks CSS/JS or critical render resources
- Canonical points to a different URL than the one indexed
- Mixed `http`/`https` or `www`/non-`www` causing duplicate content
- Redirect chains/loops (waste crawl budget and slow page load)
- Parameterized URLs indexable (filters, sort, UTM) without canonical control
- JavaScript-rendered content not visible in initial HTML
- Soft 404s (200 status with "not found" content)
- Sitemap includes non-canonical or `noindex` URLs
- Hreflang tags missing reciprocal links or using wrong language/region codes

---

## Tools

| Tool | Use |
|------|-----|
| Google Search Console | Monitor indexing, fix issues |
| Google PageSpeed Insights | Performance + Core Web Vitals |
| Rich Results Test | Validate structured data |
| Lighthouse | Full SEO audit |
| Screaming Frog | Crawl analysis |

---

## Scripts (optional)

Scripts under `scripts/seo/` for repeatable audits:

- `scripts/seo/lighthouse.sh`: run Lighthouse CLI against a URL or URL list and store JSON reports.
- `scripts/seo/pagespeed.sh`: call PageSpeed Insights API with `curl` and capture JSON output.
- `scripts/seo/search-console-export.mjs`: export Search Console Search Analytics data (requires OAuth access token).

Example usage:
```bash
# Lighthouse (SEO category only)
scripts/seo/lighthouse.sh https://example.com
scripts/seo/lighthouse.sh urls.txt reports/lighthouse

# PageSpeed Insights API (requires PAGESPEED_API_KEY)
PAGESPEED_API_KEY=... scripts/seo/pagespeed.sh https://example.com
PAGESPEED_API_KEY=... scripts/seo/pagespeed.sh urls.txt reports/pagespeed

# Search Console API (requires GSC_ACCESS_TOKEN)
GSC_ACCESS_TOKEN=... scripts/seo/search-console-export.mjs https://example.com 2024-01-01 2024-01-31
```

---

## AEO / AI Visibility Optimization

Answer Engine Optimization (AEO) focuses on making content discoverable and citable by AI agents (ChatGPT, Perplexity, Gemini, Google AI Overviews). While SEO targets rankings and clicks, AEO targets citations, mentions, and brand authority within AI-generated responses.

### Key differences from SEO

```
SEO: Rank high → get clicks → drive traffic
AEO: Be cited → own the answer → build authority

SEO metric: Position, CTR, impressions
AEO metric: Citations, mentions, AI visibility score

SEO query: "best project management software"
AEO query: "What's the best project management software for a remote team of 15 with budget under $500/month?"
```

**Market shift:**
- Gartner predicts 25% drop in traditional search volume by 2026 due to AI chatbots
- 400M+ people use OpenAI products weekly
- 58% of searches are now "zero-click" (answered directly in AI interface)

### Content structure for AEO

**Answer-first formatting:**

```markdown
<!-- ❌ SEO-style (context first) -->
## What is AEO?
In recent years, the rise of AI-powered search has transformed 
how users discover information. This shift has created new 
opportunities for brands. Answer Engine Optimization is...

<!-- ✅ AEO-style (answer first) -->
## What is AEO?
Answer Engine Optimization (AEO) is the practice of structuring 
content so AI systems can directly extract and cite answers. 
It focuses on citations in AI responses rather than search rankings.

Unlike traditional SEO, AEO optimizes for conversational queries 
and zero-click results where users get answers without visiting 
your site.
```

**Guidelines:**
- Lead with 40-60 word direct answer
- Self-contained responses (AI extracts without surrounding context)
- Conversational, natural language
- Specific data > vague claims
- Include quantified claims, dates, authoritative citations

**Entity-based optimization:**

```markdown
<!-- ❌ Keyword-focused -->
"Our software helps teams collaborate better with features 
for project management and communication."

<!-- ✅ Entity-focused -->
"Acme PM is a project management platform for remote teams. 
Founded in 2020, serves 50,000+ companies. Key features: 
Kanban boards, time tracking, Slack integration. Pricing: 
$12/user/month."
```

Define who you are, what you do, and why AI should trust you.

### Schema for AEO

Expand beyond SEO schema to optimize for AI extraction.

**Critical schema types for AEO:**

1. **FAQPage** (highest AI citation rate)
   - Template: `references/json-ld-templates.md`

**FAQ answer guidelines for AEO:**
- 40-60 words ideal (under 30 = lacks substance, over 80 = hard to extract)
- Match visible H2/H3 headings to schema "name" property exactly
- Include specific numbers, dates, and data
- Self-contained (makes sense without context)
- Natural question phrasing (how users actually ask)

2. **Author + Organization** (trust signals)
   - Template: `references/json-ld-templates.md`

**Why it matters:** AI engines prioritize content from identifiable, authoritative sources. Use `sameAs` links to disambiguate your brand.

3. **Product** (for e-commerce AEO)
   - Template: `references/json-ld-templates.md`

Allows AI shopping modules to show accurate pricing, availability, reviews.

### Platform-specific optimization

Different AI engines have different preferences. Balance all three for maximum citation probability.

**ChatGPT:**
- Neutral, encyclopedia-style tone
- Authoritative external citations
- Specific data and quantified claims
- Formal structure

```markdown
Example: "According to a 2025 Gartner study, 78% of enterprises 
adopted AI-powered search tools. The primary drivers were cost 
reduction (cited by 62% of respondents) and improved accuracy 
(58%). Source: Gartner AI Search Report 2025."
```

**Perplexity:**
- Conversational, experience-driven
- Practical examples and case studies
- Community insights and real-world context
- Less formal tone

```markdown
Example: "Most teams start with the free tier and upgrade after 
2-3 months once they've proven ROI. Based on feedback from 500+ 
customers, common triggers for upgrading include hitting user 
limits or needing advanced reporting."
```

**Google AI Overviews:**
- E-E-A-T signals (Experience, Expertise, Authoritativeness, Trust)
- Fresh content with recent dates
- Featured snippet-friendly formatting
- Mobile-optimized structure

```markdown
Example: "Updated February 2026: Current pricing starts at 
$12/user/month (annual billing). Month-to-month adds 20%. 
Education and nonprofit discounts available. No free tier 
as of Q1 2026."
```

### AEO measurement & tools

**Metrics:**
- Citation frequency (how often AI mentions your brand)
- Visibility score (presence across AI platforms)
- Context quality (positive/neutral/negative sentiment)
- Source attribution (which URLs AI cites)

**Tracking AI referral traffic:**

In Google Analytics 4, filter traffic sources:
- `chat.openai.com` (ChatGPT)
- `perplexity.ai`
- `gemini.google.com`
- `copilot.microsoft.com`

Monitor these as separate acquisition sources.

Use your preferred AEO monitoring tool to track citation frequency, context, and source attribution.

### AEO audit checklist

#### Content audit
- [ ] All key pages have 40-60 word direct answers upfront
- [ ] FAQ sections with self-contained answers
- [ ] Conversational language matching natural queries
- [ ] Specific data (numbers, dates, sources) not vague claims
- [ ] Author bios and organization info visible
- [ ] Content updated with recent dates (freshness)

#### Schema audit
- [ ] FAQPage schema on FAQ/guide pages
- [ ] Author schema on all articles/blogs
- [ ] Organization schema site-wide
- [ ] Product schema on product pages (if e-commerce)
- [ ] Article schema with datePublished/dateModified
- [ ] Schema matches visible content exactly (no hidden markup)
- [ ] Validate with Google Rich Results Test

#### Technical audit
- [ ] JSON-LD format (preferred by AI engines)
- [ ] Schema.org standards compliance
- [ ] No conflicting or duplicate schema
- [ ] Fast page load (AI crawlers prefer fast sites)
- [ ] Clean HTML structure (semantic headings)
- [ ] Mobile-optimized (especially for Google AI Overviews)

#### Entity & authority signals
- [ ] Clear brand identity (who you are, what you do)
- [ ] Consistent NAP (name, address, phone) across web
- [ ] `sameAs` links to LinkedIn, Twitter, official profiles
- [ ] External citations and backlinks from authoritative sources
- [ ] Active presence on review platforms
- [ ] Google Business Profile optimized (local businesses)

#### AI visibility monitoring
- [ ] Test top 10-20 commercial queries monthly
- [ ] Track AI referral traffic in GA4
- [ ] Monitor brand mentions across AI platforms
- [ ] Check citation context (positive/neutral/negative)
- [ ] Verify factual accuracy of AI responses about your brand
- [ ] Set up alerts for visibility changes (if using paid tools)


---

## References

- [Google Search Central](https://developers.google.com/search)
- [Schema.org](https://schema.org/)
- [Core Web Vitals](../core-web-vitals/SKILL.md)
- [Web Quality Audit](../web-quality-audit/SKILL.md)

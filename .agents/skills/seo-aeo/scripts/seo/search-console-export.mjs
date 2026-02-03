#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const [siteUrl, startDate, endDate] = args;

if (!siteUrl || !startDate || !endDate) {
  console.error(
    "Usage: scripts/seo/search-console-export.mjs <siteUrl> <startDate> <endDate> [outputDir]"
  );
  console.error("Example: scripts/seo/search-console-export.mjs https://example.com 2024-01-01 2024-01-31");
  process.exit(1);
}

const outputDir = args[3] || "reports/search-console";
const token = process.env.GSC_ACCESS_TOKEN;
if (!token) {
  console.error("Missing GSC_ACCESS_TOKEN env var.");
  console.error("Create an OAuth 2.0 access token with Search Console API scope:");
  console.error("  https://www.googleapis.com/auth/webmasters.readonly");
  console.error("Then run:");
  console.error("  GSC_ACCESS_TOKEN=... scripts/seo/search-console-export.mjs <siteUrl> <start> <end>");
  process.exit(1);
}

fs.mkdirSync(outputDir, { recursive: true });

const safeName = siteUrl.replace(/^https?:\/\//, "").replace(/[^a-zA-Z0-9._-]/g, "_");
const outPath = path.join(outputDir, `${safeName}_${startDate}_${endDate}.json`);

const endpoint = `https://searchconsole.googleapis.com/v1/sites/${encodeURIComponent(
  siteUrl
)}/searchAnalytics/query`;

const body = {
  startDate,
  endDate,
  dimensions: ["query", "page"],
  rowLimit: 25000,
};

const res = await fetch(endpoint, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify(body),
});

if (!res.ok) {
  const text = await res.text();
  console.error(`Search Console API error: ${res.status}`);
  console.error(text);
  process.exit(1);
}

const json = await res.json();
fs.writeFileSync(outPath, JSON.stringify(json, null, 2));

console.log(`Export saved to ${outPath}`);

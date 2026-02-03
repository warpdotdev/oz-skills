# JSON-LD templates

## FAQPage

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "What is the average cost of local SEO services?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Most small businesses invest $1,000–$3,000/month for local SEO covering technical fixes, Google Business Profile optimization, citations, and content. Budgets vary with competition and practice areas. Ask providers for transparent deliverables, local proof, and expected timelines."
    }
  }]
}
</script>
```

## Author + Organization

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "author": {
    "@type": "Person",
    "name": "Jane Smith",
    "url": "https://example.com/authors/jane-smith",
    "sameAs": [
      "https://linkedin.com/in/janesmith",
      "https://twitter.com/janesmith"
    ]
  },
  "publisher": {
    "@type": "Organization",
    "name": "Example Corp",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    },
    "sameAs": [
      "https://linkedin.com/company/example",
      "https://twitter.com/examplecorp"
    ]
  },
  "datePublished": "2026-01-15",
  "dateModified": "2026-02-01"
}
</script>
```

## Product

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Acme Project Manager Pro",
  "description": "Cloud project management for remote teams. Kanban, time tracking, 200+ integrations.",
  "brand": {
    "@type": "Brand",
    "name": "Acme Software"
  },
  "offers": {
    "@type": "Offer",
    "price": "12.00",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "priceValidUntil": "2026-12-31"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.7",
    "reviewCount": "3240"
  }
}
</script>
```

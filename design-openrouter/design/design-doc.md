# OpenRouter architecture / design docs

OpenRouter Quickstart (high-level product + “single endpoint, automatic fallbacks”)
https://openrouter.ai/docs/quickstart

API Reference overview (model routing + failover behavior at API-contract level)
https://openrouter.ai/docs/api/reference/overview

Provider routing / selection (how routing is controlled, load-balancing across providers)
https://openrouter.ai/docs/guides/routing/provider-selection

Latency & performance (explicitly mentions edge computing on Cloudflare Workers)
https://openrouter.ai/docs/guides/best-practices/latency-and-performance

# OpenRouter ↔ Cloudflare relationship

OpenRouter announcement: “Introducing Cloudflare as a new provider” (Cloudflare Workers AI serving models via OpenRouter)
https://openrouter.ai/announcements/introducing-cloudflare-as-a-new-provider

OpenRouter provider page: Cloudflare (OpenRouter’s provider catalog entry)
https://openrouter.ai/provider/cloudflare

Cloudflare AI Gateway: “OpenRouter” provider integration (how to call OpenRouter through Cloudflare’s AI Gateway endpoint)
https://developers.cloudflare.com/ai-gateway/usage/providers/openrouter/

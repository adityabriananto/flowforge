# RFC-003: Capability Policy Engine

## Status
PROPOSED

## Konsep Utama
Capability Policy Engine menggantikan dynamic resolver lama yang statis. Pengguna dapat mendefinisikan strategi alokasi LLM provider berdasarkan kriteria kualitas (*quality*), biaya (*cost*), dan latensi (*latency*).

## Kebijakan (Policy)
Engine membaca aturan kebijakan di level workflow:
```yaml
policy:
  strategy: "quality-first" | "cost-first" | "latency-first"
  fallback:
    - "gpt"
    - "qwen"
  timeout_seconds: 120
  retry_limit: 3
```

## Mekanisme Pemilihan
1. **quality-first**: Mengarahkan capability `architecture` atau `coding` ke model-model premium (Claude-3-Opus, Claude-3.5-Sonnet) tanpa mempedulikan biaya.
2. **cost-first**: Mengarahkan pekerjaan ke model yang lebih hemat (GPT-4o-mini, Qwen) selama kapabilitas dasarnya memenuhi syarat.

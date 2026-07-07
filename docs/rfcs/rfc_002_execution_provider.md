# RFC-002: Execution Provider and Structured Output

## Status
PROPOSED

## Konsep Utama
AI Worker mengembalikan data eksekusi terstruktur `ExecutionResult` dalam bentuk JSON yang kaya, bukan sekadar exit code atau status boolean sederhana.

## Spesifikasi Data
```json
{
  "status": "SUCCESS" | "NO_CHANGE" | "FAILED",
  "artifacts": [
    "src/utils.py",
    "docs/architecture.md"
  ],
  "metrics": {
    "duration_seconds": 12.42,
    "tokens_used": 3250,
    "estimated_cost": 0.048
  },
  "git_diff": "diff -u src/utils.py ...",
  "logs": "[cli] Processing prompt...\n[cli] Writing files...",
  "stdout": "Success",
  "stderr": ""
}
```

## Abstraksi Layer
Interface `ExecutionProvider` memisahkan channel komunikasi (apakah itu API request, CLI process, local Ollama, dll.) sehingga Worker runtime tidak perlu peduli medium komunikasi mana yang digunakan.

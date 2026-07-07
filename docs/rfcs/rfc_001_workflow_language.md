# RFC-001: FlowForge Workflow Language (FFWL)

## Status
PROPOSED

## Konsep Utama
FlowForge Workflow Language (FFWL) adalah DSL deklaratif berbasis YAML yang mendefinisikan State Machine AI Agent secara terstruktur. File FFWL harus secara ketat menggunakan ekstensi `.ff.yaml`.

## Spesifikasi Format
```yaml
name: "AI Code Generator Workflow"
version: "1.2.0"
initial_state: "ANALYSIS"

states:
  ANALYSIS:
    name: "Requirements Analyzer"
    worker_type: "subprocess"
    script: "agents/analyzer.py"
    timeout_seconds: 120
  CODING:
    name: "AI Coder"
    worker_type: "subprocess"
    script: "agents/coder.py"
    require_human: false
  REVIEW:
    name: "Human Gatekeeper"
    require_human: true
    on_approve: "COMPLETED"
    on_reject: "CODING"
  COMPLETED:
    name: "Finished"
    is_final: true

transitions:
  - from: "ANALYSIS", event: "SUCCESS", to: "CODING"
  - from: "CODING", event: "SUCCESS", to: "REVIEW"
  - from: "CODING", event: "FAILURE", to: "ANALYSIS"
```
## Verifikasi Identitas
Engine FlowForge memverifikasi nama file. Jika file tidak berakhiran `.ff.yaml`, engine akan menolak memproses alur kerja tersebut.

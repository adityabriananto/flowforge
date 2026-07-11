# FlowForge Product Roadmap

Peta jalan rilis versi pengembangan framework orkestrasi FlowForge.

---

## Release Roadmap

### v1.1 — Refactor & Foundation Enhancement
Fokus pada penguatan arsitektur internal State Machine, standarisasi input/output AI, dan loader workflow deklaratif tanpa coding.
-   **Workflow Definition YAML**: Engine meload alur kerja langsung dari file `workflow.yaml`.
-   **Capability Resolver**: Pemetaan job/worker secara dinamis ke LLM Provider terbaik (Claude/Codex).
-   **Prompt Builder**: Modul sentral untuk templating prompt dan loading file context.
-   **Artifact Manager**: Pelacakan hasil output AI formal sebagai Artifact versi terkontrol.

### v1.2 — Policy Engine & CLI Tools
Fokus pada keandalan resolusi worker secara aman dan peningkatan UX command line interface.
-   **Capability Policy Engine**: Resolusi provider dengan prioritas biaya, kecepatan, dan aturan capability matching dinamis.
-   **CLI Tools**: flowforge run, compile, replay, doctor.

### v1.3 — Mission System, Agent Profile, & Compiler
Membawa konsep AI Worker sebagai agen rekayasa modular.
-   **Mission Lifecycle**: backlog ➔ active ➔ completed.
-   **Agent Profile System**: Penentuan kapabilitas runtime agen.
-   **Mission Package Compiler**: Compiler yang merender data rekayasa mentah (RFC, ADR, roadmap) menjadi paket vendor-agnostic.

### v1.5 — AI Runtime & Core Completion (Current)
Penyambungan seluruh domain modular rekayasa ke dalam satu orkestrasi runtime terpadu.
-   **Mission Package as Contract**: Kontrak pelaksanaan tugas terstandarisasi.
-   **Engineering Session**: Log detail audit eksekusi worker tunggal secara immutable pasca-penyelesaian.
-   **Engineering State**: Memori jangka panjang proyek ter-update otomatis di disk via `ENGINEERING_STATE.yaml` untuk context restoration.
-   **AI Runtime Engine & Registry**: Penyedia integrasi orkestrasi stateless end-to-end.
-   **Core Complete**: FlowForge Core v1.5 selesai sepenuhnya.

### v1.6 — Scale & Distribution (Next)
Fokus pada infrastruktur terdistribusi dan kontainerisasi.
-   **Distributed Worker**: Eksekusi Worker di mesin server terpisah secara asinkron.
-   **Redis Integration**: Event broker & message queue berbasis Redis untuk sinkronisasi state.
-   **Dockerization**: Kontainerisasi engine backend dan dashboard frontend.
-   **Kubernetes (K8s)**: Manifest deployment untuk orkestrasi cluster terdistribusi.

### v2.0 — Ecosystem & Cloud
Fokus pada perluasan ekosistem developer dan integrasi awan.
-   **Marketplace**: Toko plugin dan worker templates kustom yang dapat di-share.
-   **Plugin Registry**: Registri pusat untuk mempublish dan mendownload FlowForge plugins.
-   **Cloud Integration**: Layanan SaaS managed FlowForge.
-   **Model Context Protocol (MCP)**: Dukungan penuh standard protokol MCP untuk integrasi tools AI.
-   **VSCode Extension**: Ekstensi editor visual untuk mendesain workflow dan memantau status instansi langsung dari editor.

---

## Definition of Done (DoD)

-   Semua unit & integration tests lulus 100%.
-   Dokumentasi API, README, dan STATUS diperbarui.
-   ADR dibuat/diperbarui untuk keputusan arsitektur baru.
-   Semua kode terkompilasi sukses tanpa warning/error.
-   Perubahan dipush ke remote origin repository.

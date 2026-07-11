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
Penyambungan seluruh domain modular rekayasa ke dalam satu orkestrasi runtime terpadu hingga stabil sebagai *FlowForge Core v1.0.0-beta*.
-   **✅ Platform Validation**: Engine Layer divalidasi melalui pilot project (BroDev Cashier & Meeting Intelligence).
-   **✅ FF-024 Engineering Artifact Identity Service**: Manajemen identifier rekayasa lintas repositori.
-   **⏳ FF-025 Mission Planning Engine**: Perencanaan *engineering* deterministik bawaan (tanpa eksekusi AI langsung).
-   **⏳ FF-026 README 2.0 & Developer Onboarding**: Perbaikan panduan instalasi dan dokumentasi orientasi.
-   **⏳ FF-027 Public Distribution (PyPI)**: Paket rilis siap pakai ke Python Package Index.

### Core Freeze Policy (Post-FF-027)
Setelah FF-027 selesai, platform *FlowForge Core* (cabang `main`) akan dibekukan (masuk fase *Core Freeze*).
-   **Core hanya menerima**: Critical bug fixes, Security fixes, Performance improvements, Documentation improvements, Small compatibility updates.
-   **Core TIDAK menerima**: Eksperimen fitur, dashboard UX, editor visual, integrasi cloud, AI-assisted planning, marketplace. Segala kapabilitas di atas merupakan peningkatan produktivitas yang harus diletakkan pada layer aplikasi di luar *Core*.

### v2.0 — Productivity & Ecosystem Enhancements (Next)
Fokus pada infrastruktur terdistribusi, perluasan ekosistem developer, dan eksperimen UX yang dijalankan sepenuhnya di cabang `next`.
-   **Distributed Worker & K8s**: Kontainerisasi engine backend dan dashboard frontend untuk cluster terdistribusi.
-   **Cloud Integration & Marketplace**: Layanan SaaS managed FlowForge dan toko template plugin.
-   **VSCode Extension & Visual Workspace**: Ekstensi editor visual untuk mendesain workflow dan memantau status instansi.
-   **AI-assisted Planning (Plugin)**: Integrasi kecerdasan buatan dalam perencanaan (sebagai modul ekstensi).

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

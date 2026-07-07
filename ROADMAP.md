# FlowForge Product Roadmap

Peta jalan rilis versi pengembangan framework orkestrasi FlowForge.

---

## Release Roadmap

### v1.1 -- Refactor & Foundation Enhancement (Current)
Fokus pada penguatan arsitektur internal State Machine, standarisasi input/output AI, dan loader workflow deklaratif tanpa coding.
-   **Workflow Definition YAML**: Engine meload alur kerja langsung dari file `workflow.yaml`.
-   **Capability Resolver**: Pemetaan job/worker secara dinamis ke LLM Provider terbaik (Claude/Codex).
-   **Prompt Builder**: Modul sentral untuk templating prompt dan loading file context.
-   **Artifact Manager**: Pelacakan hasil output AI formal sebagai Artifact versi terkontrol.
-   **Memory**: Modul memori asinkron jangka pendek & panjang di bawah `.project/memory/`.

### v1.2 -- Resiliency & Scheduling (Next)
Fokus pada keandalan sistem eksekusi Worker berskala besar.
-   **Multi Worker**: Dukungan eksekusi beberapa Worker secara paralel/konkuren.
-   **Retry Mechanism**: Pengulangan otomatis pada Worker yang mengalami crash.
-   **Scheduler**: Penjadwalan alur kerja berbasis cron/timer.
-   **Timeout**: Batasan waktu eksekusi Worker untuk mencegah hanging process.
-   **Queue (Antrean)**: Manajemen beban kerja menggunakan internal FIFO queue.

### v1.3 -- Scale & Distribution
Fokus pada infrastruktur terdistribusi dan kontainerisasi.
-   **Distributed Worker**: Eksekusi Worker di mesin server terpisah secara asinkron.
-   **Redis Integration**: Event broker & message queue berbasis Redis untuk sinkronisasi state.
-   **Dockerization**: Kontainerisasi engine backend dan dashboard frontend.
-   **Kubernetes (K8s)**: Manifest deployment untuk orkestrasi cluster terdistribusi.

### v2.0 -- Ecosystem & Cloud
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

# Business Requirements Document (BRD) - FlowForge

**Project Name:** FlowForge  
**Version:** v1.0.0  
**Status:** Approved (Sprint 0 - Discovery)  
**Date:** 2026-07-07  

---

## 1. Executive Summary

### 1.1. Background
Proses rekayasa perangkat lunak (software engineering) modern semakin banyak memanfaatkan kecerdasan buatan (AI) untuk mempercepat siklus pengembangan. Namun, sebagian besar solusi AI saat ini bekerja secara ad-hoc, tidak terstruktur, dan sulit dipantau. 

### 1.2. Product Vision
**FlowForge** hadir sebagai *AI Workflow Orchestration Framework* standar industri untuk software engineering. Sistem ini memperlakukan agen AI sebagai *Worker* yang menjalankan unit pekerjaan (*Job*) di dalam alur kerja (*Workflow*) terstruktur yang diatur oleh mesin status (*State Machine*).

### 1.3. Value Proposition
- **Workflow First**: Memaksa semua integrasi AI berjalan dalam struktur alur kerja yang terdefinisi dengan jelas.
- **Vendor Agnostic**: Fleksibilitas untuk menggunakan berbagai model AI/LLM dan infrastruktur cloud tanpa terikat pada vendor tertentu.
- **Human In Control**: Menjamin kontrol penuh manusia (Human-in-the-Loop) untuk verifikasi kode dan keputusan penting melalui mekanisme persetujuan real-time.

---

## 2. Business Objectives

1. **Efisiensi Siklus Pengembangan**: Mengurangi waktu pengerjaan (lead time) tugas-tugas berulang (seperti debugging, penulisan unit test, migrasi database) hingga 50%.
2. **Standardisasi Alur Kerja**: Menyediakan standar integrasi agen AI dalam siklus pengembangan (SDLC) yang aman dan konsisten.
3. **Auditabilitas & Transparansi**: Menyediakan jejak audit (audit trail) lengkap dari setiap keputusan dan aksi yang diambil oleh agen AI.

---

## 3. Target Audience & User Persona

### 3.1. Software Engineer / Developer
- **Tujuan**: Mendelegasikan tugas penulisan kode repetitif atau unit test ke agen AI.
- **Kebutuhan**: Integrasi yang mulus dengan repositori kode (seperti Git) dan kemampuan untuk meninjau (review) serta menyetujui pekerjaan AI sebelum digabungkan ke codebase utama.

### 3.2. Project Lead / Architect
- **Tujuan**: Mendefinisikan alur kerja pengembangan perangkat lunak yang aman dan efisien.
- **Kebutuhan**: Alat untuk memantau status alur kerja, mendefinisikan state transition, dan menegakkan kebijakan keamanan (security policies).

### 3.3. QA Engineer
- **Tujuan**: Memastikan kode yang dihasilkan oleh AI memenuhi standar kualitas dan lulus semua pengujian.
- **Kebutuhan**: Otomatisasi pengujian unit yang dipicu secara otomatis oleh transisi state alur kerja.

---

## 4. Product Scope

### 4.1. In-Scope (Fitur Utama)
- **State Machine Core**: Mesin status internal untuk mengelola transisi state dari workflow (contoh: `Idle` -> `Running` -> `Awaiting_Approval` -> `Completed`/`Failed`).
- **Worker Runtime**: Runtime yang sepenuhnya cloud-agnostic untuk menjalankan agen AI secara terisolasi.
- **Human-in-the-Loop (HITL) Interface**: Antarmuka real-time berbasis WebSocket atau Server-Sent Events (SSE) untuk memberikan umpan balik, persetujuan, atau penolakan terhadap tindakan agen AI.
- **Event-Driven Architecture**: Sistem yang mempublikasikan event untuk setiap transisi state agar sistem luar dapat melakukan observasi.
- **FastAPI Backend & React Frontend**: Kerangka kerja pengembangan utama.

### 4.2. Out-of-Scope (Fase Awal)
- Autentikasi multi-tenant yang sangat kompleks (direncanakan pada sprint berikutnya).
- Integrasi native dengan IDE (VS Code/Cursor) secara langsung (direncanakan pasca-dashboard stabil).

---

## 5. High-Level Functional Requirements

### 5.1. Workflow & State Engine
- Sistem harus mampu mendefinisikan workflow menggunakan format terstruktur (seperti JSON/YAML).
- Setiap langkah (step) dalam workflow harus diasosiasikan dengan Worker (AI/LLM atau script otomatis).
- Transisi status harus disimpan secara persisten di database (PostgreSQL) dan dipantau melalui Redis.

### 5.2. Human Approval & Real-Time Sync
- Ketika Worker memerlukan validasi manusia, workflow harus berpindah ke state `Awaiting_Approval`.
- Antarmuka pengguna (Frontend) harus menerima notifikasi instan secara real-time (melalui WebSocket/SSE) ketika persetujuan diperlukan.
- Manusia harus dapat menyetujui, menolak dengan komentar, atau meminta iterasi ulang dari pekerjaan tersebut.

### 5.3. Worker Runtime & Execution
- Runtime harus mampu mengeksekusi instruksi backend dalam Python 3.13+.
- Output dari Worker (log, kode baru, hasil pengujian) harus disimpan dan dapat diakses untuk peninjauan.

---

## 6. Non-Functional Requirements

### 6.1. Performance & Real-Time Interaction
- Latensi pengiriman pesan real-time dari Backend ke Frontend via WebSocket/SSE tidak boleh melebihi 200ms.
- State Machine harus mampu menangani hingga 100 transisi per detik secara konkuren di fase awal.

### 6.2. Security
- Isolasi eksekusi kode Worker untuk mencegah injeksi kode berbahaya.
- Audit trail yang tidak dapat diubah (immutable logs) untuk setiap perubahan state.

### 6.3. Observability
- Logging terpusat untuk memantau waktu eksekusi Worker, konsumsi token LLM (jika ada), dan status antrean di Redis.

---

## 7. Success Metrics (KPIs)

- **Workflow Completion Rate**: >= 95% untuk workflow yang terdefinisi dengan benar tanpa kegagalan sistem internal.
- **Approval Latency**: Waktu yang dibutuhkan untuk merender permintaan persetujuan pada dashboard kurang dari 500ms sejak status `Awaiting_Approval` aktif.
- **User Adoption/Satisfaction**: Kepuasan pengembang dalam menggunakan antarmuka persetujuan (diukur melalui uji kegunaan awal).

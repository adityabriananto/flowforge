# Product Requirements Document (PRD) - FlowForge

**Project Name:** FlowForge  
**Version:** v1.0.0  
**Status:** Approved (Sprint 0 - Discovery)  
**Date:** 2026-07-07  

---

## 1. Introduction & Goals

Dokumen ini menjabarkan spesifikasi fungsional dan teknis detail untuk pengembangan **FlowForge** (AI Workflow Orchestration Framework). Tujuan utamanya adalah menyediakan cetak biru (blueprint) bagi tim pengembang (Backend, Frontend, QA) agar dapat mengimplementasikan sistem yang konsisten, aman, dan berkinerja tinggi mulai dari Sprint 1.

---

## 2. User Personas & User Stories

### 2.1. User Personas

1. **Alex (Senior Software Engineer)**
   - *Karakteristik*: Berpengalaman dengan sistem terdistribusi, menginginkan otomatisasi tugas coding harian tetapi tetap ingin mempertahankan kontrol penuh atas kode yang masuk ke produksi.
   - *Pain Point*: Kualitas kode AI tidak konsisten dan tidak adanya mekanisme persetujuan formal sebelum AI memodifikasi berkas penting.

2. **Sarah (QA Engineer)**
   - *Karakteristik*: Fokus pada integritas kode dan cakupan pengujian (test coverage).
   - *Pain Point*: AI seringkali tidak menulis pengujian unit untuk kodenya sendiri atau merusak pengujian yang sudah ada tanpa disadari.

3. **Budi (Project Lead / Architect)**
   - *Karakteristik*: Bertanggung jawab atas efisiensi tim dan kepatuhan arsitektur.
   - *Pain Point*: Sulit memantau aktivitas agen AI yang berjalan di latar belakang dan melacak konsumsi LLM (token cost).

### 2.2. User Stories

- **US-01 (Mendefinisikan Workflow)**: *Sebagai Alex*, saya ingin mendefinisikan alur kerja pengerjaan kode dalam file konfigurasi YAML, sehingga saya dapat dengan mudah mengubah atau melacak transisi state menggunakan version control (Git).
- **US-02 (HITL Persetujuan Real-Time)**: *Sebagai Alex*, saya ingin menerima notifikasi persetujuan real-time di dasbor ketika agen AI selesai menulis kode, sehingga saya dapat langsung meninjau perubahannya tanpa menunda alur kerja.
- **US-03 (Isolasi Subprocess)**: *Sebagai Budi*, saya ingin eksekusi kode agen AI berjalan secara terisolasi menggunakan subprocess Python di dalam lingkungan khusus, sehingga kode yang berpotensi berbahaya tidak merusak sistem server utama.
- **US-04 (Otomatisasi Uji QA)**: *Sebagai Sarah*, saya ingin transisi state dari `Running` ke `Awaiting_Approval` secara otomatis memicu pengujian unit melalui sistem, sehingga saya hanya meninjau kode yang sudah dipastikan lolos uji dasar.

---

## 3. Product Features & Technical Specifications

### 3.1. Workflow Definition (YAML Configuration)
Sistem menggunakan berkas YAML untuk mendefinisikan State Machine dan langkah-langkah alur kerja (workflow). 

*Contoh Format Definisi Workflow (`workflow.yaml`):*
```yaml
name: "AI Code Fixer & Tester"
version: "1.0.0"
initial_state: "IDLE"

states:
  IDLE:
    on_trigger: "START"
    next_state: "CODING"
    
  CODING:
    worker_type: "python_agent"
    script: "agents/coder.py"
    timeout_seconds: 300
    next_state: "TESTING"
    on_failure: "FAILED"

  TESTING:
    worker_type: "pytest_runner"
    script: "agents/tester.py"
    timeout_seconds: 120
    next_state: "AWAITING_APPROVAL"
    on_failure: "CODING"  # Iterasi ulang jika test gagal

  AWAITING_APPROVAL:
    require_human: true
    on_approve: "COMPLETED"
    on_reject: "CODING"
    
  COMPLETED:
    final: true

  FAILED:
    final: true
```

### 3.2. State Machine Engine
- **Mesin Status Persisten**: Logika transisi harus diimplementasikan secara framework-agnostic di tingkat core domain.
- **Penyimpanan State**: State workflow aktif disimpan di PostgreSQL. Riwayat transisi dicatat sebagai log event yang tidak dapat diubah (immutable event log).
- **Antrean Pekerjaan**: Redis digunakan untuk antrean pesan antar transisi state guna memicu Worker secara asinkron.

### 3.3. Worker Runtime (Subprocess Isolation)
- Di fase awal ini, Worker akan dijalankan menggunakan **subprocess Python terisolasi**.
- Setiap subprocess dijalankan dengan lingkungan variabel (env) yang dikurangi izinnya (restricted permissions) dan direktori kerja (working directory) sementara yang dikarantina.
- Runtime bertugas menangkap output `stdout`, `stderr`, dan berkas perubahan (diff) yang dihasilkan oleh Worker.

### 3.4. Human-In-The-Loop (HITL) Dashboard & Real-Time Sync
- **WebSocket/SSE**: Backend (FastAPI) menyediakan endpoint WebSocket untuk mengirimkan perubahan status workflow secara instan ke Frontend (React).
- **Approval UI**: Dashboard harus menampilkan:
  - Visualisasi grafik State Machine saat ini.
  - Tampilan *diff viewer* (sandingan kode sebelum vs sesudah).
  - Kolom komentar/feedback untuk instruksi revisi jika ditolak.
  - Tombol aksi: **Approve** (pindah ke state berikutnya) & **Reject** (pindah kembali ke state pengerjaan).

---

## 4. Conceptual Data Model

### 4.1. Database Schema (PostgreSQL)

1. **`workflows` Table**
   - `id`: UUID (Primary Key)
   - `name`: VARCHAR
   - `status`: VARCHAR (e.g., ACTIVE, SUSPENDED, COMPLETED)
   - `definition_yaml`: TEXT
   - `created_at`: TIMESTAMP

2. **`workflow_instances` Table**
   - `id`: UUID (Primary Key)
   - `workflow_id`: UUID (Foreign Key)
   - `current_state`: VARCHAR
   - `variables`: JSONB (Menyimpan data runtime / context)
   - `created_at`: TIMESTAMP
   - `updated_at`: TIMESTAMP

3. **`jobs` Table**
   - `id`: UUID (Primary Key)
   - `instance_id`: UUID (Foreign Key)
   - `state_name`: VARCHAR
   - `status`: VARCHAR (PENDING, RUNNING, COMPLETED, FAILED)
   - `stdout`: TEXT
   - `stderr`: TEXT
   - `started_at`: TIMESTAMP
   - `ended_at`: TIMESTAMP

4. **`state_transitions` Table (Audit Trail)**
   - `id`: UUID (Primary Key)
   - `instance_id`: UUID (Foreign Key)
   - `from_state`: VARCHAR
   - `to_state`: VARCHAR
   - `trigger_event`: VARCHAR
   - `triggered_by`: VARCHAR (SYSTEM / USER_ID)
   - `comment`: TEXT
   - `created_at`: TIMESTAMP

---

## 5. Non-Functional & Safety Requirements

### 5.1. Runtime Safety
- Pembatasan waktu eksekusi (timeout) keras pada subprocess untuk mencegah infinite loops atau hang (default: 300 detik).
- Sanitasi input command line untuk mencegah command injection pada pemanggilan subprocess Python.

### 5.2. UI Responsiveness & Sync
- Ketika user melakukan klik pada tombol "Approve", status workflow di server harus terupdate dan dasbor pengguna lain yang melihat workflow yang sama harus terupdate dalam waktu kurang dari 200ms menggunakan WebSocket.

---

## 6. Project Scope Constraints (MVP Phase)

- **In-Scope**:
  - Validasi schema YAML definisi workflow.
  - Eksekusi langkah berbasis subprocess Python lokal.
  - Endpoint WebSocket di FastAPI untuk live-sync dashboard React.
  - Fitur dasbor review persetujuan dasar (Accept/Reject).

- **Out-of-Scope**:
  - Eksekusi di container Docker/Kubernetes (direncanakan untuk Sprint 4).
  - Skema otentikasi OAuth2/SSO kompleks.

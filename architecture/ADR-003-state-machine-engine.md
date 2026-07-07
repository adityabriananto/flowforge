# ADR-003: State Machine Engine Core Design

**Status:** Approved  
**Date:** 2026-07-07  
**Deciders:** Project Lead (AI Software Development Team)  

---

## 1. Context & Problem Statement

FlowForge dirancang sebagai AI Workflow Orchestration Framework. Setiap alur kerja AI (*Workflow*) terdiri dari rangkaian langkah (*Steps*) yang merepresentasikan status (*States*) dan transisi (*Transitions*). Untuk menjaga prinsip inti **ADR-002 (Framework Agnostic Core)**, kita membutuhkan mesin status (State Machine Engine) yang tidak terikat pada kerangka kerja luar (seperti Django FSM atau library Python `transitions`) agar dapat diuji secara terisolasi dan mudah diintegrasikan dengan teknologi apa pun di masa mendatang.

Bagaimana kita mendesain dan mengimplementasikan State Machine Engine ini di tingkat Core Domain?

---

## 2. Decision & Implementation Strategy

Kami memutuskan untuk mengimplementasikan **Pure Custom Lightweight State Machine Engine** menggunakan fitur bawaan Python 3.13 standard library.

### 2.1. Desain Core Abstraction
State Machine Core akan dirancang dengan pendekatan Object-Oriented dan DDD (Domain-Driven Design), terdiri dari:
1. **`State`**: Representasi status individual dengan hooks seperti `on_enter`, `on_exit`, dan `execute`.
2. **`Transition`**: Definisi perpindahan status dari `source_state` ke `target_state` yang dipicu oleh `event`.
3. **`StateMachine`**: Orchestrator utama yang mengelola status aktif saat ini, memvalidasi transisi yang sah, dan mengeksekusi transisi.

### 2.2. Validasi Konfigurasi YAML
- Engine akan memuat skema transisi melalui definisi YAML (yang disepakati di PRD).
- Saat inisialisasi, engine akan memvalidasi keutuhan grafik transisi (mencegah jalan buntu yang tidak disengaja/unreachable states).

### 2.3. Keamanan & Exception Handling
- Transisi yang tidak valid akan memicu custom exception `InvalidTransitionError`.
- Setiap transisi harus bersifat atomik; kegagalan dalam eksekusi transisi akan mengembalikan status ke state sebelumnya (`rollback` behavior) untuk menghindari status gantung (zombie state).

---

## 3. Consequences

### 3.1. Pros (Keuntungan)
- **Zero External Dependencies**: Menjamin core engine tetap sangat ringan, cepat dipasang, dan bebas dari kerentanan keamanan pihak ketiga.
- **Framework Agnostic**: Core dapat digunakan di lingkungan CLI, FastAPI, Django, atau sistem asinkron lainnya secara konsisten.
- **Mudah Ditest**: Unit test dapat ditulis murni menggunakan `unittest` atau `pytest` standar tanpa perlu setup infrastruktur yang rumit.

### 3.2. Cons (Kerugian)
- **Custom Development Effort**: Tim pengembang backend harus menulis kode logika transisi, penanganan deadlock, dan parsing skema YAML sendiri dari awal.
- **Maintenance**: Pemeliharaan engine State Machine berada sepenuhnya di bawah kendali tim internal.

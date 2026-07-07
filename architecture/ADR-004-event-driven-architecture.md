# ADR-004: Event-Driven Architecture Design

**Status:** Approved  
**Date:** 2026-07-07  
**Deciders:** Project Lead (AI Software Development Team)  

---

## 1. Context & Problem Statement

FlowForge bekerja berdasarkan perubahan state yang dipicu oleh tindakan Worker AI atau interaksi manusia (HITL). Untuk menjaga modularitas dan memungkinkan integrasi asinkron yang aman dengan dashboard real-time dan log audit, kita membutuhkan mekanisme penyebaran event (Event Publishing & Routing) yang kuat.

Mekanisme ini harus aman (prevent race conditions), asinkron, dan scalable, serta tetap selaras dengan arsitektur bersih Hexagonal.

---

## 2. Decision & Implementation Strategy

Kami memutuskan untuk merancang arsitektur event-driven menggunakan pola **Ports & Adapters (Hexagonal Architecture)**. 

### 2.1. Abstraksi Core Domain (Ports)
Kami membuat interface abstrak murni di tingkat core domain:
- **`EventPublisher` (Port)**: Definisikan metode `publish(event: Event) -> None`.
- **`EventSubscriber` (Port)**: Definisikan metode `subscribe(event_type: str, handler: Callable) -> None`.

Setiap event diwakili oleh struktur data immutable (misal: Python `@dataclass` atau Pydantic model) yang membawa `event_id`, `timestamp`, `event_type`, dan `payload`.

### 2.2. Implementasi Runtime (Adapters)

1. **`InMemoryEventBus` (Development & Testing)**
   - *Teknologi*: Menggunakan `asyncio.Queue` dari pustaka standar Python.
   - *Penggunaan*: Dipakai untuk pengujian unit terisolasi (unit testing) dan eksekusi lokal tanpa dependensi eksternal. Sangat aman dan tidak memerlukan overhead jaringan.

2. **`RedisEventBus` (Production & Multi-process)**
   - *Teknologi*: Menggunakan Redis Pub/Sub melalui driver asinkron `redis-py`.
   - *Penggunaan*: Digunakan untuk lingkungan produksi di mana backend FastAPI, Worker runner, dan dashboard berjalan di proses atau server yang berbeda. Redis Pub/Sub menjamin penyampaian pesan real-time berlatensi sangat rendah (< 10ms).
   - *Keamanan*: Koneksi ke Redis harus menggunakan protokol terenkripsi (rediss://) dengan otentikasi password/token yang kuat.

---

## 3. Consequences

### 3.1. Pros (Keuntungan)
- **High Modularity & Scalability**: Memisahkan backend FastAPI dan runtime worker secara longgar (loosely coupled) melalui pesan event.
- **Portability**: Kita bisa mengganti adapter in-memory dengan Redis Pub/Sub di konfigurasi produksi tanpa perlu memodifikasi kode logika State Machine utama.
- **Testability**: QA Engineer dapat dengan mudah mem-mock `EventPublisher` untuk menguji fungsionalitas domain tanpa memerlukan Redis server yang menyala.

### 3.2. Cons (Kerugian)
- **Kompleksitas Kode**: Pola Port & Adapters membutuhkan pendefinisian interface abstrak tambahan, yang sedikit meningkatkan jumlah baris kode awal.
- **Eventual Consistency**: Transisi status asinkron berarti data di dasbor frontend mungkin mengalami keterlambatan beberapa milidetik dibandingkan dengan kondisi database utama (tapi masih dalam batas toleransi < 200ms).

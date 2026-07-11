# AI Contribution Guide

## Objective

Semua AI harus mengikuti aturan yang sama agar hasil konsisten.

## Startup Checklist

-   Baca README.md
-   Baca STATUS.md
-   Baca ROADMAP.md
-   Baca seluruh dokumen sprint aktif
-   Jangan mulai coding jika sprint belum mengizinkan.

## Roles

### Architect

-   Mendesain solusi
-   Membuat ADR
-   Tidak mengimplementasikan kode

### Engineer

-   Mengimplementasikan task
-   Menambah test
-   Tidak mengubah arsitektur

### Reviewer

-   Review kualitas kode
-   Review security
-   Review performance

## Rules

-   Jangan menambah dependency tanpa approval.
-   Jangan mengubah stack tanpa approval.
-   Semua keputusan arsitektur harus menjadi ADR.
-   Semua perubahan harus mengacu pada sprint aktif.
-   Update dokumen yang relevan setelah pekerjaan selesai.

## Branch Strategy

Sesuai dengan *Core Freeze Policy*, repositori ini mengadopsi strategi dua branch jangka panjang:

-   **`main`**: Merepresentasikan *stable FlowForge Core*. Hanya bug fix kritis, perbaikan sekuritas, perbaikan dokumentasi, dan optimasi performa yang boleh di-*merge* ke sini. TIDAK menerima fitur eksperimental apa pun.
-   **`next`**: Merepresentasikan masa depan ekosistem FlowForge. Segala fitur baru yang bersifat opsional (Dashboard, VS Code Extension, Cloud, AI-assisted Planning, Marketplace, dll) dikembangkan dan divalidasi pada branch ini.

## Tech Stack

Backend: Python + FastAPI Frontend: React + TypeScript Database:
PostgreSQL Queue: Redis ORM: SQLAlchemy

# FlowForge Workspace Documentation (v1.0.0)

Dokumentasi ini menjelaskan standar struktur direktori untuk memisahkan file rekayasa orisinal dengan file temporer runtime.

## Struktur Folder

### 1. `engineering/`
Pusat seluruh aset rekayasa yang bersifat editable dan persisten:
- `missions/`: Spesifikasi misi otonom (`backlog`, `active`, `completed`).
- `missions/templates/`: Template yang di-version untuk Misi, RFC, ADR, Sprint, dan Review.
- `reports/`: Laporan eksekusi misi dari agen AI.
- `rfcs/`: Dokumen usulan fitur teknis.
- `adrs/`: Catatan keputusan arsitektural.
- `roadmap/`: Rencana sprint.
- `architecture/`: Desain sistem dan diagram.
- `decisions/`: Berkas `AGENTS.md` (Engineering Rules).

### 2. `.flowforge/`
Berkas runtime ephemera otomatis (di-ignore oleh git secara default):
- `packages/`: Plugin terunduh / compiled mission packages.
- `providers/`: Konfigurasi provider dan raw `api_key`.
- `cache/`: Cache eksekusi.
- `workspace/`: Workspace sandbox isolasi.
- `logs/`: Logs mentah.

## Contoh Eksekusi Perpindahan Misi
Developer/Runtime dapat memicu transisi file misi dengan:
```python
from flowforge.services.workspace.engineering_workspace import EngineeringWorkspace

# Inisialisasi struktur folder awal
EngineeringWorkspace.initialize_workspace()

# Pindahkan file dari backlog ke active
EngineeringWorkspace.move_mission_file("mission_1.yaml", "backlog", "active")
```

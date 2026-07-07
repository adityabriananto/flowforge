# RFC-004: Prompt Pipeline

## Status
PROPOSED

## Konsep Utama
Mengubah Prompt Builder menjadi **PromptPipeline** deterministic. Pipeline memuat data-data pendukung secara bertahap dan chain-linked untuk meminimalisasi overhead context.

## Tahapan Pemrosesan Pipeline
```
Input Prompt Template
    ↓
1. Workspace File Loader   (Memuat snippet file lokal terkait)
    ↓
2. Memory Loader           (Memuat lesson learned & historical memory)
    ↓
3. Artifact Loader         (Memuat berkas-berkas artifact AI versi terkontrol)
    ↓
4. Git Diff Loader         (Memuat status git diff terakhir)
    ↓
Output Final Formatted Prompt
```
Hal ini memastikan instruksi LLM terfokus pada context state aktif dan log QA error yang tepat.

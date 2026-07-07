# RFC-005: Lesson Learned Memory Engine

## Status
PROPOSED

## Konsep Utama
AI Agent harus memiliki kemampuan untuk self-improve/belajar dari eksekusi alur kerja masa lalu. Lesson Learned Memory Engine secara otomatis merekam histori keberhasilan dan kegagalan task di repositori.

## Aliran Pembelajaran
```
Workflow Run Completed
    ↓
Analyze Execution Logs / QA Results
    ↓
Extract Lessons Learned ("Lessons learned: close DB session in finally block")
    ↓
Persist to .project/memory/lessons.json
    ↓
Inject lessons learned to Prompt Pipeline of next workflow instances
```
Ini memastikan agent tidak mengulangi kesalahan yang sama pada eksekusi runtime berikutnya.

# Resumen de Métricas — Evaluación NER

**Matching:** comparación por texto exacto tras normalizar espacios y guiones inconsistentes. Sin cambios de mayúsculas/minúsculas. Métricas micro-promediadas sobre 8 documentos.

| Modelo | PER F1 | ORG F1 | PROJ F1 | Total F1 |
|---|---|---|---|---|
| groq/llama-3.3-70b-versatile | 0.9565 | 0.9200 | 1.0000 | **0.9489** |
| Qwen/Qwen2.5-7B-Instruct | 0.9565 | 0.8511 | 0.8571 | **0.9051** |
| kalawinka/flair-ner-acknowledgments | 0.7937 | 0.5778 | 1.0000 | **0.7460** |
| Jean-Baptiste/roberta-large-ner-english | 0.6857 | 0.6182 | 0.0000 | **0.6119** |

**Ganador:** groq/llama-3.3-70b-versatile (Total F1 = 0.9489)

El detalle completo (TP/FP/FN por paper, por categoría, entidades concretas) está en `evaluation_report.json`.

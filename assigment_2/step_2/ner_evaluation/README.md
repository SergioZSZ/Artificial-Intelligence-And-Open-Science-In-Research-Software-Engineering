# Evaluación de Modelos NER — Acknowledgements

## 1. Resumen

Este proyecto evalúa 4 modelos de NER para extraer personas (PER), organizaciones (ORG) y códigos de proyecto (PROJ) de los agradecimientos de 30 papers académicos. Comparamos modelos clásicos y LLMs contra un gold standard de 8 papers anotados a mano. **El ganador es `groq/llama-3.3-70b-versatile` con un F1 de 0.9489.**

---

## 2. Modelos evaluados

| Modelo | Enfoque | ¿Detecta proyectos? |
|---|---|---|
| Jean-Baptiste/roberta-large-ner-english | NER clásico (baseline). El que enseña el profesor. | No (no tiene etiqueta para códigos) |
| kalawinka/flair-ner-acknowledgments | NER especializado en agradecimientos científicos (Flair). | Sí |
| groq/llama-3.3-70b-versatile | LLM grande vía API de Groq. | Sí |
| Qwen/Qwen2.5-7B-Instruct | LLM pequeño de familia distinta (Qwen), vía HuggingFace. | Sí |

---

## 3. Requisitos

- Python 3.11+ con Poetry
- Una clave de Groq (https://console.groq.com) — necesaria para el modelo 03
- Un token de HuggingFace (https://huggingface.co/settings/tokens) — necesario para el 04

Los modelos 01 y 02 se ejecutan localmente sin API key.

---

## 4. Cómo ejecutar

```bash
# 1. Instalar dependencias
poetry install

# 2. Configurar claves (nunca commits .env, solo .env.example)
cp .env.example .env
# Editar .env y poner GROQ_API_KEY y HF_TOKEN

# 3. Ejecutar las predicciones (en cualquier orden, 01-04)
poetry run python scripts/01_predict_jean_baptiste.py
poetry run python scripts/02_predict_kalawinka.py
poetry run python scripts/03_predict_groq.py
poetry run python scripts/04_predict_hf_inference.py

# 4. Evaluar (necesita los 4 anteriores)
poetry run python scripts/05_evaluate.py
```

---

## 5. Entradas y salidas

- **Gold standard:** `corpus/gold_standard.json` en la raíz del repo (8 papers anotados a mano con PER/ORG/PROJ).
- **Predicciones:** `predictions/jean_baptiste.json`, `kalawinka.json`, `groq.json`, `hf_inference.json`.
- **Informes:** `reports/evaluation_report.json` (métricas por modelo y por paper) y `evaluation_report.md` (tabla resumen).
- **Informe narrativo:** `reports/ner_evaluation_report.md` (explicación completa, escrito a mano).

---

## 6. Decisiones técnicas clave

- **Prompt compartido.** Los dos LLMs (Groq y Qwen) usan el mismo prompt. Así la diferencia entre ellos se debe al modelo, no al prompt.
- **Comparación por texto.** Las predicciones se comparan con el gold standard como listas de texto (no por posición en el documento). Solo normalizamos espacios y guiones inconsistentes: no pasamos a minúsculas ni quitamos puntuación para no romper códigos de proyecto.
- **Métricas micro-promediadas.** Sumamos todos los aciertos y fallos de los 8 papers y calculamos precisión/recall/F1 sobre el total. Cada entidad pesa igual.
- **LLMs con temperature=0.** Para que las respuestas sean lo más deterministas posible.

El informe narrativo (`reports/ner_evaluation_report.md`) explica estas decisiones con más detalle.

---

## 7. Estructura de carpetas

```
ner_evaluation/
├── scripts/           Código de los 4 modelos + evaluación + utilidades
├── predictions/       Salidas de cada modelo (JSON)
├── reports/           Informe de métricas (generado) + informe narrativo (manual)
├── docs/              Declaración de uso de IA
├── pyproject.toml     Dependencias (entorno aislado del resto del repo)
├── poetry.lock
├── .env               Claves (no versionado)
├── .env.example       Plantilla para .env
├── .gitignore
└── README.md
```

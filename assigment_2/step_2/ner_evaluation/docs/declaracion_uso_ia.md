# Declaración de uso de IA — Evaluación NER (Acknowledgements)

**Proyecto:** G4_OPENSCIENCE — Knowledge Graph for Research Publications
**Asignatura:** Open Science and Artificial Intelligence in Research Software Engineering, ETSI Informáticos, Universidad Politécnica de Madrid
**Componente:** Evaluación y selección de modelo NER sobre la sección de Acknowledgements (Entregable 2)

---

## 1. Propósito de este documento

El uso de IA en este proyecto es obligatorio declararlo. Este documento registra qué modelos de IA se emplearon, con qué parámetros, y para qué.

Hay que distinguir dos usos de IA:
1. **La IA como objeto de estudio:** dos de los cuatro modelos evaluados son LLMs (Groq y Qwen). Su evaluación es el núcleo de la fase.
2. **La IA como herramienta de apoyo:** se usó un asistente conversacional para redactar el informe y la documentación (sección 5).

---

## 2. Modelos de IA evaluados

### 2.1. Jean-Baptiste/roberta-large-ner-english

- **Tipo:** NER clásico (RoBERTa-large, clasificación de tokens).
- **Acceso:** local con `transformers`. Es el baseline (el que el profesor usa en clase).
- **Etiquetas:** PER/ORG/LOC/MISC. LOC y MISC se descartan. No tiene etiqueta para códigos de proyecto.

### 2.2. kalawinka/flair-ner-acknowledgments

- **Tipo:** NER especializado en agradecimientos científicos (Flair). Referencia: Smirnova & Mayr, arXiv:2307.13377.
- **Acceso:** local con `flair`.
- **Etiquetas:** 6 nativas mapeadas a 3: IND→PER; UNI/FUND/COR→ORG; GRNB→PROJ; MISC descartado.

### 2.3. groq/llama-3.3-70b-versatile

- **Tipo:** LLM de 70B parámetros vía API de Groq. Temperature=0, JSON mode.
- **Prompt:** compartido con Qwen (mismo system prompt + ejemplo one-shot ficticio).
- **Función:** representa el enfoque LLM. Reproduce el método que el profesor muestra en clase.

### 2.4. Qwen/Qwen2.5-7B-Instruct

- **Tipo:** LLM de 7B parámetros vía HuggingFace Inference Providers. Temperature=0, max_tokens=1024, JSON mode.
- **Prompt:** idéntico al de Groq. Decisión metodológica: al usar el mismo prompt, la diferencia entre ambos se debe al modelo, no al prompt.

---

## 3. Datos de entrada

- **Gold standard:** `corpus/gold_standard.json` — 8 agradecimientos anotados a mano (paper_03, 07, 09, 11, 13, 19, 27, 28).
- **Guía de anotación:** `corpus/ANNOTATION_GUIDELINES.md`.
- La anotación fue manual (dos anotadores en sesión de consenso). Ninguna IA participó en crear el gold standard.

---

## 4. Fechas de ejecución

- Predicciones (scripts 01–04): 14–16 de mayo de 2026
- Evaluación (script 05): 16 de mayo de 2026

> La fecha importa porque los modelos vía API (Groq, HuggingFace) pueden actualizarse, y los LLMs no garantizan resultados idénticos entre ejecuciones aunque usen temperature=0. Las métricas corresponden a una única ejecución por modelo.

---

## 5. Uso de IA en la generación de scripts

Los scripts del directorio `scripts/` se generaron con IA generativa, revisados durante su desarrollo por el Grupo 4 de OpenScience.

## 6. Uso de IA en la redacción de la documentación

Para redactar el informe narrativo (`reports/ner_evaluation_report.md`), este documento y el README se usó un asistente conversacional de IA como herramienta de apoyo. Alcance del uso:

- Ayudó a **estructurar y redactar** los textos.
- Todos los **datos numéricos** (TP/FP/FN, precisión, recall, F1) proceden exclusivamente de la ejecución de los scripts y de `reports/evaluation_report.json`. No fueron generados por la IA.
- Las **decisiones de diseño** (modelos elegidos, política de matching, métricas, prompt compartido) las tomó el equipo, no la IA.
- El **análisis cualitativo de errores** se basa en las entidades concretas de `evaluation_report.json`. La IA ayudó a redactarlo, pero los errores descritos son los que aparecen en los datos.
- Los autores **revisaron y validaron** todo el contenido.

---

## 7. Problemas técnicos resueltos

Durante la puesta en marcha del entorno se resolvieron tres conflictos de dependencias. Se documentan por trazabilidad y reproducibilidad.

### 7.1. Flair y PyTorch 2.6

PyTorch 2.6 cambió `torch.load` a `weights_only=True` por defecto, bloqueando la carga del modelo de Flair.

**Solución:** parchear `torch.load` al inicio del script para forzar `weights_only=False`. Seguro porque el modelo es de un repositorio académico conocido (kalawinka, arXiv:2307.13377).

### 7.2. SDK de Groq y httpx

La versión 0.11.0 del SDK `groq` era incompatible con `httpx` moderno.

**Solución:** actualizar a groq 1.2.0 con `poetry add "groq@latest"`.

### 7.3. transformers y huggingface-hub

`huggingface-hub` 1.x es incompatible con `transformers`. La versión 0.25 usaba un endpoint ya retirado (error 404).

**Solución:** fijar `huggingface-hub@^0.34.0`, que usa el router actual y es compatible con `transformers`.

---

## 8. Reproducibilidad

- Dependencias y versiones exactas en `pyproject.toml` y `poetry.lock`.
- Credenciales (GROQ_API_KEY, HF_TOKEN) en `.env` local (no versionado). Se incluye `.env.example` como plantilla.
- Limitación: los modelos vía API pueden actualizarse sin aviso, y los LLMs no son 100% deterministas. Los modelos locales (01, 02) sí son deterministas.

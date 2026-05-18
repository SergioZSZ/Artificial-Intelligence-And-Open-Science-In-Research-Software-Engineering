# Declaración de uso de IA — Evaluación NER (Acknowledgements)

**Proyecto**: G4_OPENSCIENCE — Knowledge Graph for Research Publications
**Asignatura**: Open Science and Artificial Intelligence in Research Software
Engineering, ETSI Informáticos, Universidad Politécnica de Madrid
**Componente**: Evaluación y selección de modelo NER sobre la sección de
Acknowledgements (Entregable 2)

---

## 1. Propósito de este documento

El uso de modelos de IA en este proyecto es obligatorio declararlo. Este
documento registra, de forma trazable, qué modelos de IA se han empleado en
la evaluación NER, con qué parámetros, con qué entradas, y los problemas
técnicos encontrados y resueltos durante el proceso.

Conviene distinguir dos usos de IA, ambos documentados aquí:

1. **La IA como objeto de estudio**: dos de los cuatro modelos evaluados son
   modelos de lenguaje grandes (LLMs). Su uso es el núcleo de esta fase.
2. **La IA como herramienta de apoyo**: se ha usado un asistente conversacional
   para la redacción del informe y de la documentación (ver sección 5).

---

## 2. Modelos de IA evaluados

Se evaluaron cuatro modelos NER. Los dos primeros son modelos de
clasificación de tokens que se ejecutan localmente; los dos últimos son LLMs
accedidos vía API.

### 2.1. Jean-Baptiste/roberta-large-ner-english

- **Tipo**: NER clásico (RoBERTa-large, clasificación de tokens).
- **Acceso**: ejecución local mediante la librería `transformers`.
- **Función en el proyecto**: modelo de referencia (baseline). Es el ejemplo
  que el profesor utiliza en la Sesión 11 (slide 22).
- **Etiquetas**: `PER / ORG / LOC / MISC`. Las etiquetas `LOC` y `MISC` se
  descartan. El modelo no dispone de etiqueta para códigos de proyecto.

### 2.2. kalawinka/flair-ner-acknowledgments

- **Tipo**: NER especializado en acknowledgements científicos (Flair).
- **Referencia**: Smirnova & Mayr, arXiv:2307.13377.
- **Acceso**: ejecución local mediante la librería `flair`.
- **Función en el proyecto**: representa el enfoque de especialización de
  dominio.
- **Etiquetas**: 6 etiquetas nativas mapeadas a 3 categorías —
  `IND` → PER; `UNI`, `FUND`, `COR` → ORG; `GRNB` → PROJ; `MISC` se descarta.

### 2.3. groq/llama-3.3-70b-versatile

- **Tipo**: LLM (Llama 3.3, 70.000 millones de parámetros).
- **Acceso**: API de Groq (https://groq.com/). Requiere `GROQ_API_KEY`.
- **Función en el proyecto**: representa el enfoque LLM. Reproduce el método
  que el profesor muestra en la Sesión 11 (slides 19-20).
- **Parámetros de inferencia**:
  - `temperature = 0`
  - Modo de salida JSON (JSON mode)
- **Prompt**: prompt compartido (`scripts/prompt_ner.py`), idéntico al usado
  con el modelo 2.4. Consta de un *system prompt* que codifica las reglas de
  anotación del gold standard y un ejemplo *one-shot* con entidades ficticias
  (inventadas, no presentes en los 8 papers evaluados).

### 2.4. Qwen/Qwen2.5-7B-Instruct

- **Tipo**: LLM (Qwen 2.5 Instruct, 7.000 millones de parámetros).
- **Acceso**: HuggingFace Inference Providers. Requiere `HF_TOKEN`.
- **Función en el proyecto**: segundo LLM, de familia distinta a Llama, para
  comprobar si el resultado del enfoque LLM generaliza entre familias de
  modelos.
- **Parámetros de inferencia**:
  - `temperature = 0`
  - `max_tokens = 1024`
  - Modo de salida JSON (JSON mode)
- **Prompt**: el mismo prompt compartido que el modelo 2.3. El uso de un
  prompt idéntico para ambos LLMs es una decisión metodológica deliberada:
  aísla el modelo como única variable de la comparación LLM-vs-LLM.

---

## 3. Datos de entrada

- **Gold standard**: `corpus/gold_standard.json` — 8 acknowledgements anotados
  manualmente (`paper_03, 07, 09, 11, 13, 19, 27, 28`).
- **Guía de anotación**: `corpus/ANNOTATION_GUIDELINES.md`.
- La anotación fue realizada manualmente por dos anotadores en sesión de
  consenso. Ningún modelo de IA participó en la creación del gold standard;
  es la verdad de referencia (*ground truth*) frente a la que se miden los
  modelos.

---

## 4. Fechas de ejecución


     - Predicciones (scripts 01-04): [14-05-2026] [15-05-2026] [16-05-2026]
     - Evaluación (script 05):       [16-05-2026]
     Si los modelos se ejecutaron en fechas distintas, indicarlo. -->

- Predicciones (`01`–`04`): _pendiente de completar_
- Evaluación (`05`): _pendiente de completar_

> La fecha de ejecución es relevante porque los modelos accedidos vía API
> (Groq, HuggingFace) pueden actualizarse por parte del proveedor, y porque
> los LLMs no garantizan resultados idénticos entre ejecuciones (ver
> Sesión 11, slide 18). Las métricas reportadas corresponden a una única
> ejecución por modelo.

---
## 5. Uso de IA en la generación de scripts

Los scripts del directorio `/scripts` fueron generados con IA generativa, revisados durante su generación por el grupo 4 de OpenScience.


## 6. Uso de IA en la redacción de la documentación

Para la redacción del informe narrativo (`reports/ner_evaluation_report.md`),
de este documento y del `README.md` se ha utilizado un asistente
conversacional de IA como herramienta de apoyo.

Alcance de ese uso, para que quede claro:

- El asistente ayudó a **estructurar y redactar** los textos.
- Todos los **datos numéricos** (TP/FP/FN, precision, recall, F1) proceden
  exclusivamente de la ejecución de los scripts y del fichero
  `reports/evaluation_report.json`. No fueron generados ni estimados por la
  IA.
- Las **decisiones de diseño** de la evaluación (los cuatro modelos, la
  política de matching, las métricas micro-averaged, el prompt compartido)
  fueron tomadas por el equipo, no por la IA.
- El **análisis cualitativo de errores** se basa en las entidades concretas
  registradas en `evaluation_report.json`; la IA ayudó a redactarlo, pero los
  errores descritos son los que aparecen en los datos.
- Los autores han **revisado y validado** todo el contenido redactado.

---

## 7. Problemas técnicos encontrados y resueltos

Durante la puesta en marcha del entorno se resolvieron tres conflictos de
dependencias. Se documentan aquí por trazabilidad y porque afectan a la
reproducibilidad del experimento.

### 7.1. Flair y PyTorch 2.6

PyTorch 2.6 cambió el valor por defecto de `torch.load` a
`weights_only=True`, lo que impedía cargar el modelo de Flair
(`02_predict_kalawinka.py`).

**Solución**: se parchea `torch.load` para forzar `weights_only=False` al
inicio del script. Es una solución segura en este caso, dado que el modelo
procede de un repositorio académico conocido (kalawinka, asociado a la
publicación arXiv:2307.13377).

### 7.2. SDK de Groq y httpx

La versión `0.11.0` del SDK `groq` era incompatible con versiones modernas de
`httpx` (error: `unexpected keyword argument 'proxies'`).

**Solución**: actualización del SDK con `poetry add "groq@latest"`, que
instaló la versión `1.2.0`, compatible.

### 7.3. transformers y huggingface-hub

`huggingface-hub` 1.x es incompatible con `transformers` (que requiere
`huggingface-hub < 1.0`). Además, una versión antigua (`0.25`) usaba el
endpoint ya retirado `api-inference.huggingface.co`, que devolvía error 404.

**Solución**: instalación de una versión intermedia con
`poetry add "huggingface-hub@^0.34.0"`. La versión `0.34` utiliza el router
actual (`router.huggingface.co`) y es compatible con `transformers`.

---

## 8. Reproducibilidad

- Las dependencias y sus versiones exactas están fijadas en `pyproject.toml`
  y `poetry.lock`.
- Las credenciales (`GROQ_API_KEY`, `HF_TOKEN`) se gestionan mediante un
  fichero `.env` local, no versionado. Se proporciona `.env.example` como
  plantilla.
- Limitación de reproducibilidad: los modelos accedidos vía API pueden ser
  actualizados por el proveedor sin previo aviso, y los LLMs no garantizan
  resultados idénticos entre ejecuciones aun con `temperature=0`. Los modelos
  NER locales (`01`, `02`) sí son deterministas.

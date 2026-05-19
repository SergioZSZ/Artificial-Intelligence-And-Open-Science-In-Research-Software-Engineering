# Informe de Evaluación de Modelos NER — Fase 5c

**Proyecto:** G4_OPENSCIENCE — Knowledge Graph for Research Publications
**Asignatura:** Open Science and AI in RSE, ETSI Informáticos, Universidad Politécnica de Madrid
**Grupo:** https://github.com/SergioZSZ/OS-IA-Pipegrobid

---

## 1. ¿Qué necesitábamos y por qué?

Necesitamos un modelo de NER (Reconocimiento de Entidades Nombradas) para extraer automáticamente **personas, organizaciones y códigos de proyecto** de la sección de agradecimientos de 30 papers académicos. Estos datos irán después a nuestro Grafo de Conocimiento.

Antes de aplicar un modelo a los 30 papers, teníamos que elegir cuál usar y justificar la decisión. El profesor exige (Sesión 11, diapositiva 26) comparar modelos y medir su rendimiento sobre datos anotados por nosotros mismos, calculando precisión, recall y F1.

Este informe documenta esa comparación y explica por qué elegimos **groq/llama-3.3-70b-versatile**.

### Las 3 categorías de entidades

| Categoría | ¿Qué incluye? | Ejemplos |
|---|---|---|
| PER | Personas mencionadas en los agradecimientos | "SS", "A.-F. B.", "xlr8harder", "Prof. C.Z. Zhang" |
| ORG | Organizaciones, financiadores, fundaciones, programas marco | "National Science Foundation", "Horizon 2020", "ERC" |
| PROJ | Solo códigos alfanuméricos de proyecto/grant | "IIS-2229876", "851173", "EP/S023356/1" |

---

## 2. Los 4 modelos evaluados

Elegimos 4 modelos que representan 4 enfoques distintos. Dos son los mismos que el profesor usa en clase (Jean-Baptiste y Groq); los otros dos amplían la comparación.

| Modelo | Enfoque | ¿Detecta PROJ? | Por qué lo incluimos |
|---|---|---|---|
| Jean-Baptiste/roberta-large-ner-english | NER clásico (baseline) | No (no tiene esa etiqueta) | Es el ejemplo que pone el profesor. Responde a: ¿un NER genérico sirve? |
| kalawinka/flair-ner-acknowledgments | NER especializado en agradecimientos | Sí | Está entrenado específicamente en textos como los nuestros. ¿Gana la especialización? |
| groq/llama-3.3-70b-versatile | LLM vía API (70B parámetros) | Sí | Es el enfoque LLM que muestra el profesor. |
| Qwen/Qwen2.5-7B-Instruct | LLM vía API (7B parámetros) | Sí | ¿El resultado LLM se mantiene en otra familia de modelos más pequeña? |

**Nota importante sobre Jean-Baptiste:** no tiene etiqueta para códigos de proyecto, así que su PROJ siempre será 0. Esto no es un fallo del modelo, sino un dato importante: antes de usar un modelo hay que comprobar si soporta las categorías que necesitas.

---

## 3. Cómo medimos (metodología)

### 3.1. El Gold Standard

Anotamos a mano 8 papers (paper_03, 07, 09, 11, 13, 19, 27, 28). Los elegimos para cubrir distintos tipos de agradecimiento: desde una línea con un solo financiador (paper_03) hasta un párrafo denso con 19 personas y 5 organizaciones (paper_28).

Reglas de anotación (detalladas en `corpus/ANNOTATION_GUIDELINES.md`):
- Anotamos el texto exacto, sin expandir iniciales ni inferir entidades.
- Sigla y nombre completo son dos entidades separadas ("National Eye Institute" + "NEI").
- Solo códigos alfanuméricos van a PROJ (no "Horizon 2020", que es ORG).

### 3.2. Cómo comparamos predicciones

Cada modelo predice una lista de entidades por categoría. Comparamos esas listas con el gold standard después de una normalización ligera:
- Quitar espacios al inicio/final
- Colapsar espacios múltiples
- Normalizar guiones solo cuando el espaciado es inconsistente

**No** pasamos a minúsculas ni quitamos puntuación. Esto es importante para no romper los códigos de proyecto (ej. "EP/S023356/1").

La comparación es por **conjuntos de texto**, no por posición en el documento. Esto es una limitación: si una entidad aparece dos veces en el mismo texto, se cuenta una sola vez. En nuestro corpus esto no afecta a los resultados.

### 3.3. Métricas

Por cada categoría de cada paper contamos:
- **TP (True Positive):** el modelo predijo la entidad y está en el gold standard.
- **FP (False Positive):** el modelo predijo algo que no está en el gold (alucinación, span incorrecto, categoría equivocada).
- **FN (False Negative):** el modelo no predijo algo que sí está en el gold.

Con esos números calculamos:
- **Precisión = TP / (TP + FP):** de lo que predijo el modelo, ¿cuánto es correcto?
- **Recall = TP / (TP + FN):** de lo que realmente hay, ¿cuánto encontró el modelo?
- **F1:** media armónica de precisión y recall.

Las métricas son **micro-promediadas**: sumamos TP/FP/FN de los 8 papers y calculamos sobre el total. Así los papers largos pesan más, que es lo que queremos.

### 3.4. Limitaciones del método

- **Solo 8 documentos.** Suficientes para ver diferencias claras, pero los valores absolutos son orientativos.
- **Sin offsets de posición.** Si un nombre aparece dos veces, el conjunto lo cuenta como uno. En nuestro corpus no pasa, pero es una limitación real.
- **Los LLMs no son 100% deterministas.** Los ejecutamos con temperature=0 para minimizarlo, pero la API podría dar resultados distintos en otra ejecución.
- **La ventaja del prompt.** Los LLMs reciben las reglas de anotación en el prompt; los modelos NER no. Esto se discute en la sección 7.

---

## 4. Resultados

### Ranking

| Modelo | PER F1 | ORG F1 | PROJ F1 | Total F1 |
|---|---|---|---|---|
| groq/llama-3.3-70b-versatile | 0.9565 | 0.9200 | 1.0000 | **0.9489** |
| Qwen/Qwen2.5-7B-Instruct | 0.9565 | 0.8511 | 0.8571 | **0.9051** |
| kalawinka/flair-ner-acknowledgments | 0.7937 | 0.5778 | 1.0000 | **0.7460** |
| Jean-Baptiste/roberta-large-ner-english | 0.6857 | 0.6182 | 0.0000 | **0.6119** |

**Datos clave del ganador (Groq):** 65 aciertos (TP), 3 falsos positivos, 4 falsos negativos en total.

### ¿Qué nos dicen los números?

1. **Los dos LLMs ganan claramente.** La diferencia con los modelos NER no es pequeña: 0.9489 vs 0.7460 vs 0.6119.
2. **La especialización no ganó.** Kalawinka (entrenado en agradecimientos) supera al baseline genérico, pero queda lejos de los LLMs.
3. **PROJ divide a los modelos.** Groq y Kalawinka tienen un 1.0 perfecto. Jean-Baptiste, 0.0 (por diseño, no por fallo). Qwen, 0.8571 (encuentra todos los códigos pero mete 3 que no lo son).
4. **ORG es lo más difícil.** Todos los modelos puntúan más bajo en organizaciones, porque son spans largos con nombres compuestos, siglas, y estructuras complejas.

---

## 5. ¿Qué falló cada modelo?

### 5.1. Jean-Baptiste (F1 total 0.6119)

**Problemas principales:**
- No puede detectar proyectos (0% por diseño). Pierde 9 códigos.
- Confunde iniciales de personas con organizaciones ("SS", "LM" → ORG).
- La tokenización genera ruido: suelta puntos sueltos (".") como entidades y fragmentos sin sentido ("ation on", "E").
- Errores de límite: "xlr8harder" → "lr8harder" (pierde la primera letra), "Prof. C.Z. Zhang" → "C.Z. Zhang" (pierde el título).

**En resumen:** 24 falsos positivos, 28 falsos negativos. No es mal modelo, pero no está hecho para esta tarea.

### 5.2. Kalawinka (F1 total 0.7460)

**Problemas principales:**
- Une sigla con nombre completo: "European Research Council (ERC)" como una sola entidad, cuando el gold las separa. Esto le cuesta 4 FN + 2 FP solo en paper_13.
- Organizaciones unidas por "y" las parte mal: "Research Corporation for Science Advancement and Arnold" como una entidad, "Mabel Beckman Foundation" como otra. Ambas incorrectas.
- Recorta iniciales: "A.-F. B." → "F. B.", "C. Lawrence Zitnick" → "Lawrence Zitnick".

**Matiz importante:** Parte de sus errores en ORG no son ceguera del modelo, sino que su convención de anotación (con la que fue entrenado) es distinta a la nuestra. Si el gold standard usara su misma convención, algunos de esos errores serían aciertos.

### 5.3. Qwen 2.5 7B (F1 total 0.9051)

**Problemas principales:**
- En paper_27 mete 3 cosas en PROJ que no lo son: "SAB" (una persona), "Simons Foundation..." y "Schmidt Sciences..." (organizaciones). El prompt dice claramente que PROJ son solo códigos alfanuméricos.
- En paper_11 alucina "J.K.", una entidad que solo existe en el ejemplo ficticio del prompt. El modelo copió el ejemplo a la respuesta.
- Se pierde 5 organizaciones que Groq sí encuentra (ORG F1 0.8511 vs 0.9200).

**En resumen:** Es un buen modelo, pero sus errores son los peores para producción porque **introduce datos falsos** (no solo omisiones).

### 5.4. Groq Llama 3.3 70B (F1 total 0.9489) — Ganador

**Solo 4 errores en todo el corpus:**

| Paper | Error | Tipo |
|---|---|---|
| paper_09 | Predice "UKRI" como ORG extra | FP (no está en el gold) |
| paper_11 | "C.Z. Zhang" en vez de "Prof. C.Z. Zhang" | Pierde el título (1 FP + 1 FN) |
| paper_19 | No encuentra "national SARS-CoV-2 biosurveillance initiative" | FN (organización en minúscula, difícil de detectar) |
| paper_27 | "Stanford Medicine Post-Baccalaureate Experience In Research" sin "program" | Error de límite (1 FP + 1 FN) |

**Lo que NO hace:** no alucina entidades, no confunde categorías, no fragmenta palabras, no suelta puntos sueltos. Su PROJ es perfecto (9/9, 0 falsos positivos).

---

## 6. Modelo ganador y por qué

Elegimos **groq/llama-3.3-70b-versatile** por 4 razones:

1. **Mejor F1 total (0.9489).** Gana por 4 puntos al segundo (Qwen) y por 20+ a los NER clásicos.
2. **Equilibrado en las 3 categorías.** No cojea en ninguna, a diferencia de los demás (Kalawinka se hunde en ORG, Jean-Baptiste no hace PROJ, Qwen confunde PROJ).
3. **El perfil de error más limpio.** 3 FP y 4 FN en total. No alucina, no confunde categorías. Es fiable para ejecutarlo sin supervisión sobre los 30 papers.
4. **Fácil de desplegar.** Solo una API key, sin GPU, sin descargar modelos, sin entrenar. Es el mismo enfoque que el profesor muestra en clase.

**Sobre el segundo clasificado (Qwen):** Qwen confirma que la estrategia LLM funciona en más de una familia de modelos. Pero no lo elegimos porque sus errores (confundir categorías, alucinar entidades del prompt) son los peores para un pipeline automatizado: meten datos falsos en el grafo.

---

## 7. Una cosa importante: los LLMs parten con ventaja (y está bien)

Los dos LLMs recibieron un prompt que **les enseña las reglas exactas del gold standard**: qué es PROJ y qué no, que las siglas van separadas, que no se expanden iniciales, etc. Los modelos NER (Jean-Baptiste, Kalawinka) no pueden recibir instrucciones: solo aplican lo que aprendieron durante su entrenamiento.

Esto no invalida la comparación. La capacidad de ser instruido es una ventaja real de los LLMs, no una trampa. En producción, cualquier usuario escribiría ese prompt. Medir a los LLMs con prompt es medirlos como se usarían realmente.

Pero sí cambia cómo leer los números: la diferencia no es solo "los LLMs son mejores reconociendo entidades", sino **"un modelo que puede seguir instrucciones sobrepasa a uno que no puede, cuando las reglas son detalladas"**. En nuestro caso, las reglas son muy detalladas (3 categorías con definiciones estrictas), así que la ventaja es grande. Con reglas más estándar, la diferencia sería menor.

Parte de los errores de Kalawinka en ORG, por ejemplo, no son fallos de reconocimiento sino que sigue las reglas con las que fue entrenado — distintas a las nuestras. Los LLMs evitan ese error porque el prompt les dice qué convención seguir.

Dicho esto, la elección sigue siendo Groq. El proyecto necesita un modelo que cumpla nuestras reglas de anotación, y la capacidad de darle instrucciones es exactamente cómo se consigue eso.

---

## 8. Conclusión

Comparamos 4 modelos NER de 4 enfoques distintos sobre 8 papers anotados a mano. **Groq/Llama 3.3 70B gana con F1=0.9489**, el perfil de error más limpio y rendimiento equilibrado en las 3 categorías.

Este es el modelo que usamos para extraer personas, organizaciones y proyectos de los 30 papers del corpus, cuyos resultados alimentan el subgrafo de financiación de nuestro Grafo de Conocimiento.

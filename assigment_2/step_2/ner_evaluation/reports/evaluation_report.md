# NER Model Evaluation Report

Evaluation of NER models on the acknowledgements gold standard (8 documents).

Matching policy: set-based comparison after light normalization (strip, whitespace collapse, hyphen normalization). Case-sensitive. Metrics are micro-averaged over the 8 documents.

## Comparative summary (F1 per category)

| Model                                      | PER F1 | ORG F1 | PROJ F1 | Overall F1 |
|:-------------------------------------------|-------:|-------:|--------:|-----------:|
| groq/llama-3.3-70b-versatile               | 0.9565 | 0.9200 |  1.0000 |     0.9489 |
| hf/Qwen/Qwen2.5-7B-Instruct                | 0.9565 | 0.8511 |  0.8571 |     0.9051 |
| Jean-Baptiste/roberta-large-ner-english    | 0.6857 | 0.6182 |  0.0000 |     0.6119 |
| kalawinka/flair-ner-acknowledgments        | 0.7937 | 0.5778 |  1.0000 |     0.7460 |

## Detailed metrics per model

### groq/llama-3.3-70b-versatile

| Category    | TP | FP | FN | Precision | Recall |     F1 |
|:------------|---:|---:|---:|----------:|-------:|-------:|
| PER         | 33 |  1 |  2 |    0.9706 | 0.9429 | 0.9565 |
| ORG         | 23 |  2 |  2 |    0.9200 | 0.9200 | 0.9200 |
| PROJ        |  9 |  0 |  0 |    1.0000 | 1.0000 | 1.0000 |
| **Overall** | 65 |  3 |  4 |    0.9559 | 0.9420 | 0.9489 |

### hf/Qwen/Qwen2.5-7B-Instruct

| Category    | TP | FP | FN | Precision | Recall |     F1 |
|:------------|---:|---:|---:|----------:|-------:|-------:|
| PER         | 33 |  1 |  2 |    0.9706 | 0.9429 | 0.9565 |
| ORG         | 20 |  2 |  5 |    0.9091 | 0.8000 | 0.8511 |
| PROJ        |  9 |  3 |  0 |    0.7500 | 1.0000 | 0.8571 |
| **Overall** | 62 |  6 |  7 |    0.9118 | 0.8986 | 0.9051 |

### Jean-Baptiste/roberta-large-ner-english

| Category    | TP | FP | FN | Precision | Recall |     F1 |
|:------------|---:|---:|---:|----------:|-------:|-------:|
| PER         | 24 | 11 | 11 |    0.6857 | 0.6857 | 0.6857 |
| ORG         | 17 | 13 |  8 |    0.5667 | 0.6800 | 0.6182 |
| PROJ        |  0 |  0 |  9 |    0.0000 | 0.0000 | 0.0000 |
| **Overall** | 41 | 24 | 28 |    0.6308 | 0.5942 | 0.6119 |

### kalawinka/flair-ner-acknowledgments

| Category    | TP | FP | FN | Precision | Recall |     F1 |
|:------------|---:|---:|---:|----------:|-------:|-------:|
| PER         | 25 |  3 | 10 |    0.8929 | 0.7143 | 0.7937 |
| ORG         | 13 |  7 | 12 |    0.6500 | 0.5200 | 0.5778 |
| PROJ        |  9 |  0 |  0 |    1.0000 | 1.0000 | 1.0000 |
| **Overall** | 47 | 10 | 22 |    0.8246 | 0.6812 | 0.7460 |

## Best model (by overall micro-averaged F1)

**groq/llama-3.3-70b-versatile** (Overall F1 = 0.9489)

# Annotation Guidelines for NER on Acknowledgements

**Version**: 1.1
**Last updated**: May 2026
**Project**: G4_OPENSCIENCE — Knowledge Graph for Research Publications
**Repository**: https://github.com/SergioZSZ/OS-IA-Pipegrobid

---

## 1. Purpose of this document

This document defines the rules and conventions used to manually annotate
named entities in the **Acknowledgements** sections of scientific papers.
The resulting annotations constitute the **Gold Standard** (`gold_standard.json`)
against which Named Entity Recognition (NER) models are evaluated using
Precision, Recall, and F1-score.

These guidelines were applied by two human annotators working in consensus
session, and any future re-annotation must follow them exactly to ensure
reproducibility.

---

## 2. Annotation categories

Three entity categories are recognized. **No other categories** are annotated
in this corpus.

### 2.1. PER — Person

A person explicitly mentioned in the acknowledgements as someone being
thanked, acknowledged, or recognized for their contribution to the work.

**Includes**:
- Full names: `Daniel Garijo`, `Emmanuel Johnson`
- Initials: `SS`, `CJP`, `A.-F. B.`
- Names with academic titles attached in the text: `Prof. C.Z. Zhang`
- Online handles when they refer to a person: `xlr8harder`

**Does NOT include**:
- Pronouns or generic references: *"our collaborators"*, *"the authors"*, *"they"*, *"the team"*
- Author groups: *"the FAIR Chemistry group"* (this is an ORG, not a list of PERs)

### 2.2. ORG — Organization

Any organizational entity mentioned as a source of support, affiliation,
funding, or collaboration.

**Includes**:
- Universities and research centers: `UC Berkeley`, `LBNL`, `Stanford Medicine Post-Baccalaureate Experience In Research program`
- Funding agencies and foundations: `National Science Foundation`, `Simons Foundation`, `Henri Seydoux Fund`
- Funding framework programmes: `Horizon 2020`, `FP7`, `Marie Skłodowska-Curie Actions`
- Government departments and supranational bodies: `Department of Health -Epidemiology Bureau`, `European Union`
- Research groups, collaborations, and named initiatives: `FAIR Chemistry group`, `Simons Foundation Collaboration on the Physics of Learning and Neural Computation`, `national SARS-CoV-2 biosurveillance initiative`
- Named awards and programs treated as organizational entities: `Schmidt Sciences Polymath Award`
- Companies providing compute or resources: `Prime Intellect`

**Does NOT include**:
- Software libraries, code, or tools: `FEniCS`, `PyTorch`, `TensorFlow`
- Hosting platforms when mentioned generically: `GitHub` (when used as a code-hosting reference)
- URLs and web addresses: `www.safeandtrustedai.org`
- Countries treated as geographic locations (not as financing entities)

### 2.3. PROJ — Project / Grant / Award

**Strict definition**: only alphanumeric identifiers of grants, awards, or
contracts. A PROJ entity is a code that uniquely identifies a specific
funded project.

**Includes**:
- Standard grant codes: `IIS-2229876`, `R01EY022933`, `EP/S023356/1`, `851173`, `SA-AUT-2024-015b`, `26-23955S`
- Codes with mixed format: alphanumeric strings with separators (hyphens, slashes, dots) used as project identifiers

**Does NOT include**:
- Names of framework programmes (Horizon 2020 → ORG)
- Names of initiatives or programs without a code
- Names of awards without a code (Schmidt Sciences Polymath Award → ORG)
- The surrounding words such as *"grant"*, *"award"*, *"contract"*, *"agreement"*, *"number"*, *"No."*, *"#"*

**Rationale**: this strict definition aligns with the example shown in
Session 11 of the course (slide 7), where the lecturer marks only
alphanumeric codes as Project IDs. It also aligns with our ontology, where
`schema:Project` is expected to have a unique `schema:identifier`, a
`schema:startDate`, a `schema:endDate`, and a `my:fundingAmount`, which only
apply to individual funded projects, not to framework programmes.

---

## 3. Core annotation principles

### 3.1. Literal text principle

**Annotate entities exactly as they appear in the text**. Do not expand
initials, do not infer implicit entities, do not normalize variant spellings.

**Why**: NER models process the literal text. If we annotate expansions
that don't appear in the source, our evaluation will systematically penalize
the model for not performing entity resolution, which is a separate task.

**Examples**:

| Text says | Correct annotation | Incorrect annotation |
|---|---|---|
| `A.-F. B.` | `A.-F. B.` (PER) | `Anne-Florence Bitbol` |
| `CJP` | `CJP` (PER) | `C. J. Palpal-latoc` |
| `S.G.` | `S.G.` (PER) | `Surya Ganguli` |

Entity resolution (linking `A.-F. B.` to a Wikidata Q-ID or an ORCID) is a
**later pipeline stage**, not annotation.

### 3.2. Span cleanliness

Annotate the **minimum span that uniquely identifies the entity**, without
trailing connectors, prepositions, or determiners.

**Examples**:

| Text says | Correct annotation | Incorrect annotation |
|---|---|---|
| `the US Office of Naval Research` | `US Office of Naval Research` | `the US Office of Naval Research` |
| `grant number EP/S023356/1` | `EP/S023356/1` | `grant number EP/S023356/1` |
| `the FAIR Chemistry group` | `FAIR Chemistry group` | `the FAIR Chemistry group` |

### 3.3. Both long form and acronym annotation

When an entity appears in both long form and acronym separated by parentheses,
annotate **both forms as separate entities of the same type**.

**Example**:

> *"the National Eye Institute (NEI)"*

Annotation:
- ORG: `National Eye Institute`
- ORG: `NEI`

> *"the European Research Council (ERC)"*

Annotation:
- ORG: `European Research Council`
- ORG: `ERC`

### 3.4. Academic titles included only when attached in text

If the text writes the title inline (e.g., `Prof. C.Z. Zhang`), include it
in the span as it appears. Do not strip it.

If the title appears separately from the name (e.g., *"Professor Zhang and
his team"*), annotate only the name span (`Zhang`).

### 3.5. No inference of implicit entities

Do not annotate organizations that are only implicit through compound names.

**Example**: In *"Simons Foundation Collaboration on the Physics of Learning
and Neural Computation"*, annotate only the full collaboration name as ORG.
Do **not** also annotate "Simons Foundation" separately unless it appears
independently elsewhere in the same text.

### 3.6. Anaphora and pronouns

Pronouns and generic references are **never annotated**:
- *"our collaborators"* → not annotated
- *"the authors"* → not annotated
- *"the team"* → not annotated
- *"others from the X group"* → only `X group` is annotated as ORG

---

## 4. Specific decisions and edge cases

This section documents non-trivial decisions made during annotation.
These cases were discussed in consensus session and the resolution is binding
for all annotators.

### 4.1. Framework programmes vs. individual projects

**Decision**: Framework funding programmes (Horizon 2020, FP7, Horizon Europe,
Marie Skłodowska-Curie Actions, etc.) are annotated as **ORG**, not PROJ.

**Justification**: These are administrative frameworks under which thousands
of individual projects are funded. The actual project that funds a paper is
identified by its specific grant agreement code (e.g., `851173`), which is
what should be annotated as PROJ.

**Example (paper_13)**:

> *"This research was partly funded by the European Research Council (ERC)
> under the European Union's Horizon 2020 research and innovation programme
> (grant agreement No. 851173, to A.-F. B.)."*

Annotation:
- PER: `A.-F. B.`
- ORG: `European Research Council`, `ERC`, `European Union`, `Horizon 2020`
- PROJ: `851173`

### 4.2. Named awards without codes

**Decision**: Awards that have a proper name but no alphanumeric code are
annotated as **ORG**, not PROJ.

**Justification**: Without a unique identifier, an award does not fit our
`schema:Project` class, which requires `schema:identifier`. The award is
modeled instead as a recognition/funding entity (ORG).

**Example (paper_27)**:

> *"a Schmidt Sciences Polymath Award"*

Annotation:
- ORG: `Schmidt Sciences Polymath Award`

### 4.3. Software, libraries, and tools

**Decision**: Software products are **not annotated**, in any category.

**Justification**: Software is outside the scope of the three defined
categories. While it could be modeled as a separate `schema:SoftwareApplication`
class in the knowledge graph, this is not part of the NER evaluation task.

**Examples**:
- `FEniCS` → not annotated
- `PyTorch` → not annotated
- `GitHub` (when mentioned as a code-hosting platform) → not annotated

### 4.4. URLs and web addresses

**Decision**: URLs are **not annotated**, in any category.

**Example (paper_09)**: `www.safeandtrustedai.org` → not annotated.

### 4.5. Author handles and pseudonyms

**Decision**: Online handles and pseudonyms used to refer to individual
contributors are annotated as **PER**.

**Example (paper_07)**: `xlr8harder`, `Janus` → both annotated as PER.

### 4.6. Government departments and bureaus

**Decision**: Government departments and bureaus are annotated as **ORG**,
including their internal divisions when mentioned together.

**Example (paper_19)**:

> *"the Department of Health -Epidemiology Bureau"*

Annotation:
- ORG: `Department of Health -Epidemiology Bureau` (annotated exactly as
  it appears in the text, even with non-standard whitespace around the hyphen)

### 4.7. Affiliations of acknowledged people

When the text says *"X from University Y"*, both X (as PER) and University Y
(as ORG) are annotated.

**Example (paper_28)**:

> *"We thank Tobias Kreiman, Sam Blau, ... from UC Berkeley / LBNL"*

Annotation:
- PER: `Tobias Kreiman`, `Sam Blau`, ...
- ORG: `UC Berkeley`, `LBNL`

---

## 5. Out-of-scope categories

The following categories were **deliberately excluded** from the gold standard:

- **LOC / Country**: Geographic locations are not annotated. Country and city
  information for organizations is enriched downstream via Wikidata and
  external sources, not extracted from the acknowledgement text.
- **Software / Tool**: Excluded as discussed in 4.3.
- **Date / Time**: Not relevant for funding entity identification.
- **Money / FundingAmount**: Monetary values, when present, are not annotated
  in the gold standard. Funding amounts are modeled in the ontology
  (`my:fundingAmount`) but populated from external sources, not NER output.

---

## 6. Annotation process

1. The acknowledgement text of each paper is extracted from the GROBID TEI/XML
   output by a Python parser. The plain text is stored in the `text` field
   of each entry in `gold_standard.json`.
2. Two annotators independently read each acknowledgement and identify
   entities according to these guidelines.
3. Disagreements are resolved in a consensus session with at least three
   members of the group present.
4. The final consensus annotation is recorded in `gold_standard.json`.

---

## 7. Evaluation methodology

The gold standard is used to compute Precision, Recall, and F1-score per
category (PER, ORG, PROJ) for each candidate NER model. Models are compared
against the **literal text annotations**: the model output must match the
exact string in the gold standard to be counted as a true positive.

The current corpus consists of **8 documents** containing diverse
acknowledgement structures: short statements with a single funder, medium
statements with multiple persons and organizations, and long statements
with multiple funding sources, named programs, and research collaborations.

---

## 8. Versioning

| Version | Date | Changes |
|---|---|---|
| 1.0 | May 2026 | Initial annotation with mixed PROJ interpretation |
| 1.1 | May 2026 | Strict PROJ definition adopted (alphanumeric codes only). Framework programmes moved to ORG. Literal text principle formalized. |

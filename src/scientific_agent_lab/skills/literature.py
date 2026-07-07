"""Literature retrieval skill — a REAL offline retrieval over a curated domain
knowledge base.

This replaces the earlier honest mock. It stays true to the project's identity:
zero third-party dependencies, fully offline, and **deterministic** (the same
query always returns the same ranked results — which is what lets the
`result_is_reproducible` contract hold). Retrieval is stdlib TF-IDF cosine over a
small, curated knowledge base of domain findings.

Deliberately NOT a live web/API search (arXiv/Crossref/Semantic Scholar): a
network call would break offline execution and determinism, and the whole point
of this layer is reproducibility. Entries are concept-level domain knowledge, not
fabricated paper citations — every match is honestly labelled with its retrieval
score and knowledge-base id.
"""

from __future__ import annotations

import math
import re
from collections import Counter

from ..schemas import EvidenceItem, EvidenceKind

# --- curated domain knowledge base (topical findings, not fake citations) ------
# Each entry: id, domain, finding (the claim), keywords/text used for matching.
KNOWLEDGE_BASE: list[dict] = [
    {"id": "rfb-catholyte-metrics", "domain": "electrochemistry",
     "finding": "Nonaqueous redox-flow catholyte viability is governed jointly by the redox-potential window, active-species solubility, and long-term cycling stability — no single metric is sufficient.",
     "text": "nonaqueous redox flow battery catholyte viability redox potential window solubility cycling stability energy density capacity fade active species"},
    {"id": "rfb-capacity-fade", "domain": "electrochemistry",
     "finding": "Capacity fade in organic redox-flow catholytes is dominated by chemical decomposition of the charged state, so cycling-stability data is required before viability claims.",
     "text": "capacity fade organic redoxmer decomposition charged state cycling stability degradation flow battery dialkoxyarene"},
    {"id": "rfb-solubility-tradeoff", "domain": "electrochemistry",
     "finding": "Solubility of the redox-active species sets the achievable energy density; predicted solubility should be confirmed by measurement before design decisions.",
     "text": "solubility energy density redox active species prediction measurement nonaqueous electrolyte concentration"},
    {"id": "cv-redox-potential", "domain": "electrochemistry",
     "finding": "Cyclic voltammetry is the standard method to characterize redox potential and reversibility of a candidate redoxmer.",
     "text": "cyclic voltammetry redox potential reversibility characterization electrochemistry scan rate peak separation"},
    {"id": "stem-phase-id", "domain": "microscopy",
     "finding": "Crystalline-phase identification from STEM requires lattice-resolved imaging (d-spacings and symmetry) or a companion diffraction measurement; texture descriptors alone are insufficient.",
     "text": "STEM scanning transmission electron microscopy crystalline phase identification lattice spacing d-spacing symmetry diffraction imaging"},
    {"id": "eels-eds-composition", "domain": "microscopy",
     "finding": "Local composition in electron microscopy is established by EELS or EDS, not by contrast/texture alone.",
     "text": "EELS EDS composition electron microscopy elemental analysis spectroscopy contrast texture region"},
    {"id": "microscopy-sampling-bias", "domain": "microscopy",
     "finding": "A single imaged region may not be representative; phase claims should account for sampling bias across the specimen.",
     "text": "sampling bias representative region specimen heterogeneity microscopy field of view phase distribution"},
    {"id": "xrd-phase-id", "domain": "materials",
     "finding": "X-ray diffraction identifies crystalline phases by matching reflection positions and intensities; Rietveld refinement quantifies phase fractions.",
     "text": "x-ray diffraction XRD phase identification reflection peak position intensity Rietveld refinement crystalline"},
    {"id": "tio2-anatase-rutile", "domain": "materials",
     "finding": "Anatase and rutile TiO2 are distinguished by characteristic XRD reflections (e.g. anatase (101) vs rutile (110)); single-phase claims require the absence of the competing phase's peaks.",
     "text": "TiO2 titanium dioxide anatase rutile XRD reflection 101 110 single phase secondary phase peak"},
    {"id": "single-phase-confirmation", "domain": "materials",
     "finding": "A single-phase assignment is only supported when no secondary-phase reflections are detectable above the noise floor.",
     "text": "single phase confirmation secondary phase reflections detection limit noise floor purity XRD"},
    {"id": "measurement-vs-prediction", "domain": "general",
     "finding": "Treating a model prediction as if it were a direct measurement is a common source of over-confidence; the two carry different evidential weight.",
     "text": "measurement prediction model evidence provenance confidence over-confidence evidence kind mismatch"},
    {"id": "uncertainty-before-acceptance", "domain": "general",
     "finding": "Explicit uncertainty quantification should precede any acceptance decision; unquantified confidence is not the same as validated confidence.",
     "text": "uncertainty quantification acceptance decision confidence validation evidence quality reasoning"},
    {"id": "missing-evidence-gating", "domain": "general",
     "finding": "When a required measurement is absent, the responsible action is to acquire it rather than conclude — missing evidence should gate acceptance.",
     "text": "missing evidence required measurement gating acquire before conclude decision human review responsible"},
    {"id": "provenance-reproducibility", "domain": "general",
     "finding": "Every scientific claim should carry provenance and be reproducible from a recorded trace; irreproducible reasoning cannot be audited.",
     "text": "provenance reproducibility trace replay audit scientific claim record deterministic"},
    {"id": "human-in-the-loop", "domain": "general",
     "finding": "Autonomous scientific agents should route consequential actions through a human-in-the-loop review gate before any experiment or write action.",
     "text": "human in the loop review gate autonomous agent experiment write action safety approval"},
]

_STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "is", "are", "for", "on",
    "this", "that", "with", "as", "by", "be", "it", "at", "from", "what", "should",
    "i", "next", "does", "do", "can", "we", "how", "which", "was", "were", "not",
}


def _tokens(text: str) -> list[str]:
    return [w for w in re.split(r"[^a-z0-9]+", (text or "").lower()) if w and w not in _STOP]


# Precompute IDF + per-document TF-IDF vectors from the fixed KB (deterministic).
def _build_index():
    docs = [_tokens(f"{e['finding']} {e['text']} {e['domain']}") for e in KNOWLEDGE_BASE]
    n = len(docs)
    df: Counter = Counter()
    for d in docs:
        for w in set(d):
            df[w] += 1
    idf = {w: math.log((n + 1) / (c + 1)) + 1.0 for w, c in df.items()}
    vecs = []
    for d in docs:
        tf = Counter(d)
        vec = {w: (tf[w] / len(d)) * idf.get(w, 0.0) for w in tf} if d else {}
        vecs.append(vec)
    return idf, vecs


_IDF, _DOC_VECS = _build_index()


def _cosine(qv: dict, dv: dict) -> float:
    if not qv or not dv:
        return 0.0
    dot = sum(qv[w] * dv.get(w, 0.0) for w in qv)
    nq = math.sqrt(sum(v * v for v in qv.values()))
    nd = math.sqrt(sum(v * v for v in dv.values()))
    return dot / (nq * nd) if nq and nd else 0.0


def search(query: str, domain: str | None = None, k: int = 2) -> list[EvidenceItem]:
    """Return the top-k knowledge-base matches for the query as LITERATURE evidence.
    Deterministic: pure function of (query, domain, fixed KB)."""
    qtok = _tokens(f"{query} {domain or ''}")
    if not qtok:
        return []
    qtf = Counter(qtok)
    qv = {w: (qtf[w] / len(qtok)) * _IDF.get(w, 0.0) for w in qtf}

    scored = []
    for i, e in enumerate(KNOWLEDGE_BASE):
        s = _cosine(qv, _DOC_VECS[i])
        if domain and e["domain"] == domain:
            s *= 1.15  # gentle in-domain boost
        scored.append((s, i))
    # deterministic ordering: score desc, then KB order
    scored.sort(key=lambda t: (-t[0], t[1]))

    out: list[EvidenceItem] = []
    for s, i in scored[: max(0, k)]:
        if s <= 0.01:
            continue
        e = KNOWLEDGE_BASE[i]
        out.append(
            EvidenceItem(
                claim=e["finding"],
                kind=EvidenceKind.LITERATURE,
                value=None,
                confidence=round(min(0.6, 0.2 + s), 3),
                source=f"knowledge_base:{e['id']}",
                caveats=(
                    f"Retrieved from a curated offline domain knowledge base "
                    f"(TF-IDF match {round(s, 3)}); not a live literature API."
                ),
            )
        )
    return out

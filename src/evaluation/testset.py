from __future__ import annotations

from pathlib import Path
from typing import Any
import pandas as pd

from core.utils import write_json, first_sentence


def build_test_set(df: pd.DataFrame | list[dict[str, Any]], output_path: str | Path) -> list[dict[str, Any]]:
    """Generates an evaluation test set from the cleaned dataframe / dataset.

    Steps:
    1. Check minimum document count requirement (at least 1 document).
    2. Select representative papers.
    3. Generate diverse question types:
       - summary
       - authors
       - date
       - categories
    4. Each sample contains:
       - id
       - question_type
       - question
       - ground_truth
       - ground_truth_doc_ids
    5. Write JSON array to output_path and return.
    """
    if isinstance(df, list):
        df = pd.DataFrame(df)
    
    if df.empty:
        raise ValueError("Cannot build test set from an empty dataset.")

    test_samples: list[dict[str, Any]] = []
    output_p = Path(output_path)

    # Use up to 10 representative papers to construct questions
    sample_papers = df.head(10).to_dict(orient="records")
    sample_id = 1

    for row in sample_papers:
        paper_id = str(row.get("paper_id", "")).strip()
        title = str(row.get("title", "")).strip()
        summary = str(row.get("summary", "")).strip()
        authors_joined = str(row.get("authors_joined", "")).strip()
        published = str(row.get("published", "")).strip()
        categories_joined = str(row.get("categories_joined", "")).strip() or "General"

        if not paper_id or not title:
            continue

        # 1. Summary question
        if summary:
            test_samples.append({
                "id": f"q{sample_id}",
                "question_type": "summary",
                "question": f"What is the summary of the paper '{title}'?",
                "ground_truth": first_sentence(summary),
                "ground_truth_doc_ids": [paper_id]
            })
            sample_id += 1

        # 2. Authors question
        if authors_joined:
            test_samples.append({
                "id": f"q{sample_id}",
                "question_type": "authors",
                "question": f"Who authored the paper '{title}'?",
                "ground_truth": authors_joined,
                "ground_truth_doc_ids": [paper_id]
            })
            sample_id += 1

        # 3. Publication date question
        if published:
            test_samples.append({
                "id": f"q{sample_id}",
                "question_type": "date",
                "question": f"When was the paper '{title}' published?",
                "ground_truth": published,
                "ground_truth_doc_ids": [paper_id]
            })
            sample_id += 1

        # 4. Categories question
        if categories_joined:
            test_samples.append({
                "id": f"q{sample_id}",
                "question_type": "categories",
                "question": f"What categories belong to the paper '{title}'?",
                "ground_truth": categories_joined,
                "ground_truth_doc_ids": [paper_id]
            })
            sample_id += 1

    write_json(output_p, test_samples)
    return test_samples

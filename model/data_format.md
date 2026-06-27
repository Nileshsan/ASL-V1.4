# Data Format — ASL V1.4 Training Data

## Overview

ASL V1.4 was trained on ~124K domain-specific conversation samples in structured JSON format.
This file documents the schema. The `sample_data.json` file contains 500 anonymized examples.

## JSON Schema

Each record is a JSON object with the following fields:

```json
{
  "id": "string — unique sample identifier",
  "input": {
    "context": "string — conversational or document context",
    "instruction": "string — task instruction (summarize / reply / classify)",
    "history": ["array of prior turns, oldest first"]
  },
  "output": {
    "text": "string — target response",
    "quality_score": "float 0-1 — RL reward signal label",
    "label": "string — task type: summary | reply | classification"
  },
  "metadata": {
    "domain": "string — e.g. sales, support, finance",
    "source": "string — synthetic | human_annotated",
    "length_tokens": "int — approximate token count of output"
  }
}
```

## Field Notes

- `context`: The input document or email thread. PII stripped, names replaced with `[NAME]`, emails with `[EMAIL]`.
- `quality_score`: Used as the RL reward signal during Phase 3 fine-tuning. Derived from human annotation + ROUGE-L correlation.
- `history`: Empty array `[]` for single-turn tasks.
- `domain`: Used during training to condition domain-specific behavior. The model learned separate distributions per domain through the RL phase.

## Split

| Split | Count | Notes |
|-------|-------|-------|
| Train | 111,600 | ~90% |
| Validation | 7,400 | ~6% |
| Test | 5,000 | ~4%, held out for eval |

## Privacy

All samples are either synthetic (generated) or human-annotated with full PII removal.
No real email addresses, names, or business identifiers appear in the released dataset.


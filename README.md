# ASL V1.4

**A custom transformer encoder-decoder architecture trained from scratch for domain-specific email and document intelligence.**

Built at [Applied Sentience Labs](https://appliedsentiencelabs.com) · [HuggingFace Weights](https://huggingface.co/asl-research/asl-v1.4) · [Live Demo App](#quick-start)

---

## Overview

ASL V1.4 is a 4-layer transformer encoder-decoder trained from scratch on ~124K domain-specific conversation samples. Unlike fine-tuned general-purpose models, ASL V1.4 was built to be compact, deterministic, and optimized for structured business communication — email summarization, contextual reply generation, and intent classification.

The model went through three training phases:

1. **Supervised pre-training** on labeled input-output pairs across sales, finance, and support domains
2. **Domain adaptation** using domain-tagged inputs (`<sales>`, `<finance>`, `<support>`) to learn separate behavioral distributions per domain
3. **RL fine-tuning** using a combined reward signal — human quality annotations weighted with automatic ROUGE-L scores — to push outputs toward concise, high-fidelity responses

The result is a model that runs inference in under 200ms on CPU and integrates directly into a production web app with live Gmail and Microsoft Outlook connectivity.

---

## Architecture

```
Input tokens
     │
     ▼
┌─────────────────────────────┐
│        Embedding Layer       │
│   d_model=512, vocab=32000   │
│   + Positional Encoding      │
└─────────────┬───────────────┘
              │
     ┌────────▼────────┐
     │  Encoder (×4)   │
     │                 │
     │  Multi-Head     │
     │  Self-Attention │  ← 8 heads, depth=64
     │  (8 heads)      │
     │       +         │
     │  Feed-Forward   │  ← dff=2048
     │  (ReLU, 2048)   │
     │       +         │
     │  Layer Norm     │
     │  + Dropout 0.1  │
     └────────┬────────┘
              │  encoder output
     ┌────────▼────────┐
     │  Decoder (×4)   │
     │                 │
     │  Masked Self-   │
     │  Attention      │  ← causal mask, 8 heads
     │       +         │
     │  Cross-Attention│  ← attends to encoder output
     │       +         │
     │  Feed-Forward   │
     │       +         │
     │  Layer Norm ×3  │
     └────────┬────────┘
              │
     ┌────────▼────────┐
     │  Linear + Softmax│
     │  vocab=32000     │
     └─────────────────┘
              │
         Output tokens
```

| Parameter | Value |
|-----------|-------|
| Architecture | Transformer encoder-decoder |
| Encoder layers | 4 |
| Decoder layers | 4 |
| Attention heads | 8 |
| Model dimension (d_model) | 512 |
| Feed-forward dimension | 2048 |
| Vocabulary size | 32,000 (BPE) |
| Max input length | 1,024 tokens |
| Max output length | 256 tokens |
| Total parameters | ~45M |
| Training samples | ~124K |
| Framework | TensorFlow / Keras |

---

## Training

### Phase 1 — Supervised fine-tuning (SFT)

Trained on 111,600 labeled samples across three domains. Each input is prefixed with a domain token and task instruction:

```
<sales> [INST] summarize [/INST] Hi [NAME], following up on our proposal...
```

Optimizer: Adam with warmup (`warmup_steps=4000`, `lr=1e-4`). Label smoothing `ε=0.1`.

### Phase 2 — Domain adaptation

Domain tokens (`<sales>`, `<finance>`, `<support>`, `<general>`) were embedded as learned special tokens during SFT, allowing the model to condition its output style and vocabulary on the domain. Finance outputs are more numerical and structured; sales outputs are more conversational.

### Phase 3 — RL fine-tuning

Fine-tuned using a combined reward signal:

```
reward = 0.6 × human_quality_score + 0.4 × rouge_l_score
```

- **Human quality score**: 0–1 annotation by human reviewers rating response conciseness, accuracy, and tone
- **ROUGE-L score**: Computed against reference outputs in the held-out validation set
- **KL penalty** (`coef=0.1`) against the SFT reference model to prevent reward hacking

RL training ran for 10 epochs at `lr=5e-6` on the full training set.

---

## Evaluation

Evaluated on a held-out test set of 5,000 samples.

### Summarization

| Metric | Score |
|--------|-------|
| ROUGE-1 | 0.61 |
| ROUGE-2 | 0.38 |
| ROUGE-L | 0.57 |

### Reply generation

| Metric | Score |
|--------|-------|
| ROUGE-1 | 0.54 |
| ROUGE-2 | 0.29 |
| ROUGE-L | 0.49 |

### Classification (intent)

| Metric | Score |
|--------|-------|
| Accuracy | 91.4% |
| F1 (macro) | 0.89 |

> **Note**: ROUGE scores reflect concise, domain-specific outputs — not open-ended generation. The model is optimized for precision over diversity.

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/Nileshsan/ASL-V1.4.git
cd ASL-V1.4
pip install -r requirements.txt
```

### 2. Download weights from HuggingFace

```bash
pip install huggingface_hub
python -c "
from huggingface_hub import hf_hub_download
hf_hub_download(repo_id='asl-research/asl-v1.4', filename='model.h5', local_dir='./weights')
"
```

### 3. Run the web app

```bash
# Copy and fill in your credentials
cp .env.example .env

# Start the app
cd app
pip install -r requirements.txt
python main.py
```

Then open `http://localhost:5000` — connect your Gmail or Outlook account and the model will start summarizing and drafting replies on live email threads.

---

## Environment Variables

Create a `.env` file in the root (never commit this):

```env
# Gmail OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Microsoft OAuth
OUTLOOK_CLIENT_ID=your_outlook_client_id
OUTLOOK_CLIENT_SECRET=your_outlook_client_secret

# Model
WEIGHTS_PATH=./weights/model.h5
DEVICE=cpu
```

---

## Repository Structure

```
ASL-V1.4/
├── model/
│   ├── architecture.py      # Full encoder-decoder model class
│   ├── layers.py            # Custom Keras layer definitions
│   ├── rl_trainer.py        # RL fine-tuning loop
│   └── config.py            # Hyperparameters and model config
├── training/
│   ├── 01_data_preprocessing.ipynb
│   ├── 02_model_training.ipynb
│   ├── 03_rl_finetuning.ipynb
│   └── 04_evaluation.ipynb
├── data/
│   ├── sample_data.json     # 500 anonymized training examples
│   └── data_format.md       # Full schema documentation
├── app/
│   ├── main.py              # Flask app entrypoint
│   ├── gmail_connector.py   # Gmail OAuth + thread fetching
│   ├── outlook_connector.py # Microsoft Graph API connector
│   ├── summarizer.py        # Inference wrapper — summarization
│   └── reply_generator.py  # Inference wrapper — reply generation
├── assets/
│   ├── architecture.png     # Architecture diagram
│   └── demo.gif             # App demo
└── requirements.txt
```

---

## Pretrained Weights

Weights (~2GB) are hosted on HuggingFace due to file size:

**[asl-research/asl-v1.4 on HuggingFace](https://huggingface.co/asl-research/asl-v1.4)**

The GitHub repo contains all code, training notebooks, and sample data only.

---

## Citation

If you use ASL V1.4 in your research or build on this work:

```bibtex
@misc{sanyasi2025aslv14,
  title     = {ASL V1.4: Domain-Specific Transformer for Email Intelligence},
  author    = {Sanyasi, Nilesh},
  year      = {2025},
  publisher = {Applied Sentience Labs},
  url       = {https://github.com/Nileshsan/ASL-V1.4}
}
```

---

## License

MIT License — see [LICENSE](./LICENSE) for details.

---

*Built by [Nilesh Sanyasi](https://linkedin.com/in/nileshsanyasi) · [Applied Sentience Labs](https://appliedsentiencelabs.com)*

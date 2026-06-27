"""
ASL V1.4 — Model Configuration
Applied Sentience Labs
"""

MODEL_CONFIG = {
    # Architecture
    "model_name": "ASL-V1.4",
    "version": "1.4",
    "architecture": "transformer_encoder_decoder",

    # Encoder
    "encoder_layers": 4,
    "encoder_heads": 8,
    "encoder_dff": 2048,        # Feed-forward dim
    "encoder_dropout": 0.1,

    # Decoder
    "decoder_layers": 4,
    "decoder_heads": 8,
    "decoder_dff": 2048,
    "decoder_dropout": 0.1,

    # Shared
    "d_model": 512,             # Embedding dimension
    "max_seq_len": 1024,        # Max input tokens
    "max_output_len": 256,      # Max generation length
    "vocab_size": 32000,        # BPE vocabulary

    # Training
    "batch_size": 32,
    "learning_rate": 1e-4,
    "warmup_steps": 4000,
    "total_steps": 100000,
    "gradient_clip": 1.0,

    # RL Phase
    "rl_learning_rate": 5e-6,
    "rl_epochs": 10,
    "rl_kl_coef": 0.1,         # KL penalty vs SFT reference
    "reward_scale": 1.0,

    # Domain tags (prepended to input)
    "domain_tokens": ["<sales>", "<finance>", "<support>", "<general>"],

    # Paths (override in env or training script)
    "checkpoint_dir": "./checkpoints",
    "log_dir": "./logs",
}

TOKENIZER_CONFIG = {
    "type": "bpe",
    "vocab_size": 32000,
    "special_tokens": {
        "pad": "[PAD]",
        "unk": "[UNK]",
        "bos": "[BOS]",
        "eos": "[EOS]",
        "sep": "[SEP]",
        "mask": "[MASK]",
        "pii_name": "[NAME]",
        "pii_email": "[EMAIL]",
        "pii_org": "[ORG]",
    }
}
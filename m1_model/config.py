"""
Configuration file for M1 Hybrid Reasoning Model project.
"""

MODEL_CONFIG = {
    "embed_dim": 512,
    "num_heads": 8,
    "num_layers": 12,
    "expansion": 4
}

TRAINING_CONFIG = {
    "distillation_epochs": 10,
    "sft_epochs": 5,
    "rl_epochs": 5,
    "batch_size": 32,
    "learning_rate": 1e-4
}
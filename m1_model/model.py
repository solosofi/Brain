"""
M1 Hybrid Reasoning Model Architecture (initial skeleton)
"""

import torch
import torch.nn as nn

class MambaLayer(nn.Module):
    def __init__(self, embed_dim, num_heads, expansion):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.expansion = expansion
        self.attn = nn.MultiheadAttention(embed_dim, num_heads, batch_first=True)
        self.ffn = nn.Sequential(
            nn.Linear(embed_dim, embed_dim * expansion),
            nn.GELU(),
            nn.Linear(embed_dim * expansion, embed_dim)
        )
        self.norm1 = nn.LayerNorm(embed_dim)
        self.norm2 = nn.LayerNorm(embed_dim)

    def forward(self, x):
        # Self-attention
        attn_output, _ = self.attn(x, x, x)
        x = x + attn_output
        x = self.norm1(x)
        # Feed-forward
        ff_output = self.ffn(x)
        x = x + ff_output
        x = self.norm2(x)
        return x

class M1Model(nn.Module):
    def __init__(self, embed_dim=512, num_heads=8, num_layers=12, expansion=4, vocab_size=30522):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_dim)
        self.layers = nn.ModuleList([
            MambaLayer(embed_dim, num_heads, expansion) for _ in range(num_layers)
        ])
        self.ln = nn.LayerNorm(embed_dim)
        self.head = nn.Linear(embed_dim, vocab_size)

    def forward(self, input_ids):
        x = self.embed(input_ids)
        for layer in self.layers:
            x = layer(x)
        x = self.ln(x)
        logits = self.head(x)
        return logits
"""
ASL V1.4 — Custom Keras Layer Definitions
Applied Sentience Labs
"""

import tensorflow as tf
import numpy as np


def get_positional_encoding(max_len, d_model):
    """Sinusoidal positional encoding as per 'Attention Is All You Need'."""
    positions = np.arange(max_len)[:, np.newaxis]
    dims = np.arange(d_model)[np.newaxis, :]
    angles = positions / np.power(10000, (2 * (dims // 2)) / d_model)
    angles[:, 0::2] = np.sin(angles[:, 0::2])
    angles[:, 1::2] = np.cos(angles[:, 1::2])
    return tf.cast(angles[np.newaxis, :, :], dtype=tf.float32)


class MultiHeadAttention(tf.keras.layers.Layer):
    """
    Multi-head self/cross attention.
    Supports causal masking (for decoder self-attention)
    and cross-attention between encoder output and decoder state.
    """

    def __init__(self, d_model, num_heads, **kwargs):
        super().__init__(**kwargs)
        assert d_model % num_heads == 0
        self.num_heads = num_heads
        self.d_model = d_model
        self.depth = d_model // num_heads

        self.wq = tf.keras.layers.Dense(d_model)
        self.wk = tf.keras.layers.Dense(d_model)
        self.wv = tf.keras.layers.Dense(d_model)
        self.dense = tf.keras.layers.Dense(d_model)

    def split_heads(self, x, batch_size):
        x = tf.reshape(x, (batch_size, -1, self.num_heads, self.depth))
        return tf.transpose(x, perm=[0, 2, 1, 3])

    def call(self, q, k, v, mask=None):
        batch_size = tf.shape(q)[0]

        q = self.split_heads(self.wq(q), batch_size)
        k = self.split_heads(self.wk(k), batch_size)
        v = self.split_heads(self.wv(v), batch_size)

        # Scaled dot-product attention
        matmul_qk = tf.matmul(q, k, transpose_b=True) / tf.math.sqrt(
            tf.cast(self.depth, tf.float32)
        )
        if mask is not None:
            matmul_qk += mask * -1e9

        weights = tf.nn.softmax(matmul_qk, axis=-1)
        output = tf.matmul(weights, v)
        output = tf.transpose(output, perm=[0, 2, 1, 3])
        output = tf.reshape(output, (batch_size, -1, self.d_model))

        return self.dense(output), weights


class FeedForward(tf.keras.layers.Layer):
    """Position-wise feed-forward network."""

    def __init__(self, d_model, dff, dropout_rate=0.1, **kwargs):
        super().__init__(**kwargs)
        self.dense1 = tf.keras.layers.Dense(dff, activation="relu")
        self.dense2 = tf.keras.layers.Dense(d_model)
        self.dropout = tf.keras.layers.Dropout(dropout_rate)

    def call(self, x, training=False):
        x = self.dense1(x)
        x = self.dropout(x, training=training)
        return self.dense2(x)


class EncoderLayer(tf.keras.layers.Layer):
    """Single encoder layer: self-attention + FFN + residuals."""

    def __init__(self, d_model, num_heads, dff, dropout_rate=0.1, **kwargs):
        super().__init__(**kwargs)
        self.mha = MultiHeadAttention(d_model, num_heads)
        self.ffn = FeedForward(d_model, dff, dropout_rate)
        self.norm1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.norm2 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.drop1 = tf.keras.layers.Dropout(dropout_rate)
        self.drop2 = tf.keras.layers.Dropout(dropout_rate)

    def call(self, x, mask=None, training=False):
        attn_out, _ = self.mha(x, x, x, mask)
        x = self.norm1(x + self.drop1(attn_out, training=training))
        ffn_out = self.ffn(x, training=training)
        return self.norm2(x + self.drop2(ffn_out, training=training))


class DecoderLayer(tf.keras.layers.Layer):
    """Single decoder layer: masked self-attention + cross-attention + FFN."""

    def __init__(self, d_model, num_heads, dff, dropout_rate=0.1, **kwargs):
        super().__init__(**kwargs)
        self.mha1 = MultiHeadAttention(d_model, num_heads)   # masked self-attn
        self.mha2 = MultiHeadAttention(d_model, num_heads)   # cross-attn
        self.ffn = FeedForward(d_model, dff, dropout_rate)
        self.norm1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.norm2 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.norm3 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.drop1 = tf.keras.layers.Dropout(dropout_rate)
        self.drop2 = tf.keras.layers.Dropout(dropout_rate)
        self.drop3 = tf.keras.layers.Dropout(dropout_rate)

    def call(self, x, enc_output, look_ahead_mask=None, padding_mask=None, training=False):
        attn1, attn_w1 = self.mha1(x, x, x, look_ahead_mask)
        x = self.norm1(x + self.drop1(attn1, training=training))

        attn2, attn_w2 = self.mha2(x, enc_output, enc_output, padding_mask)
        x = self.norm2(x + self.drop2(attn2, training=training))

        ffn_out = self.ffn(x, training=training)
        x = self.norm3(x + self.drop3(ffn_out, training=training))

        return x, attn_w1, attn_w2
import json


def encoding_to_text(encoding) -> str:
    return json.dumps(encoding.tolist())


def text_to_encoding(vector_text: str):
    import numpy as np

    return np.array(json.loads(vector_text), dtype=float)

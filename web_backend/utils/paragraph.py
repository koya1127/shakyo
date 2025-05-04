from typing import List

def split_paragraphs(text: str) -> List[str]:
    """空行（\\n\\n）で段落を分割して返す。"""
    return [p.strip() for p in text.split("\n\n") if p.strip()]

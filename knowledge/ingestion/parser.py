import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger("knowledge.parser")

class DocumentParser:
    """
    Multi-format document parser & chunker for NEUROCORE RAG.
    Supports TXT, MD, PY, JSON, CSV, PDF, and DOCX files.
    """
    def __init__(self, chunk_size: int = 300, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = path.suffix.lower()
        
        if ext in {".pdf"}:
            text = self._parse_pdf(path)
        elif ext in {".docx", ".doc"}:
            text = self._parse_docx(path)
        elif ext in {".json"}:
            text = self._parse_json(path)
        else:
            # Plain text fallback (txt, md, py, csv, etc.)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

        return self.chunk_text(text, source=path.name, file_type=ext)

    def _parse_pdf(self, path: Path) -> str:
        # Try PyPDF2 / pypdf
        try:
            import pypdf
            reader = pypdf.PdfReader(str(path))
            text = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text.append(t)
            return "\n".join(text)
        except ImportError:
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(str(path))
                text = [page.extract_text() for page in reader.pages if page.extract_text()]
                return "\n".join(text)
            except ImportError:
                logger.warning(f"PyPDF library not available. Reading raw text from {path.name}")
                with open(path, "rb") as f:
                    content = f.read().decode("latin1", errors="ignore")
                    return content

    def _parse_docx(self, path: Path) -> str:
        try:
            import docx
            doc = docx.Document(str(path))
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except ImportError:
            logger.warning(f"docx library not available. Reading plain text from {path.name}")
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

    def _parse_json(self, path: Path) -> str:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
            return json.dumps(data, indent=2)

    def chunk_text(self, text: str, source: str = "raw_text", file_type: str = ".txt") -> List[Dict[str, Any]]:
        words = text.split()
        if not words:
            return []

        chunks = []
        start = 0

        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            chunk_str = " ".join(chunk_words)

            chunks.append({
                "source": source,
                "file_type": file_type,
                "chunk_index": len(chunks),
                "start_word": start,
                "end_word": min(end, len(words)),
                "content": chunk_str
            })

            start += (self.chunk_size - self.overlap)

        logger.info(f"Chunked document '{source}' into {len(chunks)} fragments.")
        return chunks


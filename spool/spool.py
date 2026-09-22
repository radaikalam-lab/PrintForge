import hashlib
import os
import json
import asyncio
from typing import Dict, Any, Optional, BinaryIO
from datetime import datetime, UTC
from pathlib import Path


class SpoolStore:
    def __init__(self, base_path: str = "./spool"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._load_metadata()

    def _artifact_path(self, artifact_id: str) -> Path:
        return self.base_path / artifact_id

    def _metadata_path(self) -> Path:
        return self.base_path / "metadata.json"

    def _load_metadata(self) -> None:
        path = self._metadata_path()
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                self._metadata = json.load(f)

    def _save_metadata(self) -> None:
        path = self._metadata_path()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._metadata, f, indent=2, default=str)

    def _compute_sha256(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    async def store(self, artifact: bytes, metadata: Dict[str, Any]) -> str:
        artifact_id = self._compute_sha256(artifact)
        path = self._artifact_path(artifact_id)
        if path.exists():
            raise FileExistsError(f"Artifact {artifact_id} already exists")
        with open(path, "wb") as f:
            f.write(artifact)
        record = {
            "artifact_id": artifact_id,
            "size": len(artifact),
            "sha256": artifact_id,
            "stored_at": datetime.now(UTC).isoformat(),
            "metadata": metadata,
        }
        self._metadata[artifact_id] = record
        self._save_metadata()
        return artifact_id

    async def retrieve(self, artifact_id: str) -> bytes:
        path = self._artifact_path(artifact_id)
        if not path.exists():
            raise FileNotFoundError(f"Artifact {artifact_id} not found")
        with open(path, "rb") as f:
            data = f.read()
        expected_hash = self._compute_sha256(data)
        if expected_hash != artifact_id:
            raise ValueError(f"Integrity check failed for artifact {artifact_id}")
        return data

    async def delete(self, artifact_id: str) -> bool:
        path = self._artifact_path(artifact_id)
        if not path.exists():
            return False
        path.unlink()
        self._metadata.pop(artifact_id, None)
        self._save_metadata()
        return True

    async def exists(self, artifact_id: str) -> bool:
        return self._artifact_path(artifact_id).exists()

    async def cleanup(self, max_age_seconds: Optional[int] = None) -> int:
        now = datetime.now(UTC)
        removed = 0
        for artifact_id in list(self._metadata.keys()):
            record = self._metadata[artifact_id]
            stored_at = datetime.fromisoformat(record["stored_at"])
            if max_age_seconds is not None:
                age = (now - stored_at).total_seconds()
                if age > max_age_seconds:
                    await self.delete(artifact_id)
                    removed += 1
        return removed

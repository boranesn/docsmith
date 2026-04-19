import json
import uuid
from datetime import datetime
from pathlib import Path

from docsmith.config import settings
from docsmith.models import RunMetadata


class StateManager:
    def __init__(self, state_path: Path | None = None) -> None:
        self._path = state_path or settings.state_file
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def new_run(self, repo_path: str, output_path: str) -> RunMetadata:
        return RunMetadata(
            run_id=str(uuid.uuid4()),
            repo_path=repo_path,
            started_at=datetime.utcnow(),
            output_path=output_path,
        )

    def save(self, metadata: RunMetadata) -> None:
        history = self._load_history()
        history[metadata.run_id] = json.loads(metadata.model_dump_json())
        self._path.write_text(json.dumps(history, indent=2, default=str))

    def load_latest(self) -> RunMetadata | None:
        history = self._load_history()
        if not history:
            return None
        latest_id = max(history, key=lambda k: history[k]["started_at"])
        return RunMetadata(**history[latest_id])

    def _load_history(self) -> dict:
        if not self._path.exists():
            return {}
        return json.loads(self._path.read_text())

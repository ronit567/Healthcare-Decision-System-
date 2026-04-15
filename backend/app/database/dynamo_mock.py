"""
Mock DynamoDB implementation using an in-memory store + JSON file persistence.
Stores step-by-step execution logs, LLM outputs, and intermediate workflow state.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from threading import Lock

DYNAMO_PERSIST_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "dynamo_store.json")

_lock = Lock()


class DynamoMockTable:
    """Simulates a single DynamoDB table with partition key + sort key."""

    def __init__(self, table_name: str):
        self.table_name = table_name
        self._items: List[Dict[str, Any]] = []
        self._load()

    def _persist_path(self) -> str:
        os.makedirs(os.path.dirname(DYNAMO_PERSIST_PATH), exist_ok=True)
        return DYNAMO_PERSIST_PATH

    def _load(self):
        path = self._persist_path()
        if os.path.exists(path):
            with open(path, "r") as f:
                store = json.load(f)
                self._items = store.get(self.table_name, [])

    def _save(self):
        path = self._persist_path()
        store = {}
        if os.path.exists(path):
            with open(path, "r") as f:
                store = json.load(f)
        store[self.table_name] = self._items
        with open(path, "w") as f:
            json.dump(store, f, indent=2, default=str)

    def put_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        with _lock:
            if "id" not in item:
                item["id"] = str(uuid.uuid4())
            item["timestamp"] = datetime.now(timezone.utc).isoformat()
            self._items.append(item)
            self._save()
        return item

    def get_items_by_key(self, key: str, value: str) -> List[Dict[str, Any]]:
        with _lock:
            return [i for i in self._items if i.get(key) == value]

    def get_all_items(self) -> List[Dict[str, Any]]:
        with _lock:
            return list(self._items)

    def query(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        with _lock:
            results = self._items
            for k, v in filters.items():
                results = [i for i in results if i.get(k) == v]
            return results

    def clear(self):
        with _lock:
            self._items = []
            self._save()


# Singleton table instances
execution_logs_table = DynamoMockTable("execution_logs")
llm_outputs_table = DynamoMockTable("llm_outputs")
workflow_state_table = DynamoMockTable("workflow_state")

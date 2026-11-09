"""
Undo/Redo functionality for CompPy
Tracks parameter changes and allows reverting
"""
from __future__ import annotations

from typing import Any


State = dict[str, Any]


class UndoRedoManager:
    """Bounded undo/redo stack for field-edit states."""

    def __init__(self) -> None:
        self.undo_stack: list[State] = []
        self.redo_stack: list[State] = []
        self.max_stack_size: int = 50

    def push_state(self, state: State) -> None:
        """Push a new state; clears redo history.

        State keys: stage_idx, field_name, old_value, new_value.
        """
        self.undo_stack.append(state)
        if len(self.undo_stack) > self.max_stack_size:
            self.undo_stack.pop(0)
        # Clear redo stack when new change is made.
        self.redo_stack.clear()

    def can_undo(self) -> bool:
        """Return True when an undo state is available."""
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """Return True when a redo state is available."""
        return len(self.redo_stack) > 0

    def undo(self) -> State | None:
        """Pop and return the last state, or None if unavailable."""
        if not self.can_undo():
            return None
        state = self.undo_stack.pop()
        self.redo_stack.append(state)
        return state

    def redo(self) -> State | None:
        """Reapply and return the last undone state, or None if unavailable."""
        if not self.can_redo():
            return None
        state = self.redo_stack.pop()
        self.undo_stack.append(state)
        return state

    def clear(self) -> None:
        """Clear all undo/redo history."""
        self.undo_stack.clear()
        self.redo_stack.clear()

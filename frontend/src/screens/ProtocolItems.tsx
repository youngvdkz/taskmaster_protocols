import { useEffect, useMemo, useRef, useState } from "react";
import {
  deleteItem,
  fetchItems,
  Item,
  quickCreateItems,
  renameItem,
  reorderItems,
  transcribeAudio
} from "../api/client";
import {
  DndContext,
  TouchSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors
} from "@dnd-kit/core";
import {
  SortableContext,
  useSortable,
  verticalListSortingStrategy,
  arrayMove
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

function SortableRow({
  item,
  onDelete,
  onRename
}: {
  item: Item;
  onDelete: (id: number) => void;
  onRename: (id: number, title: string) => void;
}) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({
    id: item.id
  });

  const style: React.CSSProperties = {
    transform: CSS.Transform.toString(transform),
    transition
  };

  return (
    <li ref={setNodeRef} style={style} className="list-item">
      <button className="drag-handle" {...attributes} {...listeners} aria-label="Drag">
        ::
      </button>
      <span className="title-button">{item.title}</span>
      <div className="inline-actions">
        <button
          className="icon-action"
          onClick={() => {
        const next = window.prompt("Rename item", item.title);
        if (next) onRename(item.id, next);
          }}
          aria-label="Rename item"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M4 20h4l11-11-4-4L4 16v4Zm14.7-14.7 1.3-1.3a1 1 0 0 1 1.4 0l1.3 1.3a1 1 0 0 1 0 1.4L21.4 8 18.7 5.3Z"
              fill="currentColor"
            />
          </svg>
        </button>
        <button className="icon-action danger" onClick={() => onDelete(item.id)} aria-label="Delete item">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M7 8h2v10H7V8Zm8 0h2v10h-2V8ZM9 4h6l1 2h4v2H4V6h4l1-2Zm-3 6h12l-1 9a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2l-1-9Z"
              fill="currentColor"
            />
          </svg>
        </button>
      </div>
    </li>
  );
}

export default function ProtocolItems({
  protocolId,
  onBack
}: {
  protocolId: number;
  onBack: () => void;
}) {
  const [items, setItems] = useState<Item[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [recording, setRecording] = useState(false);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 6 } }),
    useSensor(TouchSensor, { activationConstraint: { delay: 150, tolerance: 6 } })
  );
  const ids = useMemo(() => items.map((i) => i.id), [items]);

  useEffect(() => {
    fetchItems(protocolId)
      .then(setItems)
      .catch((err) => setError(err.message));
  }, [protocolId]);

  async function handleAdd(title: string) {
    if (!title.trim()) return;
    setSaving("Saving...");
    try {
      const created = await quickCreateItems(protocolId, title.trim());
      setItems((prev) => [...prev, ...created]);
      setInput("");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(null);
    }
  }

  async function handleVoice() {
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
      setError("Voice input is not supported on this device.");
      return;
    }
    if (recording) {
      recorderRef.current?.stop();
      return;
    }
    setError(null);
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    recorderRef.current = recorder;
    chunksRef.current = [];
    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };
    recorder.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop());
      setRecording(false);
      const blob = new Blob(chunksRef.current, { type: "audio/webm" });
      try {
        const text = await transcribeAudio(blob);
        setInput(text);
        await handleAdd(text);
      } catch (err: any) {
        setError(err.message);
      }
    };
    setRecording(true);
    recorder.start();
  }

  async function handleDelete(id: number) {
    if (!window.confirm("Delete this item?")) return;
    setSaving("Saving...");
    try {
      await deleteItem(id);
      setItems((prev) => prev.filter((i) => i.id !== id));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(null);
    }
  }

  async function handleRename(id: number, title: string) {
    setSaving("Saving...");
    try {
      await renameItem(id, title);
      setItems((prev) => prev.map((i) => (i.id === id ? { ...i, title } : i)));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(null);
    }
  }

  async function handleDragEnd(event: any) {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    const oldIndex = ids.indexOf(active.id);
    const newIndex = ids.indexOf(over.id);
    const next = arrayMove(items, oldIndex, newIndex).map((i, idx) => ({
      ...i,
      order_index: idx
    }));

    setItems(next);
    try {
      await reorderItems(next.map((i) => i.id));
    } catch (err: any) {
      setError(err.message);
      const fresh = await fetchItems(protocolId);
      setItems(fresh);
    }
  }

  return (
    <div className="app-shell">
      <div className="header">
        <div>
          <h1 className="title">Protocol items</h1>
          <div className="subtle">Order the steps and keep it light.</div>
        </div>
        <div className="inline-actions">
          <button className="button secondary" onClick={onBack}>
            Back
          </button>
        </div>
      </div>
      <div className="card">
        <div className="input-row">
          <input
            className="input"
            placeholder="Add a new item..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleAdd(input);
            }}
          />
          <div className="inline-actions">
            <button className="icon-btn" onClick={handleVoice} aria-label="Voice input">
              {recording ? "■" : "🎙"}
            </button>
            <button className="icon-btn" onClick={() => handleAdd(input)} aria-label="Add item">
              +
            </button>
          </div>
        </div>
        <div className="row">
          <div className="badge">Reorder enabled</div>
          {saving && <div className="status">{saving}</div>}
        </div>
        {error && <p style={{ color: "var(--danger)" }}>{error}</p>}
      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={ids} strategy={verticalListSortingStrategy}>
          <ul className="list">
            {items.map((item) => (
              <SortableRow key={item.id} item={item} onDelete={handleDelete} onRename={handleRename} />
            ))}
          </ul>
        </SortableContext>
      </DndContext>
        {items.length === 0 && <div className="empty">No items yet. Add the first step.</div>}
      </div>
    </div>
  );
}

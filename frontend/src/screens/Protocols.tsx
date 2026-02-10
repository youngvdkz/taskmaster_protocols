import { useEffect, useMemo, useRef, useState } from "react";
import {
  deleteProtocol,
  fetchProtocols,
  getUserId,
  Protocol,
  quickCreateProtocol,
  renameProtocol,
  reorderProtocols,
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
  protocol,
  onOpen,
  onDelete,
  onRename
}: {
  protocol: Protocol;
  onOpen: (id: number) => void;
  onDelete: (id: number) => void;
  onRename: (id: number, title: string) => void;
}) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({
    id: protocol.id
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
      <button className="title-button" onClick={() => onOpen(protocol.id)}>
        {protocol.title}
      </button>
      <div className="inline-actions">
        <button
          className="icon-action"
          onClick={() => {
        const next = window.prompt("Rename protocol", protocol.title);
        if (next) onRename(protocol.id, next);
          }}
          aria-label="Rename protocol"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M4 20h4l11-11-4-4L4 16v4Zm14.7-14.7 1.3-1.3a1 1 0 0 1 1.4 0l1.3 1.3a1 1 0 0 1 0 1.4L21.4 8 18.7 5.3Z"
              fill="currentColor"
            />
          </svg>
        </button>
        <button className="icon-action danger" onClick={() => onDelete(protocol.id)} aria-label="Delete protocol">
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

export default function Protocols({ onOpen }: { onOpen: (id: number) => void }) {
  const [protocols, setProtocols] = useState<Protocol[]>([]);
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
  const ids = useMemo(() => protocols.map((p) => p.id), [protocols]);

  useEffect(() => {
    fetchProtocols(getUserId())
      .then(setProtocols)
      .catch((err) => setError(err.message));
  }, []);

  async function handleAdd(title: string) {
    if (!title.trim()) return;
    setSaving("Saving...");
    try {
      const created = await quickCreateProtocol(title.trim());
      setProtocols((prev) => [...prev, created.protocol]);
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
    if (!window.confirm("Delete this protocol?")) return;
    setSaving("Saving...");
    try {
      await deleteProtocol(id);
      setProtocols((prev) => prev.filter((p) => p.id !== id));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(null);
    }
  }

  async function handleRename(id: number, title: string) {
    setSaving("Saving...");
    try {
      await renameProtocol(id, title);
      setProtocols((prev) => prev.map((p) => (p.id === id ? { ...p, title } : p)));
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
    const next = arrayMove(protocols, oldIndex, newIndex).map((p, idx) => ({
      ...p,
      order_index: idx
    }));

    setProtocols(next);
    try {
      await reorderProtocols(next.map((p) => p.id));
    } catch (err: any) {
      setError(err.message);
      const fresh = await fetchProtocols(getUserId());
      setProtocols(fresh);
    }
  }

  return (
    <div className="app-shell">
      <div className="header">
        <div>
          <h1 className="title">Protocols</h1>
          <div className="subtle">Create checklists for your daily routines.</div>
        </div>
      </div>
      <div className="card">
        <div className="input-row">
          <input
            className="input"
            placeholder="Add a new protocol..."
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
            <button className="icon-btn" onClick={() => handleAdd(input)} aria-label="Add protocol">
              +
            </button>
          </div>
        </div>
        <div className="row">
          {saving && <div className="status">{saving}</div>}
        </div>
        {error && <p style={{ color: "var(--danger)" }}>{error}</p>}
        <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={ids} strategy={verticalListSortingStrategy}>
          <ul className="list">
            {protocols.map((p) => (
              <SortableRow
                key={p.id}
                protocol={p}
                onOpen={onOpen}
                onDelete={handleDelete}
                onRename={handleRename}
              />
            ))}
          </ul>
        </SortableContext>
      </DndContext>
        {protocols.length === 0 && <div className="empty">No protocols yet. Add your first routine.</div>}
      </div>
    </div>
  );
}

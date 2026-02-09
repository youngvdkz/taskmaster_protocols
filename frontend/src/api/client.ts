function normalizeApiBase(value: string | undefined): string {
  if (!value) return "/api";
  const trimmed = value.trim();
  const unquoted = trimmed.replace(/^['"]|['"]$/g, "");
  return unquoted.replace(/\/+$/, "") || "/api";
}

export const API_BASE = normalizeApiBase(import.meta.env.VITE_API_BASE);

export type Protocol = { id: number; title: string; order_index: number };
export type Item = { id: number; title: string; order_index: number };

export function getUserId(): number {
  const params = new URLSearchParams(window.location.search);
  const fromQuery = params.get("user_id");
  if (fromQuery && !Number.isNaN(Number(fromQuery))) {
    return Number(fromQuery);
  }
  const tg = (window as any).Telegram?.WebApp;
  return tg?.initDataUnsafe?.user?.id ?? 123;
}

export async function fetchProtocols(userId: number): Promise<Protocol[]> {
  const res = await fetch(`${API_BASE}/protocols/?user_id=${userId}`);
  if (!res.ok) throw new Error("Failed to load protocols");
  return res.json();
}

export async function fetchItems(protocolId: number): Promise<Item[]> {
  const res = await fetch(`${API_BASE}/protocols/${protocolId}/items`);
  if (!res.ok) throw new Error("Failed to load items");
  return res.json();
}

export async function createProtocol(title: string): Promise<Protocol> {
  const res = await fetch(`${API_BASE}/protocols/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: getUserId(), title })
  });
  if (!res.ok) throw new Error("Failed to create protocol");
  return res.json();
}

export async function quickCreateProtocol(text: string): Promise<{
  protocol: Protocol;
  items: Item[];
}> {
  const res = await fetch(`${API_BASE}/protocols/quick-create`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: getUserId(), text })
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail?.detail?.error || "Failed to parse input");
  }
  return res.json();
}

export async function renameProtocol(id: number, title: string): Promise<void> {
  const res = await fetch(`${API_BASE}/protocols/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title })
  });
  if (!res.ok) throw new Error("Failed to rename protocol");
}

export async function deleteProtocol(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/protocols/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete protocol");
}

export async function reorderProtocols(orderedIds: number[]): Promise<void> {
  const res = await fetch(`${API_BASE}/protocols/reorder`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ordered_ids: orderedIds })
  });
  if (!res.ok) throw new Error("Failed to reorder protocols");
}

export async function createItem(protocolId: number, title: string): Promise<Item> {
  const res = await fetch(`${API_BASE}/protocols/${protocolId}/items`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title })
  });
  if (!res.ok) throw new Error("Failed to create item");
  return res.json();
}

export async function quickCreateItems(protocolId: number, text: string): Promise<Item[]> {
  const res = await fetch(`${API_BASE}/protocols/${protocolId}/items/quick-create`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail?.detail?.error || "Failed to parse items");
  }
  const data = await res.json();
  return data.items;
}

export async function transcribeAudio(file: Blob): Promise<string> {
  const form = new FormData();
  form.append("file", file, "audio.webm");
  const res = await fetch(`${API_BASE}/audio/transcribe`, { method: "POST", body: form });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail?.detail || "Failed to transcribe audio");
  }
  const data = await res.json();
  return data.text as string;
}

export async function renameItem(id: number, title: string): Promise<void> {
  const res = await fetch(`${API_BASE}/items/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title })
  });
  if (!res.ok) throw new Error("Failed to rename item");
}

export async function deleteItem(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/items/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete item");
}

export async function reorderItems(orderedIds: number[]): Promise<void> {
  const res = await fetch(`${API_BASE}/items/reorder`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ordered_ids: orderedIds })
  });
  if (!res.ok) throw new Error("Failed to reorder items");
}

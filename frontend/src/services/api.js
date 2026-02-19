const API_URL = window.location.origin.includes('localhost') ? 'http://localhost:8000' : 'https://backend-rho-gray-56.vercel.app';

export const getNotes = async () => {
  const response = await fetch(`${API_URL}/notes`);
  if (!response.ok) throw new Error('Failed to fetch notes');
  return response.json();
};

export const createNote = async (note) => {
  const response = await fetch(`${API_URL}/notes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(note),
  });
  if (!response.ok) throw new Error('Failed to create note');
  return response.json();
};

export const updateNote = async (id, note) => {
  const response = await fetch(`${API_URL}/notes/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(note),
  });
  if (!response.ok) throw new Error('Failed to update note');
  return response.json();
};

export const deleteNote = async (id) => {
  const response = await fetch(`${API_URL}/notes/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete note');
  return response.json();
};

export const createSubscription = async (sub) => {
  const response = await fetch(`${API_URL}/subscriptions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(sub),
  });
  if (!response.ok) throw new Error('Failed to subscribe');
  return response.json();
};

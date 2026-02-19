import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [notes, setNotes] = useState([])
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')

  const fetchNotes = async () => {
    try {
      const res = await axios.get('http://localhost:8000/notes')
      setNotes(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const addNote = async (e) => {
    e.preventDefault()
    if (!title || !content) return
    try {
      await axios.post('http://localhost:8000/notes', { title, content })
      setTitle('')
      setContent('')
      fetchNotes()
    } catch (err) {
      console.error(err)
    }
  }

  const deleteNote = async (id) => {
    try {
      await axios.delete(`http://localhost:8000/notes/${id}`)
      fetchNotes()
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    fetchNotes()
  }, [])

  return (
    <div className="container">
      <h1>EchoVault</h1>
      <form onSubmit={addNote} className="note-form">
        <input 
          type="text" 
          placeholder="Title" 
          value={title} 
          onChange={(e) => setTitle(e.target.value)} 
        />
        <textarea 
          placeholder="Content" 
          value={content} 
          onChange={(e) => setContent(e.target.value)} 
        />
        <button type="submit">Add Note</button>
      </form>

      <div className="notes-grid">
        {notes.map(note => (
          <div key={note.id} className="note-card">
            <h3>{note.title}</h3>
            <p>{note.content}</p>
            <button onClick={() => deleteNote(note.id)} className="delete-btn">x</button>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App

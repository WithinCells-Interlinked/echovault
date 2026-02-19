import { useState, useEffect } from 'react'
import { getNotes, createNote, deleteNote as apiDeleteNote, createSubscription } from './services/api'
import './App.css'

function App() {
  const [notes, setNotes] = useState([])
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [isSubscribed, setIsSubscribed] = useState(false)

  const fetchNotes = async () => {
    try {
      const data = await getNotes()
      setNotes(Array.isArray(data) ? data : [])
    } catch (err) {
      console.error(err)
    }
  }

  const subscribeUser = async () => {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js');
        const subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: 'BNBNV-3pkq0PU9RHlGa5H_NbDdw-MBBSIZZFZ2BfMgjjU7ZhtrLs9cL0YgyBDF0Alg4cfdAHwSFA8qPJI6AJoj8'
        });

        const subData = subscription.toJSON();
        await createSubscription({
          endpoint: subData.endpoint,
          p256dh: subData.keys.p256dh,
          auth: subData.keys.auth
        });
        
        setIsSubscribed(true);
        console.log('User is subscribed.');
      } catch (err) {
        console.error('Failed to subscribe user: ', err);
      }
    }
  };

  const addNote = async (e) => {
    e.preventDefault()
    if (!title || !content) return
    try {
      await createNote({ title, content })
      setTitle('')
      setContent('')
      fetchNotes()
    } catch (err) {
      console.error(err)
    }
  }

  const handleDeleteNote = async (id) => {
    try {
      await apiDeleteNote(id)
      fetchNotes()
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    fetchNotes()
    // Check for existing subscription
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.ready.then(registration => {
        registration.pushManager.getSubscription().then(subscription => {
          setIsSubscribed(!!subscription);
        });
      });
    }
  }, [])

  return (
    <div className="container">
      <div className="header-flex">
        <h1>EchoVault</h1>
        {!isSubscribed && (
          <button onClick={subscribeUser} className="subscribe-btn">
            Enable Notifications
          </button>
        )}
      </div>
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
            <button onClick={() => handleDeleteNote(note.id)} className="delete-btn">x</button>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App

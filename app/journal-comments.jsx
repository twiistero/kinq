'use client';

import {useEffect, useState} from 'react';

const dateLabel = value => new Date(value).toLocaleDateString('fr-FR', {day: 'numeric', month: 'long', year: 'numeric'});

export default function JournalComments({slug}) {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [sending, setSending] = useState(false);

  useEffect(() => {
    let active = true;
    fetch(`/api/journal/${encodeURIComponent(slug)}/comments`)
      .then(response => {if (!response.ok) throw Error(); return response.json();})
      .then(rows => {if (active) setComments(rows);})
      .catch(() => {if (active) setError('Les commentaires sont momentanément indisponibles.');})
      .finally(() => {if (active) setLoading(false);});
    return () => {active = false;};
  }, [slug]);

  async function submit(event) {
    event.preventDefault();
    if (sending) return;
    setSending(true);
    setNotice('');
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form));
    try {
      const response = await fetch(`/api/journal/${encodeURIComponent(slug)}/comments`, {
        method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data),
      });
      if (!response.ok) throw Error();
      form.reset();
      setNotice('Merci ! Ton message sera visible après validation par l’équipe.');
    } catch {
      setNotice('Envoi impossible pour le moment. Réessaie dans quelques instants.');
    } finally {
      setSending(false);
    }
  }

  return <section className="nt-comments" aria-labelledby="journal-comments-title">
    <div className="nt-comments-intro"><p className="eyebrow">LA CONVERSATION CONTINUE</p><h2 id="journal-comments-title">On en parle ?</h2><p>Partage ton point de vue ou pose une question. L’équipe lit chaque message avant sa publication.</p></div>
    <div className="nt-comments-layout">
      <div className="nt-comments-list" aria-live="polite">
        <h3>Les messages <span>{!loading && !error ? comments.length : ''}</span></h3>
        {loading && <p className="nt-comments-note">Chargement des messages…</p>}
        {error && <p className="nt-comments-note">{error}</p>}
        {!loading && !error && comments.length === 0 && <p className="nt-comments-note">Pas encore de message. Lance la conversation !</p>}
        {comments.map(comment => <article className="nt-comment" key={comment.id}>
          <div className="nt-comment-meta"><strong>{comment.author_name}</strong><time dateTime={comment.created_at}>{dateLabel(comment.created_at)}</time></div>
          <p>{comment.body}</p>
          {comment.replies.map(reply => <div className="nt-comment-reply" key={reply.id}>
            <div className="nt-comment-meta"><strong>Kinq Team <span>ÉQUIPE</span></strong><time dateTime={reply.created_at}>{dateLabel(reply.created_at)}</time></div>
            <p>{reply.body}</p>
          </div>)}
        </article>)}
      </div>
      <form className="nt-comment-form" onSubmit={submit}>
        <h3>Écris ton message</h3><p>Il sera relu avant d’apparaître ici.</p>
        <label>Ton prénom ou pseudo<input name="author_name" type="text" minLength="1" maxLength="80" autoComplete="nickname" required/></label>
        <label>Ton message<textarea name="body" minLength="1" maxLength="2000" rows="6" required/></label>
        <div className="nt-comment-trap" aria-hidden="true"><label>Site web<input name="website" type="text" tabIndex="-1" autoComplete="off"/></label></div>
        <button className="button" type="submit" disabled={sending}>{sending ? 'Envoi en cours…' : 'Envoyer mon message'}</button>
        {notice && <p className="nt-comment-feedback" role="status">{notice}</p>}
      </form>
    </div>
  </section>;
}

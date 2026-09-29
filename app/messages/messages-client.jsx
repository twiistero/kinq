'use client';

import {useEffect, useRef, useState} from 'react';
import {Ban, Pin} from 'lucide-react';

const startingChats = [
  {id:'alex', name:'Alex', age:32, city:'Paris', code:'KQ-7M4X9P', mood:'Curieux, sans se presser', common:['Leather','Aftercare','Paris'], portrait:'lime', online:true, mutualHook:true, status:'À découvrir', unread:2, time:'14:32', intro:'J’aime les échanges francs, les détails qu’on remarque et les plans qui se construisent à deux.', spark:'Vous avez accroché sur le même univers.', messages:[{from:'them',text:'J’ai vu ton Pin sur le cuir. Le tien, c’est plutôt une silhouette ou toute une ambiance ?',time:'14:26'},{from:'me',text:'Les deux, je crois. Le détail qui change tout, c’est l’attitude.',time:'14:29'},{from:'them',text:'On est d’accord. Et pour toi, qu’est-ce qui fait qu’une rencontre passe du joli profil au vrai feeling ?',time:'14:32'}]},
  {id:'tom', name:'Tom', age:28, city:'Lyon', code:'KQ-2F8L6S', mood:'De l’humour et du répondant', common:['Sportswear','Musique'], portrait:'violet', online:true, mutualHook:false, status:'Nouveau Hook', unread:1, time:'Hier', intro:'La bonne conversation commence souvent par une question que personne d’autre n’aurait posée.', spark:'Tom t’a envoyé un Hook.', messages:[{from:'them',text:'Question très sérieuse : on choisit d’abord la playlist ou le lieu du premier verre ?',time:'19:42'}]},
  {id:'max', name:'Max', age:35, city:'Bordeaux', code:'KQ-9C3B1R', mood:'Prendre le temps', common:['Rubber','Photo'], portrait:'orange', online:false, mutualHook:false, status:'En cours', unread:0, time:'Lun.', intro:'Je préfère une belle discussion à dix messages copiés collés.', spark:'Une conversation qui prend son rythme.', messages:[{from:'me',text:'Tu parlais de photo. Tu as un endroit préféré pour te balader et regarder la ville autrement ?',time:'18:08'},{from:'them',text:'Les quais, tôt le matin. Bordeaux est différente quand elle appartient encore aux marcheurs.',time:'18:14'}]},
  {id:'sacha', name:'Sacha', age:38, city:'Paris', code:'KQ-5D7A2V', mood:'Ouvert aux surprises', common:['Bondage','Rubber'], portrait:'blue', online:false, mutualHook:true, status:'En cours', unread:0, time:'Dim.', intro:'Les meilleures histoires commencent quand on ose être un peu soi.', spark:'Déjà quelques mots en commun.', messages:[{from:'them',text:'J’ai noté ton conseil de film. Verdict : très bon choix.',time:'21:06'},{from:'me',text:'Je prends ce compliment très au sérieux. À ton tour de m’en trouver un.',time:'21:11'}]},
];

function Icon({name, size = 20}) {
  const paths = {
    arrow:<path d="M4 12h16m-6-6 6 6-6 6"/>, back:<path d="M20 12H4m6-6-6 6 6 6"/>, plus:<path d="M12 5v14M5 12h14"/>,
    search:<><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></>,
    spark:<path d="m12 2 1.7 6.3L20 10l-6.3 1.7L12 18l-1.7-6.3L4 10l6.3-1.7L12 2Z"/>,
    close:<path d="M5 5l14 14M19 5 5 19"/>,
    hook:<path d="M7 3v12a5 5 0 0 0 10 0v-5l-4 4"/>,
    smile:<><circle cx="12" cy="12" r="9"/><path d="M8 14c1 2 2.3 3 4 3s3-1 4-3M9 9h.01M15 9h.01"/></>,
    image:<><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m3 17 5-5 4 4 3-3 6 6"/></>,
    clock:<><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
    lock:<><rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}

const portraits = {
  alex: 'https://static.wixstatic.com/media/739d69_8f8ce9ef74c34d25803f679a3f8127e4~mv2.jpg/v1/fill/w_480%2Ch_720%2Cal_c%2Cq_80%2Cusm_0.66_1.00_0.01%2Cenc_avif%2Cquality_auto/739d69_8f8ce9ef74c34d25803f679a3f8127e4~mv2.jpg',
  tom: 'https://mr-riegillio.com/cdn/shop/articles/sylven-meets-rj-585763.jpg?v=1607874225&width=1200',
  max: 'https://www.invinciblerubber.com/image/cache/catalog/SU056_h-840x840.jpg',
};
function Avatar({chat}) {
  return <span className={`mc-avatar${portraits[chat.id] ? '' : ' mc-avatar-private'}`}><img src={portraits[chat.id] || '/assets/kinq-symbol.svg'} alt=""/></span>;
}
const reactionOptions = ['❤️','🔥','😂','😍','👍','😘','😮','🥹','👏','🖤','😈','👀'];
const timeNow = () => new Intl.DateTimeFormat('fr-FR', {hour:'2-digit',minute:'2-digit'}).format(new Date());

export default function MessagesClient() {
  const [chats, setChats] = useState(startingChats);
  const [activeId, setActiveId] = useState('alex');
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('all');
  const [drafts, setDrafts] = useState({});
  const [pinned, setPinned] = useState({alex:true});
  const [blocked, setBlocked] = useState({});
  const [reactions, setReactions] = useState({});
  const [reactionPicker, setReactionPicker] = useState(null);
  const [showThread, setShowThread] = useState(false);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState('normal');
  const [menuOpen, setMenuOpen] = useState(false);
  const [ephemeral, setEphemeral] = useState({});
  const endRef = useRef(null);
  const inputRef = useRef(null);
  const photoRef = useRef(null);
  const objectUrls = useRef([]);
  const timers = useRef([]);
  const active = chats.find(chat => chat.id === activeId) || chats[0];
  const isBlocked = !!blocked[activeId];
  const draft = drafts[activeId] || '';
  const setDraft = value => setDrafts(current => ({...current,[activeId]:value}));
  const unreadCount = chats.reduce((count, chat) => count + chat.unread, 0);
  const visible = chats.filter(chat => (filter === 'all' || chat.unread > 0) && `${chat.name} ${chat.city}`.toLocaleLowerCase('fr').includes(query.toLocaleLowerCase('fr').trim()));

  useEffect(() => {
    setLoading(true);
    const timer = setTimeout(() => setLoading(false), 650);
    return () => clearTimeout(timer);
  }, [activeId]);
  useEffect(() => {
    if (!loading) {
      const scroll = endRef.current?.closest('.mc-conversation-scroll');
      if (scroll) scroll.scrollTop = scroll.scrollHeight;
    }
  }, [activeId, chats, loading]);
  useEffect(() => () => {
    timers.current.forEach(clearTimeout);
    objectUrls.current.forEach(URL.revokeObjectURL);
  }, []);

  function openChat(id) {
    setActiveId(id);
    setChats(current => current.map(chat => chat.id === id ? {...chat,unread:0} : chat));
    setShowThread(true);
    setReactionPicker(null);
    setMenuOpen(false);
    setMode('normal');
  }
  function addMessage(message) {
    setChats(current => current.map(chat => chat.id === activeId ? {...chat,messages:[...chat.messages,{from:'me',time:timeNow(),local:true,id:`local-${Date.now()}-${Math.random()}`,...message}],time:timeNow()} : chat));
  }
  function sendMessage(event) {
    event.preventDefault();
    const text = draft.trim();
    if (!text || isBlocked) return;
    addMessage({text,kind:mode === 'ephemeral' ? 'ephemeral' : 'text'});
    setDraft('');
    setMode('normal');
    inputRef.current?.focus();
  }
  function sendAlbum() {
    if (isBlocked) return;
    addMessage({kind:'album',text:'Invitation à découvrir mon album privé'});
    setMenuOpen(false);
  }
  function sendPhoto(event) {
    if (isBlocked) return;
    const file = event.target.files?.[0];
    if (!file || !file.type.startsWith('image/')) return;
    const url = URL.createObjectURL(file);
    objectUrls.current.push(url);
    addMessage({kind:'photo',text:'Photo éphémère',url});
    event.target.value = '';
    setMenuOpen(false);
  }
  function reveal(message) {
    if (ephemeral[message.id]) return;
    setEphemeral(current => ({...current,[message.id]:'visible'}));
    timers.current.push(setTimeout(() => setEphemeral(current => ({...current,[message.id]:'expired'})),10000));
  }
  function react(key,emoji) {
    setReactions(current => ({...current,[key]:current[key] === emoji ? null : emoji}));
    setReactionPicker(null);
  }

  return <main id="page-main" className={`discovery kinq-messages${showThread ? ' mc-thread-open' : ''}`}>
    <div className="discovery-inner wrap">
      <header className="space-heading"><h1>Mes <em>discussions.</em></h1><span className="space-demo"><i/>Aperçu de la messagerie</span></header>
      <nav className="space-tabs mc-space-tabs" aria-label="Espace rencontres">
        <a href="/rencontres">Découvrir</a><a href="/rencontres?view=pins">Mes Pins</a><a href="/rencontres?view=hooks">Mes Hooks</a><a href="/messages" aria-current="page">Messages <span>{unreadCount || ''}</span></a><a href="/mon-profil">Mon profil</a>
      </nav>
      <div className="mc-workspace">
        <section className="mc-inbox" aria-label="Conversations en cours">
          <div className="mc-inbox-heading"><h2>Entre nous.</h2></div>
          <label className="mc-search"><Icon name="search" size={17}/><input type="search" value={query} onChange={event => setQuery(event.target.value)} placeholder="Retrouver quelqu’un…" aria-label="Rechercher une conversation"/></label>
          <div className="mc-filters" role="group" aria-label="Filtrer les conversations"><button type="button" aria-pressed={filter === 'all'} onClick={() => setFilter('all')}>Tous les échanges <span>{chats.length}</span></button><button type="button" aria-pressed={filter === 'unread'} onClick={() => setFilter('unread')}>À lire <span>{unreadCount}</span></button></div>
          <div className="mc-chat-list">
            {visible.length ? visible.map(chat => <button type="button" className={`mc-chat-card${activeId === chat.id ? ' is-active' : ''}`} key={chat.id} onClick={() => openChat(chat.id)} aria-current={activeId === chat.id ? 'true' : undefined}>
              <Avatar chat={chat}/><span className="mc-chat-copy"><span className="mc-chat-top"><strong>{chat.name}<small>{chat.age}</small></strong><span className="mc-chat-meta"><time>{chat.time}</time>{chat.unread > 0 && <span className="mc-unread" aria-label={`${chat.unread} messages non lus`}>{chat.unread}</span>}</span></span><span className="mc-chat-place">{chat.city}<span className={`mc-presence${chat.online ? ' is-online' : ''}`}/><span className="mc-presence-label">{chat.online ? 'En ligne' : 'Hors ligne'}</span></span><span className="mc-chat-preview">{drafts[chat.id] ? `Brouillon : ${drafts[chat.id]}` : chat.messages.at(-1)?.text}</span></span>
            </button>) : <div className="mc-empty"><strong>Aucun échange ici.</strong><p>Essaie un autre mot ou affiche tous les échanges.</p></div>}
          </div>
        </section>
        <section className="mc-thread" aria-label={`Conversation avec ${active.name}`}>
          <header className="mc-thread-head"><button className="mc-mobile-back" type="button" onClick={() => setShowThread(false)} aria-label="Retour aux conversations"><Icon name="back"/></button><Avatar chat={active}/><div className="mc-thread-person"><h2>{active.name}<span>{active.age}</span>{active.mutualHook && <span className="mc-mutual-hook" title="Hook commun" aria-label="Hook commun"><Icon name="hook" size={18}/></span>}</h2><p>{active.city} · <span className={`mc-presence${active.online ? ' is-online' : ''}`}/><span className="mc-presence-label">{active.online ? 'En ligne' : 'Hors ligne'}</span></p></div><div className="mc-thread-actions"><button className="mc-pin-chat" type="button" onClick={() => setPinned(current => ({...current,[activeId]:!current[activeId]}))} aria-pressed={!!pinned[activeId]} aria-label={pinned[activeId] ? 'Retirer cette discussion des Pins' : 'Ajouter cette discussion aux Pins'} title={pinned[activeId] ? 'Discussion épinglée' : 'Épingler la discussion'}><Pin size={20} aria-hidden="true"/></button><button className="mc-block-chat" type="button" onClick={() => {setBlocked(current => ({...current,[activeId]:!current[activeId]}));setMenuOpen(false);setReactionPicker(null);}} aria-pressed={isBlocked} aria-label={isBlocked ? `Débloquer ${active.name}` : `Bloquer ${active.name}`} title={isBlocked ? `Débloquer ${active.name}` : `Bloquer ${active.name}`}><Ban size={19} aria-hidden="true"/></button></div></header>
          <div className="mc-thread-body"><div className="mc-conversation-scroll">
            {loading ? <div className="mc-message-loader" role="status"><img src="/assets/kinq-symbol.svg" alt=""/><span>Les messages arrivent…</span></div> : <>
              <div className="mc-messages" role="log" aria-label="Messages de la conversation" aria-live="polite">
                {active.messages.map((message,index) => {
                  const key = `${activeId}:${message.id || index}`;
                  const temporary = message.kind === 'ephemeral' || message.kind === 'photo';
                  const state = ephemeral[message.id];
                  return <div className={`mc-message mc-message--${message.from} mc-message--arriving`} style={{'--message-index':Math.min(index,8)}} key={key}><div className="mc-message-caption"><span>{message.from === 'me' ? 'Toi' : active.name}</span><time>{message.time}</time></div><div className="mc-message-content">
                    {temporary ? <button className={`mc-ephemeral mc-ephemeral--${state || 'sealed'}`} type="button" onClick={() => reveal(message)} disabled={!!state} aria-label={state === 'expired' ? 'Contenu éphémère expiré' : state === 'visible' ? 'Contenu éphémère affiché' : 'Afficher le contenu éphémère pendant 10 secondes'}><Icon name={message.kind === 'photo' ? 'image' : 'clock'} size={18}/>{state === 'visible' ? message.kind === 'photo' ? <img src={message.url} alt="Photo éphémère locale"/> : <span>{message.text}</span> : <span>{state === 'expired' ? 'Ce moment est passé.' : `${message.kind === 'photo' ? 'Photo' : 'Message'} éphémère · toucher pour voir`}</span>}</button> : message.kind === 'album' ? <div className="mc-album"><Icon name="lock" size={20}/><span>Album privé<small>{message.text} · aperçu uniquement</small></span></div> : <p>{message.text}</p>}
                    {!isBlocked && <div className="mc-react-area"><button type="button" className="mc-react-button" aria-label={`Réagir au message de ${message.from === 'me' ? 'toi' : active.name}`} aria-expanded={reactionPicker === key} onClick={() => setReactionPicker(reactionPicker === key ? null : key)}><Icon name="smile" size={17}/></button>{reactionPicker === key && <div className="mc-reaction-picker" role="group" aria-label="Choisir une réaction">{reactionOptions.map(emoji => <button type="button" key={emoji} onClick={() => react(key,emoji)} aria-label={`Réagir avec ${emoji}`}>{emoji}</button>)}</div>}</div>}
                  </div>{reactions[key] && <button className="mc-reaction-mark" type="button" onClick={() => react(key,reactions[key])} aria-label="Retirer ma réaction">{reactions[key]}</button>}{message.local && <small>Aperçu local · non transmis</small>}</div>;
                })}
                <div ref={endRef}/>
              </div><div className="mc-end-messages">Fin des messages</div>
            </>}
          </div></div>
          <div className="mc-composer-zone">
            {isBlocked ? <p className="mc-blocked-note">{active.name} est bloqué. Débloque cette personne pour reprendre la discussion.</p> : <>
            {menuOpen && <div id="mc-attachments" className="mc-attachments"><button type="button" onClick={sendAlbum}><Icon name="lock" size={18}/>Partager mon album privé</button><button type="button" onClick={() => {setMode(mode === 'ephemeral' ? 'normal' : 'ephemeral');setMenuOpen(false);inputRef.current?.focus();}}><Icon name="clock" size={18}/>{mode === 'ephemeral' ? 'Revenir au message classique' : 'Message éphémère'}</button><button type="button" onClick={() => photoRef.current?.click()}><Icon name="image" size={18}/>Photo éphémère</button></div>}
            <input ref={photoRef} type="file" accept="image/*" className="mc-sr-only" onChange={sendPhoto} aria-label="Choisir une photo éphémère"/>
            <form className="mc-composer" onSubmit={sendMessage}><button type="button" className="mc-attach-toggle" onClick={() => setMenuOpen(!menuOpen)} aria-expanded={menuOpen} aria-controls="mc-attachments" aria-label="Ajouter à la discussion"><Icon name="plus" size={19}/></button><label htmlFor="mc-message-input" className="mc-sr-only">Écrire un message à {active.name}</label><textarea id="mc-message-input" ref={inputRef} value={draft} maxLength={1000} rows="1" placeholder={mode === 'ephemeral' ? 'Message éphémère · visible 10 secondes…' : `Un mot pour ${active.name}…`} onChange={event => setDraft(event.target.value)} onKeyDown={event => {if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {event.preventDefault();sendMessage(event);}}}/><button type="submit" disabled={!draft.trim()} aria-label="Ajouter le message à l’aperçu"><Icon name="arrow" size={20}/></button></form></>}
          </div>
        </section>
      </div>
      <p className="mc-demo-note">Aperçu interactif · profils fictifs et photos d’illustration. Les messages et les photos restent dans cette page et disparaissent en la quittant.</p>
    </div>
  </main>;
}

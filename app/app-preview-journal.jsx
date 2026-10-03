// A presentation of the published journal, using the same server articles as the home.
export default function AppPreviewJournal({published}) {
  const selection = published.slice(0, 2);
  return <div className="preview-journal">
    <div className="preview-journal-heading"><strong>NO TABOO<span>.</span></strong><svg aria-hidden="true"><use href="#search"/></svg></div>
    <span className="preview-journal-label">LE JOURNAL KINQ</span>
    <div className="preview-journal-categories"><span>À la une</span><span>Désirs</span><span>Culture kink</span></div>
    <div className="preview-journal-articles">{selection.length ? selection.map((article, index) => <article key={article.slug}>
      <div className={`preview-journal-cover cover-${index}`}>
        {(article.art_words?.length ? article.art_words : [article.title]).slice(0, 3).map((word, i) => <strong key={i}>{word}</strong>)}
        <svg aria-hidden="true"><use href="#up"/></svg>
      </div>
      <div className="preview-journal-copy"><small>{article.category}</small><strong>{article.title}</strong></div>
    </article>) : <p>Articles indisponibles pour le moment.</p>}</div>
    <div className="preview-journal-link">Explorer le journal <svg aria-hidden="true"><use href="#arrow"/></svg></div>
  </div>;
}

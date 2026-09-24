#!/usr/bin/env python3
"""Build the public delivery catalogue and isolated client pages from status.json."""
import html
import json
from pathlib import Path
from urllib.parse import urlparse, quote

ROOT = Path(__file__).resolve().parent
BASE = 'https://codenolimits.github.io/dreamnova-suivi/'
LABELS = {'available': 'À découvrir', 'review': 'Version en revue'}

def esc(value):
    return html.escape(str(value), quote=True)

def url(value):
    parsed = urlparse(value)
    if parsed.scheme != 'https' or not parsed.netloc:
        raise ValueError(f'Only public HTTPS links are accepted: {value}')
    return esc(value)

def badge(project):
    return f'<span class="badge {esc(project["status"])}"><i aria-hidden="true"></i>{esc(project.get('statusLabel', LABELS[project['status']]))}</span>'

def visual(p, path, large=False):
    content = f'<img src="{url(p["cover"])}" alt="{esc(p.get('coverAlt', p['title']))}" loading="lazy" width="1000" height="640">' if p.get('cover') else f'<span class="project-mark" aria-hidden="true">{esc(p["mark"])}</span><span class="orbit orbit-a"></span><span class="orbit orbit-b"></span><span class="visual-caption">{esc(p["category"])}</span>'
    return f'<div class="project-visual {"large" if large else ""}" style="--accent:{esc(p["accent"])}">{content}</div>'

def shell(title, description, body, prefix, canonical, client=False):
    revision = json.loads((ROOT / 'status.json').read_text())['updatedAt']
    version = quote(revision, safe='')
    nav = '<a class="top-link" href="https://dreamnova.studio/" target="_blank" rel="noopener">Le studio <span aria-hidden="true">↗</span></a>'
    return f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="portal-revision" content="{esc(revision)}"><meta name="portal-data" content="{prefix}status.json"><meta name="theme-color" content="#f3f0e8"><meta name="description" content="{esc(description)}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:type" content="website"><link rel="canonical" href="{canonical}"><link rel="icon" type="image/svg+xml" href="{prefix}assets/favicon.svg"><title>{esc(title)}</title><link rel="stylesheet" href="{prefix}assets/portal.css?v={version}"></head><body class="{'client-page' if client else 'catalogue-page'}"><a class="skip" href="#main">Aller au contenu</a><header class="site-header"><a class="brand" href="https://dreamnova.studio/" aria-label="DreamNova Studio"><span class="brand-symbol" aria-hidden="true">✳</span><span>DREAMNOVA<small>STUDIO / LIVRAISONS</small></span></a>{nav}</header><aside class="publication" aria-label="État de publication"><div>Publication du <time datetime="{esc(revision)}" data-updated>{esc(revision)}</time></div><div class="freshness-controls"><span data-freshness aria-live="polite">Vérification de la version…</span><button type="button" data-refresh hidden>Actualiser les liens</button></div></aside>{body}<footer class="site-footer"><span>DreamNova Studio</span><span>Créations, expériences & édition · 2026</span></footer><script src="{prefix}assets/portal.js?v={version}" defer></script></body></html>'''

def build():
    data = json.loads((ROOT / 'status.json').read_text())
    projects = data['projects']
    ids = set()
    cards = []
    categories = list(dict.fromkeys(p['category'] for p in projects))
    for number, p in enumerate(projects, 1):
        if p['id'] in ids or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in p['id']):
            raise ValueError('Invalid or duplicate project id')
        ids.add(p['id'])
        project_url = 'projets/' + p['id'] + '/'
        cards.append(f'''<article class="project-card" data-project data-category="{esc(p['category'])}" data-search="{esc(p['title']+' '+p['category']+' '+p['summary'])}"><a class="visual-link" href="{project_url}" aria-label="Découvrir {esc(p['title'])}">{visual(p, '')}<span class="visual-arrow" aria-hidden="true">↗</span></a><div class="card-meta"><span>{number:02d} / {esc(p['category'])}</span>{badge(p)}</div><h2><a href="{project_url}">{esc(p['title'])}</a></h2><p>{esc(p['summary'])}</p><a class="text-link" href="{project_url}">Voir les livrables <span aria-hidden="true">↗</span></a></article>''')
        link_html = ''.join(f'<a class="resource" href="{url(item["url"])}" target="_blank" rel="noopener noreferrer"><span class="resource-icon" aria-hidden="true">{"↓" if item["kind"]=="pdf" else "↗"}</span><span><strong>{esc(item["label"])}</strong><small>{"Document PDF · ouvrir ou enregistrer" if item["kind"]=="pdf" else "Accès direct"}</small></span><span aria-hidden="true">↗</span></a>' for item in p['links'])
        media_html = ''
        if p['media']:
            media_items = []
            for media in p['media']:
                poster = f' poster="{url(media["poster"])}"' if media.get('poster') else ''
                media_items.append(f'''<article class="film {esc(media.get('format','landscape'))}"><video controls preload="none" playsinline{poster} aria-label="{esc(media['title'])}"><source src="{url(media['url'])}" type="video/mp4"><p><a href="{url(media['url'])}">Ouvrir la vidéo MP4</a></p></video><div class="film-caption"><div><h3>{esc(media['title'])}</h3><p>{esc(media['description'])}</p></div><a class="download-link" href="{url(media['url'])}" target="_blank" rel="noopener noreferrer" download data-download>↓ Télécharger</a></div></article>''')
            media_html = '<section class="media-section" aria-labelledby="films-title"><div class="section-heading"><span class="eyebrow">À regarder</span><h2 id="films-title">Les films</h2><p>Regardez les vidéos ici, puis téléchargez chaque fichier MP4 avec son lien direct.</p></div><div class="film-grid">'+''.join(media_items)+'</div></section>'
        delivered = ''.join('<li><span aria-hidden="true">↗</span>'+esc(s)+'</li>' for s in p['deliverables'])
        notes = ''.join('<p>'+esc(s)+'</p>' for s in p['notes'])
        body = f'''<main id="main"><section class="client-hero"><div class="client-intro"><div class="eyebrow">{esc(p['category'])}</div><h1>{esc(p['title'])}</h1><p class="lead">{esc(p['summary'])}</p><div class="client-actions">{badge(p)}<button type="button" class="share-button" data-share>Partager cette page <span aria-hidden="true">↗</span></button></div><p class="share-feedback" aria-live="polite"></p></div>{visual(p,'',True)}</section><section class="delivery-section"><div><span class="eyebrow">Dans cette livraison</span><h2>Un accès à chaque création.</h2><ul class="deliverables">{delivered}</ul></div><div class="resources">{link_html}</div></section>{media_html}<section class="review-note"><span class="eyebrow">À savoir</span><div>{notes}</div></section><section class="share-note"><span class="share-icon" aria-hidden="true">↗</span><div><strong>Cette page est dédiée à {esc(p['title'])}.</strong><p>Partagez son adresse pour donner accès aux liens réunis ici.</p></div><a class="text-link" href="{BASE+project_url}">Lien direct</a></section></main>'''
        destination = ROOT / project_url
        destination.mkdir(parents=True, exist_ok=True)
        (destination / 'index.html').write_text(shell(p['title']+' · DreamNova',p['summary'],body,'../../',BASE+project_url,True))
    filters = '<button type="button" data-filter="all" aria-pressed="true">Tout voir <span>'+str(len(projects))+'</span></button>'+''.join(f'<button type="button" data-filter="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in categories)
    body = f'''<main id="main"><section class="hero"><div class="hero-top"><span class="eyebrow">Collection · Septembre 2026</span><span class="edition">{len(projects):02d} projets à découvrir</span></div><h1>Les créations.<br>Les accès.<br><em>Au même endroit.</em></h1><div class="hero-bottom"><p>Sites, films, livres et expériences. Retrouvez les livrables de chaque projet et sa page dédiée, prête à partager.</p><a class="jump-link" href="#collection" aria-label="Explorer les projets">↓</a></div></section><section id="collection" class="collection" aria-label="Projets"><div class="collection-toolbar"><div class="filters" aria-label="Filtrer les projets">{filters}</div><label class="search"><span class="sr-only">Rechercher un projet</span><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/></svg><input type="search" placeholder="Rechercher un projet" autocomplete="off" id="project-search"></label></div><p class="result-count" aria-live="polite">{len(projects)} projets</p><div class="project-grid">{''.join(cards)}</div><p class="empty-state" hidden>Aucun projet ne correspond. Essayez un autre nom ou une autre catégorie.</p></section><section class="catalogue-note"><div><span class="eyebrow">Des liens qui restent clairs</span><h2>Le bon projet.<br>La bonne page.</h2></div><div><p>Chaque projet possède une page indépendante : envoyez ce lien pour partager ses livrables.</p><p><strong>À découvrir</strong> indique un accès disponible. <strong>Version en revue</strong> indique un prototype ou une création encore en cours de validation. Les dossiers privés sont partagés séparément.</p><small>Mise à jour : <time datetime="{esc(data['updatedAt'])}" data-updated>{esc(data['updatedAt'])}</time></small></div></section></main>'''
    body = body.replace('</main>', '<section class="catalogue-note"><div><span class="eyebrow">Suivi des réalisations</span><h2>Les avancées.<br>Les prochaines étapes.</h2></div><div><p>Consultez les résultats vérifiés, les corrections et ce qui reste en cours, sans les échanges privés des clients.</p><a class="text-link" href="journal/">Ouvrir le compte rendu</a></div></section></main>')
    (ROOT/'index.html').write_text(shell('DreamNova · Les créations au même endroit','Les sites, films, livres et expériences DreamNova. Des liens directs et une page dédiée à chaque projet.',body,'',BASE))
    journal = data.get('journal', [])
    rows = ''.join(f'<article class="journal-entry"><div><span class="eyebrow">{esc(item["state"])}</span><h2>{esc(item["title"])}</h2></div><div><p>{esc(item["done"])}</p><p><strong>À poursuivre.</strong> {esc(item["next"])}</p></div></article>' for item in journal)
    journal_body = f'<main id="main"><section class="hero"><span class="eyebrow">Compte rendu public</span><h1>Ce qui avance.<br><em>Ce qui reste.</em></h1><p>Des faits vérifiés et les décisions utiles pour suivre les projets. Les dossiers de travail confidentiels sont conservés séparément.</p><a class="text-link" href="../">← Tous les projets et téléchargements</a></section><section class="journal-entries">{rows}</section></main>'
    (ROOT/'journal').mkdir(exist_ok=True)
    (ROOT/'journal/index.html').write_text(shell('Compte rendu · DreamNova', 'Les résultats vérifiés, corrections et prochaines étapes des projets DreamNova.', journal_body, '../', BASE+'journal/'))
    fallback = f'<main id="main"><section class="hero"><span class="eyebrow">Adresse introuvable</span><h1>Retrouvons<br><em>votre projet.</em></h1><p>Cette adresse ne correspond pas à une page disponible. Le catalogue rassemble les liens actuels et les téléchargements.</p><a class="share-button" href="{BASE}">Ouvrir le portail des projets ↗</a></section></main>'
    (ROOT/'404.html').write_text(shell('Retrouver votre projet · DreamNova', 'Accéder aux liens actuels des projets.', fallback, BASE, BASE))
    print(f'Built catalogue + {len(projects)} dedicated project pages')

if __name__ == '__main__':
    build()

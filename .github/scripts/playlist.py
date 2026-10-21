"""Met à jour playlist.json à partir de la playlist YouTube « Mes productions ».

Lancé par la GitHub Action .github/workflows/playlist.yml (aucune clé d'API :
on lit la page publique de la playlist). Le site lit ensuite playlist.json,
donc les visiteurs ne contactent pas YouTube pour ça.
"""
import base64, json, re, sys, urllib.request, http.client
from datetime import datetime, timezone

PLAYLIST_ID = 'PLefpG9mfor5Q'
SORTIE = 'playlist.json'
ENTETES = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36',
    'Accept-Language': 'fr-FR,fr;q=0.9',
    'Cookie': 'SOCS=CAI',  # évite la page de consentement de YouTube
}

def lire(url):
    req = urllib.request.Request(url, headers=ENTETES)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def donnees_initiales(html):
    m = re.search(r'var ytInitialData\s*=\s*(\{.*?\});\s*</script>', html, re.S)
    if not m:
        raise RuntimeError('ytInitialData introuvable')
    return json.loads(m.group(1))

def parcourir(o, cle):
    """Renvoie tous les objets rangés sous la clé `cle`, à n'importe quelle profondeur."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k == cle:
                yield v
            yield from parcourir(v, cle)
    elif isinstance(o, list):
        for v in o:
            yield from parcourir(v, cle)

def texte(o):
    if not o:
        return ''
    if 'simpleText' in o:
        return o['simpleText']
    return ''.join(r.get('text', '') for r in o.get('runs', []))

def chaine_de(o):
    for ep in parcourir(o, 'browseEndpoint'):
        if ep.get('browseId', '').startswith('UC') and ep.get('canonicalBaseUrl', '').startswith('/@'):
            return ep['canonicalBaseUrl'][2:]
    return None

def videos_de_la_playlist():
    data = donnees_initiales(lire(f'https://www.youtube.com/playlist?list={PLAYLIST_ID}').decode('utf-8'))
    vus, out = set(), []
    for v in parcourir(data, 'playlistVideoRenderer'):  # ancien format de page
        vid = v.get('videoId')
        if vid and vid not in vus:
            vus.add(vid)
            out.append({'id': vid, 'titre': texte(v.get('title')), 'nom': texte(v.get('shortBylineText')), 'handle': chaine_de(v.get('shortBylineText', {}))})
    for v in parcourir(data, 'lockupViewModel'):  # nouveau format de page
        vid = v.get('contentId')
        if not vid or vid in vus or v.get('contentType') not in (None, 'LOCKUP_CONTENT_TYPE_VIDEO'):
            continue
        meta = v.get('metadata', {}).get('lockupMetadataViewModel', {})
        noms = [p.get('text', {}).get('content', '') for p in parcourir(meta, 'metadataParts')
                for p in (p if isinstance(p, list) else [p])]
        vus.add(vid)
        out.append({'id': vid, 'titre': meta.get('title', {}).get('content', ''), 'nom': next((n for n in noms if n), ''), 'handle': chaine_de(v)})
    return out

def est_un_short(vid):
    """/shorts/ID répond 200 pour un Short et redirige (303) pour une vidéo classique."""
    c = http.client.HTTPSConnection('www.youtube.com', timeout=30)
    c.request('HEAD', f'/shorts/{vid}', headers=ENTETES)
    statut = c.getresponse().status
    c.close()
    return statut == 200

def avatar(handle):
    """Photo de profil de la chaîne, réduite et intégrée (pas d'appel à Google côté visiteur)."""
    html = lire(f'https://www.youtube.com/@{handle}').decode('utf-8')
    m = re.search(r'<meta property="og:image" content="([^"]+)"', html)
    if not m:
        return None
    url = re.sub(r'=s\d+.*$', '=s176-c-k-c0x00ffffff-no-rj', m.group(1))
    return 'data:image/jpeg;base64,' + base64.b64encode(lire(url)).decode()

def main():
    videos = videos_de_la_playlist()
    if not videos:
        sys.exit('Aucune vidéo trouvée : la page YouTube a peut-être changé, playlist.json est laissé tel quel.')
    try:
        ancien = json.load(open(SORTIE, encoding='utf-8'))
    except (OSError, ValueError):
        ancien = {}
    anciens_avatars = ancien.get('avatars', {})
    avatars = {}
    for v in videos:
        v['format'] = 'v' if est_un_short(v['id']) else 'h'
        h = v.pop('handle') or ''
        v['chaine'] = f'https://www.youtube.com/@{h}' if h else ''
        if h and h not in avatars:
            try:
                avatars[h] = avatar(h) or anciens_avatars.get(h)
            except Exception as e:  # une photo qui manque ne doit pas bloquer la mise à jour
                print(f'avatar de @{h} indisponible : {e}')
                avatars[h] = anciens_avatars.get(h)
    nouveau = {'videos': videos, 'avatars': {k: v for k, v in avatars.items() if v}}
    if {k: ancien.get(k) for k in nouveau} == nouveau:
        print('Playlist inchangée.')
        return
    nouveau['maj'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    with open(SORTIE, 'w', encoding='utf-8') as f:
        json.dump(nouveau, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(f'{len(videos)} vidéos écrites dans {SORTIE}.')

if __name__ == '__main__':
    main()

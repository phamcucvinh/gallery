"""
build.py — Static site generator for an online art gallery.
"""

import html
import json
import os
import datetime

GALLERY_TITLE = "Gallery"
GALLERY_SUBTITLE = ""
ARTIST_NAME = ""
BATCH_SIZE = 50

IMAGES_DIR = "images"
OUTPUT_FILE = "index.html"
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def scan_images():
    entries = []
    if not os.path.isdir(IMAGES_DIR):
        return entries
    for fname in os.listdir(IMAGES_DIR):
        stem, ext = os.path.splitext(fname)
        if ext.lower() in SUPPORTED_EXTENSIONS:
            title = stem.replace("_", " ").replace("-", " ").title()
            entries.append((fname, title))
    entries.sort(key=lambda item: item[0])
    return entries


HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{meta_description}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Noto+Serif+KR:wght@400;700&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ background:#FAF7F2; color:#2C2C2C; font-family:'Playfair Display','Noto Serif KR',Georgia,serif; min-height:100vh; display:flex; flex-direction:column; }}
    .gallery-header {{ text-align:center; padding:4rem 2rem 2rem; }}
    .gallery-header h1 {{ font-size:3rem; font-weight:600; letter-spacing:0.06em; }}
    .gallery-header .subtitle {{ margin-top:0.5rem; font-size:1.15rem; font-style:italic; color:#B8977E; }}
    .gallery-header .count {{ margin-top:0.5rem; font-size:0.9rem; color:#B8977E; }}
    .divider {{ width:60px; height:2px; background:#B8977E; margin:1.5rem auto 0; }}
    .masonry {{ column-count:4; column-gap:1.5rem; padding:2rem 3rem; max-width:1400px; margin:0 auto; flex:1; }}
    .masonry figure {{
      break-inside:avoid; margin:0 0 1.5rem; background:#fff; border-radius:6px;
      overflow:hidden; box-shadow:0 2px 12px rgba(0,0,0,0.08);
      transition:box-shadow 0.3s, transform 0.3s;
      opacity:0; transform:translateY(20px);
      animation:fadeInUp 0.6s ease forwards;
      cursor:pointer;
    }}
    .masonry figure:hover {{ box-shadow:0 6px 24px rgba(0,0,0,0.14); transform:translateY(-3px); }}
    .masonry figure img {{ display:block; width:100%; height:auto; transition:transform 0.4s ease; }}
    .masonry figure:hover img {{ transform:scale(1.03); }}
    .masonry figcaption {{ padding:0.75rem 1rem; font-size:0.95rem; text-align:center; letter-spacing:0.02em; }}
    .load-more-wrap {{ text-align:center; padding:2rem; }}
    .load-more-btn {{ font-family:inherit; font-size:1rem; padding:0.8rem 2.5rem; background:#2C2C2C; color:#FAF7F2; border:none; border-radius:4px; cursor:pointer; letter-spacing:0.04em; transition:background 0.2s; }}
    .load-more-btn:hover {{ background:#B8977E; }}
    .gallery-footer {{ text-align:center; padding:2rem; font-size:0.85rem; color:#B8977E; letter-spacing:0.04em; }}
    @keyframes fadeInUp {{ to {{ opacity:1; transform:translateY(0); }} }}
    @media (max-width:1200px) {{ .masonry {{ column-count:3; }} }}
    @media (max-width:1024px) {{ .masonry {{ column-count:2; padding:1.5rem 2rem; }} }}
    @media (max-width:600px) {{ .masonry {{ column-count:1; padding:1rem; }} .gallery-header h1 {{ font-size:2rem; }} }}
  </style>
</head>
<body>
  <header class="gallery-header">
    <h1>{title}</h1>
    {subtitle_html}
    <p class="count" id="counter"></p>
    <div class="divider" role="presentation" aria-hidden="true"></div>
  </header>
  <main class="masonry" id="gallery"></main>
  <div class="load-more-wrap" id="load-more-wrap">
    <button class="load-more-btn" id="load-more-btn" onclick="loadMore()">Load More</button>
  </div>
  <footer class="gallery-footer">{footer_text}</footer>
  <script>
    var ALL_IMAGES={images_json};
    var BATCH={batch_size};
    var loaded=0;
    var gallery=document.getElementById('gallery');
    var counter=document.getElementById('counter');
    var wrap=document.getElementById('load-more-wrap');
    function goOrder(f){{ window.location.href='order.html?img='+encodeURIComponent(f); }}
    function loadMore(){{
      var end=Math.min(loaded+BATCH,ALL_IMAGES.length);
      var frag=document.createDocumentFragment();
      for(var i=loaded;i<end;i++){{
        var item=ALL_IMAGES[i];
        var fig=document.createElement('figure');
        fig.style.animationDelay=((i-loaded)*0.04)+'s';
        fig.setAttribute('onclick','goOrder("'+item[0].replace(/"/g,'&quot;')+'")');
        var img=document.createElement('img');
        img.src='images/'+item[0];
        img.alt=item[1];
        img.loading='lazy';
        var cap=document.createElement('figcaption');
        cap.textContent=item[1];
        fig.appendChild(img);
        fig.appendChild(cap);
        frag.appendChild(fig);
      }}
      gallery.appendChild(frag);
      loaded=end;
      counter.textContent=loaded+' / '+ALL_IMAGES.length;
      if(loaded>=ALL_IMAGES.length){{ wrap.style.display='none'; }}
    }}
    loadMore();
  </script>
</body>
</html>
"""


def generate_html(images):
    images_json = json.dumps(images, ensure_ascii=False)
    subtitle_html = ""
    if GALLERY_SUBTITLE:
        subtitle_html = '<p class="subtitle">{}</p>'.format(html.escape(GALLERY_SUBTITLE))
    year = datetime.datetime.now().year
    footer_text = "{} &copy; {}".format(html.escape(ARTIST_NAME), year) if ARTIST_NAME else "&copy; {}".format(year)
    safe_title = html.escape(GALLERY_TITLE)
    meta_description = "{} — an online art gallery".format(safe_title)
    return HTML_TEMPLATE.format(
        title=safe_title,
        meta_description=html.escape(meta_description, quote=True),
        subtitle_html=subtitle_html,
        images_json=images_json,
        batch_size=BATCH_SIZE,
        footer_text=footer_text,
    )


if __name__ == "__main__":
    images = scan_images()
    print("Found {} image(s)".format(len(images)))
    result = generate_html(images)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(result)
    print("Generated {} ({} bytes)".format(OUTPUT_FILE, len(result)))

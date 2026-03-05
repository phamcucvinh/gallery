"""
build.py — Static site generator for an online art gallery.

Scans images/ for supported image files, extracts display titles from
filenames, and generates a Masonry-layout index.html with lazy-loaded
images and responsive CSS columns.
"""

import html
import os
import datetime

# ── Configuration ──────────────────────────────────────────────────────
GALLERY_TITLE = "Gallery"
GALLERY_SUBTITLE = ""
ARTIST_NAME = ""

IMAGES_DIR = "images"
OUTPUT_FILE = "index.html"
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


# ── Image scanning ─────────────────────────────────────────────────────
def scan_images():
    """Scan the images/ directory for supported image files.

    Returns a sorted list of (filename, title) tuples.
    Title is derived from the filename: extension removed, underscores
    and hyphens replaced with spaces, then title-cased.
    """
    entries = []
    if not os.path.isdir(IMAGES_DIR):
        return entries

    for fname in os.listdir(IMAGES_DIR):
        stem, ext = os.path.splitext(fname)
        if ext.lower() in SUPPORTED_EXTENSIONS:
            title = stem.replace("_", " ").replace("-", " ")
            title = title.title()
            entries.append((fname, title))

    entries.sort(key=lambda item: item[0])
    return entries


# ── HTML template ──────────────────────────────────────────────────────
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
    *,
    *::before,
    *::after {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}

    body {{
      background-color: #FAF7F2;
      color: #2C2C2C;
      font-family: 'Playfair Display', 'Noto Serif KR', Georgia, serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    /* ── Header ─────────────────────────────── */
    .gallery-header {{
      text-align: center;
      padding: 4rem 2rem 2rem;
    }}

    .gallery-header h1 {{
      font-size: 3rem;
      font-weight: 600;
      letter-spacing: 0.06em;
      color: #2C2C2C;
    }}

    .gallery-header .subtitle {{
      margin-top: 0.5rem;
      font-size: 1.15rem;
      font-style: italic;
      color: #B8977E;
    }}

    .divider {{
      width: 60px;
      height: 2px;
      background: #B8977E;
      margin: 1.5rem auto 0;
    }}

    /* ── Masonry grid ───────────────────────── */
    .masonry {{
      column-count: 4;
      column-gap: 1.5rem;
      padding: 2rem 3rem;
      max-width: 1400px;
      margin: 0 auto;
      flex: 1;
    }}

    .masonry figure {{
      break-inside: avoid;
      margin: 0 0 1.5rem;
      background: #fff;
      border-radius: 6px;
      overflow: hidden;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
      transition: box-shadow 0.3s ease, transform 0.3s ease;
    }}

    .masonry figure:hover {{
      box-shadow: 0 6px 24px rgba(0, 0, 0, 0.14);
      transform: translateY(-3px);
    }}

    .masonry figure img {{
      display: block;
      width: 100%;
      height: auto;
    }}

    .masonry figcaption {{
      padding: 0.75rem 1rem;
      font-size: 0.95rem;
      color: #2C2C2C;
      text-align: center;
      letter-spacing: 0.02em;
    }}

    /* ── Footer ─────────────────────────────── */
    .gallery-footer {{
      text-align: center;
      padding: 2rem;
      font-size: 0.85rem;
      color: #B8977E;
      letter-spacing: 0.04em;
    }}

    /* ── Responsive breakpoints ──────────────── */
    @media (max-width: 1200px) {{
      .masonry {{
        column-count: 3;
      }}
    }}

    @media (max-width: 1024px) {{
      .masonry {{
        column-count: 2;
        padding: 1.5rem 2rem;
      }}
    }}

    @media (max-width: 600px) {{
      .masonry {{
        column-count: 1;
        padding: 1rem;
      }}

      .gallery-header h1 {{
        font-size: 2rem;
      }}
    }}
  </style>
</head>
<body>

  <header class="gallery-header">
    <h1>{title}</h1>
    {subtitle_html}
    <div class="divider" role="presentation" aria-hidden="true"></div>
  </header>

  <main class="masonry">
{figures}
  </main>

  <footer class="gallery-footer">
    {footer_text}
  </footer>

</body>
</html>
"""


# ── HTML generation ────────────────────────────────────────────────────
def generate_html(images):
    """Build the complete HTML string from a list of (filename, title) tuples."""
    # Build <figure> blocks
    figure_lines = []
    for filename, title in images:
        safe_src = html.escape(IMAGES_DIR + "/" + filename, quote=True)
        safe_alt = html.escape(title, quote=True)
        safe_caption = html.escape(title)
        figure_lines.append(
            '    <figure>\n'
            '      <img src="{src}" alt="{alt}" loading="lazy">\n'
            '      <figcaption>{caption}</figcaption>\n'
            '    </figure>'.format(
                src=safe_src,
                alt=safe_alt,
                caption=safe_caption,
            )
        )
    figures = "\n".join(figure_lines)

    # Subtitle
    if GALLERY_SUBTITLE:
        subtitle_html = '<p class="subtitle">{}</p>'.format(
            html.escape(GALLERY_SUBTITLE)
        )
    else:
        subtitle_html = ""

    # Footer
    year = datetime.datetime.now().year
    if ARTIST_NAME:
        footer_text = "{} &copy; {}".format(html.escape(ARTIST_NAME), year)
    else:
        footer_text = "&copy; {}".format(year)

    safe_title = html.escape(GALLERY_TITLE)
    meta_description = "{} — an online art gallery".format(safe_title)

    return HTML_TEMPLATE.format(
        title=safe_title,
        meta_description=html.escape(meta_description, quote=True),
        subtitle_html=subtitle_html,
        figures=figures,
        footer_text=footer_text,
    )


# ── Main entry point ──────────────────────────────────────────────────
if __name__ == "__main__":
    images = scan_images()
    print("Found {} image(s):".format(len(images)))
    for fname, title in images:
        print("  {} -> {}".format(fname, title))

    html = generate_html(images)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print("\nGenerated {} ({} bytes)".format(OUTPUT_FILE, len(html)))

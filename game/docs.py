from game import GAME_DISPLAY_NAME

# =====================================================================
# TODO: replace this with how YOUR game is played. It is served as a
# standalone page at /how-to-play and linked from the web's games list.
# =====================================================================
BODY = """
<h1>{title} — How to play</h1>

<p>Replace this page with the rules of your game: the board, the objective,
what a valid move looks like, scoring, and how a game ends.</p>

<h2>Example game (Sum Battle)</h2>
<ul>
  <li>Two players take turns.</li>
  <li>On your turn you submit a <code>number</code> from 1 to 10.</li>
  <li>The number is added to your score.</li>
  <li>After 20 turns the higher score wins.</li>
</ul>

<h2>Action</h2>
<pre>{{ "action": "play", "data": {{ "number": 7 }} }}</pre>
""".format(title=GAME_DISPLAY_NAME)


DOCS_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — How to play</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 720px; margin: 2rem auto;
            padding: 0 1rem; line-height: 1.5; color: #222; }}
    code, pre {{ background: #f4f4f4; padding: .1rem .35rem; border-radius: 4px; }}
    pre {{ padding: .75rem; overflow-x: auto; }}
    h1, h2 {{ line-height: 1.2; }}
  </style>
</head>
<body>
{body}
</body>
</html>""".format(title=GAME_DISPLAY_NAME, body=BODY)

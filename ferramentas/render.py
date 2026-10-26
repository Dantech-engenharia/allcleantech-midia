"""Gera carrosséis (PNG 1080x1350) e Reels (MP4 1080x1920) da AllCleantech a partir de um roteiro JSON.

Uso:  python3 ferramentas/render.py roteiro.json
Requer: playwright (Chromium) e ffmpeg. Saída na pasta indicada em "pasta" do roteiro.

Roteiro de carrossel:
{
  "tipo": "carrossel",
  "pasta": "posts/2026-11-02-tema",
  "slides": [
    {"kicker": "Causa raiz", "titulo": "Texto <em>destaque</em>", "texto": "apoio opcional",
     "fonte": "Fonte: X", "imagem": "entrada/foto.jpg (opcional)"}
  ],
  "cta": {"kicker": "Fale com a gente", "titulo": "Frase final"}
}

Roteiro de Reel:
{
  "tipo": "reel",
  "pasta": "posts/2026-11-03-tema",
  "cenas": [
    {"arquivo": "entrada/video.mp4", "inicio": 1.0, "duracao": 3.5,
     "recorte": [0.2, 0.0, 0.62, 0.62],   # opcional: x, y, largura, altura (frações do quadro)
     "desfoque": false,                   # opcional: true = fundo desfocado (para cena de texto)
     "kicker": "Automação", "titulo": "Texto <em>destaque</em>",
     "lista": [["agua", "Menos água", "apoio"]]   # opcional: cena de benefícios (ícones: agua, ete, equipe, tempo, seguro, vapor)
    }
  ],
  "cta": {"kicker": "Fim da 6x1", "titulo": "Automatize a limpeza.<br><em>Adapte sua escala.</em>"}
}
Imagens também podem ser cenas de Reel (arquivo .jpg/.png): viram cenas com leve zoom.
"""
import json, os, subprocess, sys, pathlib, tempfile
from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FONTES = RAIZ / "ferramentas" / "fonts"
LOGO = RAIZ / "marca" / "logo-allcleantech.png"
VERDE, CLARO, FUNDO = "#22A447", "#5BEA85", "#061609"

CSS = f"""
@font-face{{font-family:Archivo;src:url('file://{FONTES}/Archivo.ttf');font-weight:100 900}}
@font-face{{font-family:Inter;src:url('file://{FONTES}/Inter.ttf');font-weight:100 900}}
html,body{{margin:0;background:transparent}}
.chip{{display:inline-flex;align-items:center;gap:14px;padding:14px 26px;border-radius:999px;background:{VERDE};color:#fff;
 font-family:Archivo;font-weight:700;font-size:30px;letter-spacing:0.12em;text-transform:uppercase}}
.chip i{{width:12px;height:12px;border-radius:50%;background:#fff;display:block}}
.t{{font-family:Archivo;font-weight:800;letter-spacing:-0.02em;color:#fff;text-shadow:0 4px 28px rgba(0,0,0,.45)}}
.t em,.x em{{font-style:normal;color:{CLARO}}}
.x{{font-family:Inter;color:#DCEBE0}}
"""
ICONES = {
 "agua": '<path d="M12 3s-6 7-6 11a6 6 0 0 0 12 0c0-4-6-11-6-11z"/>',
 "ete": '<path d="M4 10h16M6 10v8a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2v-8M9 6l3-3 3 3M12 3v9"/>',
 "equipe": '<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.4"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6M15 14.5c3 0 6 1.8 6 5.5"/>',
 "tempo": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 "seguro": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
 "vapor": '<path d="M7 20c-2-3 2-5 0-8s2-5 0-8M12 20c-2-3 2-5 0-8s2-5 0-8M17 20c-2-3 2-5 0-8s2-5 0-8"/>',
}

def pagina(corpo, w, h, fundo="transparent"):
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS}
.wrap{{width:{w}px;height:{h}px;position:relative;overflow:hidden;background:{fundo};font-family:Inter;color:#fff}}</style></head>
<body><div class="wrap">{corpo}</div></body></html>"""

def lista_html(itens, tam=56):
    out = []
    for ic, a, b in itens:
        out.append(f"""<div style="display:flex;gap:30px;align-items:center;padding:30px 0;border-top:2px solid rgba(255,255,255,.14)">
<div style="flex:none;width:108px;height:108px;border-radius:28px;background:rgba(91,234,133,.16);display:flex;align-items:center;justify-content:center">
<svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="{CLARO}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONES.get(ic, ICONES['vapor'])}</svg></div>
<div><div class="t" style="font-size:{tam}px;line-height:1.05;text-shadow:none">{a}</div>
<div class="x" style="font-size:32px;margin-top:8px">{b}</div></div></div>""")
    return "".join(out)

def tela_final(w, h, kicker, titulo):
    logo = 720 if h > 1500 else 600
    return pagina(f"""<div style="position:absolute;inset:0;background:radial-gradient(ellipse at 50% 36%, #0f3a1b 0%, {FUNDO} 62%);
display:flex;flex-direction:column;align-items:center;justify-content:center;gap:40px">
<div style="width:{logo}px;height:{logo}px;background:url('file://{LOGO}') center/cover;-webkit-mask-image:radial-gradient(ellipse 50% 50% at 50% 50%, #000 80%, transparent 100%)"></div>
<div style="display:flex;flex-direction:column;align-items:center;gap:22px;margin-top:-70px">
<span class="chip"><i></i>{kicker}</span>
<div class="t" style="font-size:72px;line-height:1.05;text-align:center;max-width:900px">{titulo}</div></div>
<div style="padding:28px 56px;border-radius:999px;background:#fff;color:#0B3B1A;font-family:Archivo;font-weight:800;font-size:42px">Fale com a AllCleantech</div>
<div class="x" style="font-size:30px;font-weight:600">Link na bio · @allcleantech</div></div>""", w, h, FUNDO)

def foto_url(p):
    return f"file://{(RAIZ / p).resolve()}"

# ---------- carrossel ----------
def carrossel(r, saida, pg):
    slides = r["slides"]; n = len(slides) + 1
    for i, s in enumerate(slides, 1):
        img = s.get("imagem")
        fundo = (f"<div style=\"position:absolute;inset:0;background:url('{foto_url(img)}') center/cover\"></div>"
                 f"<div style=\"position:absolute;inset:0;background:linear-gradient(180deg,rgba(6,22,9,.35) 0%,rgba(6,22,9,.55) 45%,rgba(6,22,9,.95) 100%)\"></div>") if img else \
                f"<div style=\"position:absolute;inset:0;background:radial-gradient(ellipse at 80% 0%, #0f3a1b 0%, {FUNDO} 60%)\"></div>"
        lista = lista_html(s["lista"], 50) if s.get("lista") else ""
        tam = s.get("tamanho", 96 if i == 1 else 84)
        corpo = f"""{fundo}
<div style="position:absolute;inset:0;padding:84px;box-sizing:border-box;display:flex;flex-direction:column;justify-content:space-between">
<div style="display:flex;justify-content:space-between;font-size:26px;font-weight:600;color:#BFD9C6"><span>@allcleantech</span><span>{i:02d} / {n:02d}</span></div>
<div style="display:flex;flex-direction:column;gap:30px">
<span class="chip" style="align-self:flex-start"><i></i>{s.get('kicker','')}</span>
<div class="t" style="font-size:{tam}px;line-height:1.03">{s['titulo']}</div>
{f'<div class="x" style="font-size:38px;line-height:1.4">{s["texto"]}</div>' if s.get('texto') else ''}
{f'<div>{lista}</div>' if lista else ''}
</div>
<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:24px;font-size:22px;color:#A9C4B0">
<span>{s.get('fonte','')}</span>{'<span style="font-family:Archivo;font-weight:700;font-size:28px;color:'+CLARO+'">Arraste →</span>' if i == 1 else ''}</div></div>"""
        render(pg, pagina(corpo, 1080, 1350, FUNDO), saida / f"tela-{i:02d}.png", 1080, 1350)
    cta = r.get("cta", {"kicker": "AllCleantech", "titulo": "Limpeza a vapor<br><em>com o mínimo de água.</em>"})
    render(pg, tela_final(1080, 1350, cta["kicker"], cta["titulo"]), saida / f"tela-{n:02d}.png", 1080, 1350)
    print(f"{n} telas em {saida}")

# ---------- reel ----------
VF = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,unsharp=5:5:0.5,eq=contrast=1.06:saturation=1.12,fps=30,format=yuv420p,setsar=1"

def sobreposicao(c):
    if c.get("lista"):
        return f"""<div style="position:absolute;inset:0;background:rgba(4,16,7,.72)"></div>
<div style="position:absolute;left:72px;right:72px;top:330px"><span class="chip"><i></i>{c.get('kicker','')}</span>
<div class="t" style="font-size:70px;line-height:1.04;margin:26px 0 30px">{c.get('titulo','')}</div>{lista_html(c['lista'])}</div>"""
    return f"""<div style="position:absolute;left:0;right:0;top:0;height:900px;background:linear-gradient(180deg,rgba(4,16,7,.82) 0%,rgba(4,16,7,.55) 55%,rgba(4,16,7,0) 100%)"></div>
<div style="position:absolute;left:72px;right:72px;top:290px"><span class="chip"><i></i>{c.get('kicker','')}</span>
<div class="t" style="font-size:84px;line-height:1.02;margin-top:26px">{c.get('titulo','')}</div></div>"""

def sh(cmd):
    subprocess.run(cmd, check=True)

def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]).decode().strip())

def reel(r, saida, pg, tmp):
    segs = []
    for i, c in enumerate(r["cenas"], 1):
        ov = tmp / f"ov{i}.png"; render(pg, pagina(sobreposicao(c), 1080, 1920), ov, 1080, 1920, transparente=True)
        src = RAIZ / c["arquivo"]; d = float(c.get("duracao", 3.5))
        pre = ""
        if c.get("recorte"):
            x, y, w, h = c["recorte"]; pre = f"crop=iw*{w}:ih*{h}:iw*{x}:ih*{y},"
        extra = ",boxblur=18:2" if c.get("desfoque") else ""
        seg = tmp / f"s{i}.mp4"
        if src.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            entrada = ["-loop", "1", "-t", str(d), "-i", str(src)]
            base = f"[0:v]{pre}scale=1300:-2,zoompan=z='min(1+0.0009*on,1.1)':d=1:s=1080x1920:fps=30,{VF}{extra}[v]"
        else:
            entrada = ["-ss", str(c.get("inicio", 0)), "-t", str(d), "-i", str(src)]
            base = f"[0:v]{pre}{VF}{extra}[v]"
        sh(["ffmpeg", "-v", "error", "-y", *entrada, "-loop", "1", "-t", str(d), "-i", str(ov), "-filter_complex",
            base + ";[1:v]format=rgba,fade=t=in:st=0.15:d=0.4:alpha=1[o];[v][o]overlay=x=0:y='max(0,70-70*(t-0.15)/0.45)':eval=frame:shortest=1,format=yuv420p[out]",
            "-map", "[out]", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", "30", str(seg)])
        segs.append(seg)
    fim = tmp / "fim.png"; cta = r.get("cta", {"kicker": "AllCleantech", "titulo": "Limpeza a vapor<br><em>com o mínimo de água.</em>"})
    render(pg, tela_final(1080, 1920, cta["kicker"], cta["titulo"]), fim, 1080, 1920)
    sf = tmp / "sfim.mp4"
    sh(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", "4", "-i", str(fim), "-vf", "zoompan=z='min(1+0.0007*on,1.06)':d=1:s=1080x1920:fps=30,format=yuv420p",
        "-c:v", "libx264", "-crf", "18", "-r", "30", str(sf)])
    segs.append(sf)
    X = 0.3; ins = []; fc = []; off = 0.0; prev = "[0]"
    for s in segs: ins += ["-i", str(s)]
    for i in range(1, len(segs)):
        off += dur(segs[i - 1]) - X if i == 1 else dur(segs[i - 1]) - X
        lab = f"[x{i}]"
        trans = "slideleft" if i < len(segs) - 1 else "fade"
        fc.append(f"{prev}[{i}]xfade=transition={trans}:duration={X}:offset={off:.3f}{lab}")
        prev = lab
    total = off + dur(segs[-1])
    fc.append(f"{prev}drawbox=x=0:y=0:w=iw:h=10:color=black@0.35:t=fill,drawbox=x=0:y=0:w='iw*t/{total:.3f}':h=10:color=0x5BEA85:t=fill,format=yuv420p[v]")
    out = saida / "reel.mp4"
    sh(["ffmpeg", "-v", "error", "-y", *ins, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-filter_complex", ";".join(fc),
        "-map", "[v]", "-map", f"{len(segs)}:a", "-shortest", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-profile:v", "high",
        "-level", "4.1", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)])
    sh(["ffmpeg", "-v", "error", "-y", "-ss", "1.2", "-i", str(out), "-frames:v", "1", "-q:v", "2", str(saida / "capa.jpg")])
    print(f"Reel {total:.1f}s em {out}")

def render(pg, html, destino, w, h, transparente=False):
    tmp = destino.with_suffix(".html"); tmp.write_text(html)
    pg.set_viewport_size({"width": w, "height": h}); pg.goto(f"file://{tmp}"); pg.wait_for_timeout(450)
    pg.screenshot(path=str(destino), omit_background=transparente); tmp.unlink()

if __name__ == "__main__":
    r = json.loads(pathlib.Path(sys.argv[1]).read_text())
    saida = RAIZ / r["pasta"]; saida.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p, tempfile.TemporaryDirectory() as td:
        b = p.chromium.launch(); pg = b.new_page()
        if r["tipo"] == "carrossel": carrossel(r, saida, pg)
        else: reel(r, saida, pg, pathlib.Path(td))
        b.close()

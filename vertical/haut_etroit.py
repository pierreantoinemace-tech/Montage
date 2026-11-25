"""Perso d'origine (pfp_dark.dreamer) avec un haut plus étroit : on retire les deux parties extérieures du vêtement."""
import inspect


def appliquer(pd):
    src = inspect.getsource(pd.dreamer)
    rep = [("p.moveTo(cx - 1.6 * s, S + 50); p.cubicTo(cx - 1.4 * s, cy + 1.4 * s, cx - 0.5 * s, cy + 1.25 * s, cx, cy + 1.25 * s)",
            "p.moveTo(cx - 0.8 * s, S + 50); p.cubicTo(cx - 0.75 * s, cy + 1.45 * s, cx - 0.35 * s, cy + 1.25 * s, cx, cy + 1.25 * s)"),
           ("p.cubicTo(cx + 0.5 * s, cy + 1.25 * s, cx + 1.4 * s, cy + 1.4 * s, cx + 1.6 * s, S + 50); p.close()",
            "p.cubicTo(cx + 0.35 * s, cy + 1.25 * s, cx + 0.75 * s, cy + 1.45 * s, cx + 0.8 * s, S + 50); p.close()"),
           ("for k in range(5):\n        cv.drawLine(cx - 1.2 * s + k * 0.6 * s, cy + 1.3 * s, cx - 1.5 * s + k * 0.75 * s, S + 50,",
            "for k in range(3):\n        cv.drawLine(cx - 0.4 * s + k * 0.4 * s, cy + 1.35 * s, cx - 0.5 * s + k * 0.5 * s, S + 50,")]
    for a, b in rep:
        assert a in src, a[:60]
        src = src.replace(a, b)
    exec(src, pd.__dict__)
    src = inspect.getsource(pd.draw_arms)
    for a, b in [("sh = [(cx - 0.72 * s, cy + 1.5 * s), (cx + 0.72 * s, cy + 1.5 * s)]", "sh = [(cx - 0.5 * s, cy + 1.5 * s), (cx + 0.5 * s, cy + 1.5 * s)]"),
                 ("idle = [(cx - 1.05 * s, cy + 2.6 * s + 0.05 * s * sw), (cx + 1.05 * s, cy + 2.6 * s - 0.05 * s * sw)]",
                  "idle = [(cx - 0.8 * s, cy + 2.6 * s + 0.05 * s * sw), (cx + 0.8 * s, cy + 2.6 * s - 0.05 * s * sw)]")]:
        assert a in src, a[:60]
        src = src.replace(a, b)
    exec(src, pd.__dict__)

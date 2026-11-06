import json, math, os, queue, socket, threading, time

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

BG = (0.04, 0.04, 0.07, 1)
NEON = (0.2, 1.0, 0.9, 1)
PINK = (1.0, 0.2, 0.8, 1)

# ---------------- ДЕЙСТВИЯ (больше 100) ----------------
HOTKEYS = [
    ("Копировать", "ctrl+c"), ("Вставить", "ctrl+v"), ("Вырезать", "ctrl+x"),
    ("Отменить", "ctrl+z"), ("Повторить", "ctrl+y"), ("Выделить всё", "ctrl+a"),
    ("Сохранить", "ctrl+s"), ("Сохранить как", "ctrl+shift+s"), ("Открыть файл", "ctrl+o"),
    ("Закрыть вкладку", "ctrl+w"), ("Новая вкладка", "ctrl+t"), ("Открыть вкладку назад", "ctrl+shift+t"),
    ("Новое окно", "ctrl+n"), ("Инкогнито", "ctrl+shift+n"), ("Поиск на странице", "ctrl+f"),
    ("Печать", "ctrl+p"), ("Закрыть окно", "alt+f4"), ("Переключить окна", "alt+tab"),
    ("Рабочий стол (Win+D)", "win+d"), ("Проводник", "win+e"), ("Заблокировать ПК", "win+l"),
    ("Выполнить (Win+R)", "win+r"), ("Задачи (Win+Tab)", "win+tab"), ("Свернуть всё", "win+m"),
    ("Развернуть всё", "win+shift+m"), ("Окно вверх", "win+up"), ("Окно вниз", "win+down"),
    ("Окно влево", "win+left"), ("Окно вправо", "win+right"), ("Диспетчер задач", "ctrl+shift+esc"),
    ("Скриншот области", "win+shift+s"), ("Скриншот в буфер", "printscreen"), ("Буфер обмена (Win+V)", "win+v"),
    ("Поиск Windows", "win+s"), ("Настройки (Win+I)", "win+i"), ("Эмодзи (Win+.)", "win+period"),
    ("Адресная строка", "ctrl+l"), ("История", "ctrl+h"), ("Закладки", "ctrl+d"),
    ("Обновить", "f5"), ("Полный экран", "f11"), ("Назад", "alt+left"), ("Вперёд", "alt+right"),
    ("Увеличить", "ctrl+equal"), ("Уменьшить", "ctrl+minus"), ("Сброс масштаба", "ctrl+0"),
    ("Слово влево", "ctrl+left"), ("Слово вправо", "ctrl+right"), ("Удалить слово", "ctrl+backspace"),
    ("Жирный", "ctrl+b"), ("Курсив", "ctrl+i"), ("Подчёркивание", "ctrl+u"),
    ("В начало документа", "ctrl+home"), ("В конец документа", "ctrl+end"),
    ("Enter", "enter"), ("Esc", "esc"), ("Tab", "tab"), ("Backspace", "backspace"),
    ("Delete", "delete"), ("Home", "home"), ("End", "end"), ("Page Up", "pageup"),
    ("Page Down", "pagedown"), ("Стрелка вверх", "up"), ("Стрелка вниз", "down"),
    ("Стрелка влево", "left"), ("Стрелка вправо", "right"),
    ("Громкость +", "volumeup"), ("Громкость -", "volumedown"), ("Без звука", "volumemute"),
    ("Play/Pause", "playpause"), ("Следующий трек", "nexttrack"), ("Предыдущий трек", "prevtrack"),
] + [(f"F{i}", f"f{i}") for i in range(1, 13)]

APPS = [
    ("Блокнот", "notepad"), ("Калькулятор", "calc"), ("Paint", "mspaint"),
    ("Командная строка", "cmd"), ("PowerShell", "powershell"), ("Панель управления", "control"),
    ("Параметры Windows", "ms-settings:"), ("Загрузки", "shell:Downloads"),
    ("Корзина", "shell:RecycleBinFolder"), ("Документы", "shell:Personal"),
]

URLS = [
    ("Google", "https://www.google.com"), ("YouTube", "https://www.youtube.com"),
    ("Gmail", "https://mail.google.com"), ("Google Диск", "https://drive.google.com"),
    ("Google Карты", "https://maps.google.com"), ("GitHub", "https://github.com"),
    ("Telegram Web", "https://web.telegram.org"), ("ChatGPT", "https://chatgpt.com"),
    ("Claude", "https://claude.ai"), ("Wikipedia", "https://www.wikipedia.org"),
]

CLICKS = [
    ("ЛКМ", {"t": "click", "btn": "left", "count": 1}),
    ("Двойной ЛКМ", {"t": "click", "btn": "left", "count": 2}),
    ("ПКМ", {"t": "click", "btn": "right", "count": 1}),
    ("Средняя кнопка", {"t": "click", "btn": "middle", "count": 1}),
]

ACTIONS = {}
for _label, _keys in HOTKEYS:
    ACTIONS[_label] = {"t": "hotkey", "keys": _keys}
for _label, _cmd in APPS:
    ACTIONS[_label] = {"t": "app", "cmd": _cmd}
for _label, _url in URLS:
    ACTIONS[_label] = {"t": "url", "url": _url}
for _label, _payload in CLICKS:
    ACTIONS[_label] = _payload

DEFAULT_TOUCH = {
    "1": "ЛКМ", "dbl": "Двойной ЛКМ", "2": "ПКМ", "3": "Средняя кнопка",
    "4": "Рабочий стол (Win+D)", "5": "Задачи (Win+Tab)",
    "3L": "Назад", "3R": "Вперёд", "3U": "Задачи (Win+Tab)", "3D": "Рабочий стол (Win+D)",
    "4L": "Переключить окна", "4R": "Переключить окна", "4U": "Развернуть всё", "4D": "Свернуть всё",
}
TOUCH_KEYS = [
    ("1", "1 палец: тап"), ("dbl", "1 палец: двойной тап"), ("2", "2 пальца: тап"),
    ("3", "3 пальца: тап"), ("4", "4 пальца: тап"), ("5", "5 пальцев: тап"),
    ("3L", "3 пальца: свайп влево"), ("3R", "3 пальца: свайп вправо"),
    ("3U", "3 пальца: свайп вверх"), ("3D", "3 пальца: свайп вниз"),
    ("4L", "4 пальца: свайп влево"), ("4R", "4 пальца: свайп вправо"),
    ("4U", "4 пальца: свайп вверх"), ("4D", "4 пальца: свайп вниз"),
]
DEFAULT_CFG = {"ip": "192.168.0.", "port": 5151, "sens": 1.6, "touch": DEFAULT_TOUCH}

HELP = """ТАЧПАД
• 1 палец: движение курсора
• 1 палец: тап = ЛКМ, двойной тап = двойной клик
• 2 пальца: прокрутка вверх/вниз
• 2 пальца: тап = ПКМ
• 3 пальца: тап = средняя кнопка
• 4 пальца: тап = рабочий стол
• 5 пальцев: тап = задачи
• 3 или 4 пальца: свайп в любую сторону (см. вкладку «Команды»)

Все назначения меняются во вкладке «Команды».

ЖЕСТЫ
Нарисуй фигуру (круг, квадрат, галочку, букву). Приложение распознает её и выполнит привязанное действие. Жесты сохраняются на телефоне.

КЛАВИАТУРА
Вкладка «Клавиатура»: текст, который ты пишешь, сразу печатается на ПК.
"""

DATA_DIR = None
CFG = {}
GESTURES = []


def store_path(name):
    return os.path.join(DATA_DIR, name)


def load_json(name, default):
    try:
        with open(store_path(name), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(name, data):
    try:
        with open(store_path(name), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass


def autolabel(text, **kw):
    lbl = Label(text=text, halign="left", valign="top", size_hint_y=None, **kw)
    lbl.bind(width=lambda i, w: setattr(i, "text_size", (w, None)),
             texture_size=lambda i, s: setattr(i, "height", s[1]))
    return lbl


def wrap(text, **kw):
    lbl = Label(text=text, halign="left", valign="middle", **kw)
    lbl.bind(width=lambda i, w: setattr(i, "text_size", (w, None)))
    return lbl


# ---------------- СЕТЬ ----------------
class Link:
    def __init__(self):
        self.sock = None
        self.q = queue.Queue()
        self.on_status = lambda text: None
        threading.Thread(target=self._sender, daemon=True).start()

    @property
    def connected(self):
        return self.sock is not None

    def _ui(self, text):
        Clock.schedule_once(lambda dt: self.on_status(text))

    def connect(self, host, port):
        self.disconnect(silent=True)

        def run():
            try:
                s = socket.create_connection((host, port), timeout=5)
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                s.settimeout(None)
                self.sock = s
                self._ui(f"Подключено: {host}:{port}")
            except Exception as e:
                self._ui(f"Ошибка подключения: {e}")

        threading.Thread(target=run, daemon=True).start()

    def disconnect(self, silent=False):
        if self.sock:
            try:
                self.sock.close()
            except OSError:
                pass
        self.sock = None
        if not silent:
            self._ui("Отключено")

    def send(self, msg):
        self.q.put(msg)

    def _sender(self):
        while True:
            msg = self.q.get()
            s = self.sock
            if s is None:
                continue
            try:
                s.sendall((json.dumps(msg) + "\n").encode("utf-8"))
            except OSError:
                self.sock = None
                self._ui("Связь потеряна")


LINK = Link()


def fire_label(label):
    if label in ACTIONS:
        LINK.send(ACTIONS[label])


# ---------------- ТАЧПАД ----------------
class TouchPad(Widget):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.touches = {}
        self.last_tap_pending = None
        self.reset()
        self.bind(pos=self.redraw, size=self.redraw)

    def reset(self):
        self.t0 = 0
        self.moved = 0
        self.maxf = 0
        self.sx = self.sy = 0
        self.ax = self.ay = 0
        self.acc_scroll = 0

    def redraw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*BG)
            Rectangle(pos=self.pos, size=self.size)
            Color(0.2, 1.0, 0.9, 0.35)
            Line(rectangle=(self.x + 4, self.y + 4, self.width - 8, self.height - 8), width=dp(2))

    def draw_dots(self):
        self.canvas.after.clear()
        with self.canvas.after:
            for x, y in self.touches.values():
                Color(0.2, 1.0, 0.9, 0.25)
                Ellipse(pos=(x - dp(45), y - dp(45)), size=(dp(90), dp(90)))
                Color(*PINK)
                Ellipse(pos=(x - dp(10), y - dp(10)), size=(dp(20), dp(20)))

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        touch.grab(self)
        if not self.touches:
            self.reset()
            self.t0 = time.time()
        self.touches[touch.uid] = touch.pos
        self.maxf = max(self.maxf, len(self.touches))
        self.draw_dots()
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return False
        old = self.touches.get(touch.uid, touch.pos)
        self.touches[touch.uid] = touch.pos
        dx = touch.x - old[0]
        dy = touch.y - old[1]
        n = len(self.touches)
        self.moved += abs(dx) + abs(dy)
        sens = CFG.get("sens", 1.6)
        if n == 1:
            self.ax += dx * sens
            self.ay += -dy * sens
            ix, iy = int(self.ax), int(self.ay)
            if ix or iy:
                LINK.send({"t": "move", "dx": ix, "dy": iy})
                self.ax -= ix
                self.ay -= iy
        elif n == 2:
            self.acc_scroll += dy
            steps = int(self.acc_scroll / dp(12))
            if steps:
                LINK.send({"t": "scroll", "dy": steps})
                self.acc_scroll -= steps * dp(12)
        else:
            self.sx += dx / n
            self.sy += dy / n
        self.draw_dots()
        return True

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return False
        touch.ungrab(self)
        self.touches.pop(touch.uid, None)
        if not self.touches:
            self.finish()
        self.draw_dots()
        return True

    def fire(self, key):
        label = CFG["touch"].get(key)
        if label:
            fire_label(label)

    def _single(self, dt):
        self.last_tap_pending = None
        self.fire("1")

    def finish(self):
        dur = time.time() - self.t0
        f = self.maxf
        if f >= 3 and max(abs(self.sx), abs(self.sy)) > dp(60):
            if abs(self.sx) > abs(self.sy):
                key = f"{f}{'R' if self.sx > 0 else 'L'}"
            else:
                key = f"{f}{'U' if self.sy > 0 else 'D'}"
            self.fire(key)
            return
        if self.moved < dp(25) and dur < 0.4:
            if f == 1:
                if self.last_tap_pending:
                    self.last_tap_pending.cancel()
                    self.last_tap_pending = None
                    self.fire("dbl")
                else:
                    self.last_tap_pending = Clock.schedule_once(self._single, 0.3)
            else:
                self.fire(str(f))


# ---------------- РАСПОЗНАВАНИЕ ЖЕСТОВ ($1-подобный алгоритм) ----------------
def path_len(pts):
    return sum(math.dist(pts[i - 1], pts[i]) for i in range(1, len(pts)))


def resample(pts, n=64):
    pts = [tuple(p) for p in pts]
    interval = path_len(pts) / (n - 1)
    if interval == 0:
        return [pts[0]] * n
    dist_acc = 0.0
    new = [pts[0]]
    i = 1
    while i < len(pts):
        d = math.dist(pts[i - 1], pts[i])
        if dist_acc + d >= interval:
            t = (interval - dist_acc) / d
            q = (pts[i - 1][0] + t * (pts[i][0] - pts[i - 1][0]),
                 pts[i - 1][1] + t * (pts[i][1] - pts[i - 1][1]))
            new.append(q)
            pts.insert(i, q)
            dist_acc = 0.0
        else:
            dist_acc += d
        i += 1
    while len(new) < n:
        new.append(pts[-1])
    return new[:n]


def normalize(pts):
    pts = resample(pts)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    s = max(max(xs) - min(xs), max(ys) - min(ys), 1e-6)
    pts = [((x - min(xs)) / s, (y - min(ys)) / s) for x, y in pts]
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    return [(x - cx, y - cy) for x, y in pts]


def rotate(pts, a):
    c, s = math.cos(a), math.sin(a)
    return [(x * c - y * s, x * s + y * c) for x, y in pts]


def avg_dist(a, b):
    return sum(math.dist(p, q) for p, q in zip(a, b)) / len(a)


def recognize(pts, templates):
    cand = normalize(pts)
    best_name, best = None, 1e9
    for name, tpl in templates:
        for deg in range(0, 360, 6):
            d = avg_dist(rotate(cand, math.radians(deg)), tpl)
            if d < best:
                best_name, best = name, d
    if best < 0.25:
        return best_name, best
    return None, best


class DrawPad(Widget):
    def __init__(self, on_stroke, **kw):
        super().__init__(**kw)
        self.on_stroke = on_stroke
        self.stroke = []
        self._drawing = False
        self.bind(pos=self.redraw, size=self.redraw)

    def redraw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*BG)
            Rectangle(pos=self.pos, size=self.size)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        if self._drawing:
            return True
        self._drawing = True
        touch.grab(self)
        self.stroke = [tuple(touch.pos)]
        self.canvas.after.clear()
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return False
        self.stroke.append(tuple(touch.pos))
        self.canvas.after.clear()
        with self.canvas.after:
            Color(*NEON)
            Line(points=[c for p in self.stroke for c in p], width=dp(3))
        return True

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return False
        touch.ungrab(self)
        self._drawing = False
        if len(self.stroke) >= 8:
            self.on_stroke(list(self.stroke))
        return True


class GestureTab(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", spacing=dp(6), padding=dp(6), **kw)
        self.last_points = None
        self.info = wrap("Нарисуй фигуру: приложение распознает её и выполнит действие",
                         size_hint_y=None, height=dp(44))
        self.pad = DrawPad(self.on_stroke, size_hint_y=0.4)
        self.name_in = TextInput(hint_text="Название жеста, например: Круг",
                                 multiline=False, size_hint_y=None, height=dp(44))
        self.action_sp = Spinner(text="ЛКМ", values=list(ACTIONS.keys()),
                                 size_hint_y=None, height=dp(44))
        save_btn = Button(text="Сохранить последний рисунок", size_hint_y=None, height=dp(44),
                          on_release=self.save_last)
        self.del_sp = Spinner(text="Выбери жест для удаления", values=[],
                              size_hint_y=None, height=dp(44))
        del_btn = Button(text="Удалить выбранный", size_hint_y=None, height=dp(44),
                         on_release=self.delete_gesture)
        self.list_lbl = autolabel("", size_hint_y=None)
        scroll = ScrollView()
        scroll.add_widget(self.list_lbl)
        self.list_lbl.size_hint_y = None

        for w in (self.info, self.pad, self.name_in, self.action_sp, save_btn,
                  self.del_sp, del_btn):
            self.add_widget(w)
        self.add_widget(scroll)
        self.refresh()

    def refresh(self):
        self.del_sp.values = [g["name"] for g in GESTURES]
        text = "\n".join(f"• {g['name']} → {g['action']}" for g in GESTURES)
        self.list_lbl.text = text or "Сохранённых жестов пока нет"

    def on_stroke(self, pts):
        self.last_points = pts
        if not GESTURES:
            self.info.text = "Жестов нет. Нарисуй фигуру, введи название и сохрани."
            return
        templates = [(g["name"], normalize(g["points"])) for g in GESTURES]
        name, score = recognize(pts, templates)
        if name is None:
            self.info.text = f"Не распознано (похожесть {score:.2f})"
            return
        g = next(g for g in GESTURES if g["name"] == name)
        self.info.text = f"{name} → {g['action']}"
        fire_label(g["action"])

    def save_last(self, *a):
        name = self.name_in.text.strip()
        if not name or not self.last_points:
            self.info.text = "Нарисуй фигуру и введи название"
            return
        GESTURES[:] = [g for g in GESTURES if g["name"] != name]
        GESTURES.append({"name": name, "points": self.last_points, "action": self.action_sp.text})
        save_json("gestures.json", GESTURES)
        self.info.text = f"Жест «{name}» сохранён"
        self.refresh()

    def delete_gesture(self, *a):
        name = self.del_sp.text
        GESTURES[:] = [g for g in GESTURES if g["name"] != name]
        save_json("gestures.json", GESTURES)
        self.refresh()


# ---------------- КЛАВИАТУРА ----------------
class KeyboardTab(BoxLayout):
    SENT = "\u200b"

    def __init__(self, **kw):
        super().__init__(orientation="vertical", spacing=dp(6), padding=dp(6), **kw)
        self._busy = False
        self.inp = TextInput(text=self.SENT, multiline=True,
                             hint_text="Пиши здесь, текст сразу печатается на ПК",
                             size_hint_y=0.45)
        self.inp.bind(text=self.on_text)
        self.add_widget(self.inp)

        quick = [("Enter", "enter"), ("Esc", "esc"), ("Tab", "tab"), ("⌫", "backspace"),
                 ("Del", "delete"), ("←", "left"), ("→", "right"), ("↑", "up"), ("↓", "down")]
        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(4))
        for label, key in quick:
            row.add_widget(Button(text=label,
                                  on_release=lambda b, k=key: LINK.send({"t": "hotkey", "keys": k})))
        self.add_widget(row)

        row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(4))
        for label, keys in [("Копировать", "ctrl+c"), ("Вставить", "ctrl+v"),
                            ("Отменить", "ctrl+z"), ("Выделить всё", "ctrl+a")]:
            row2.add_widget(Button(text=label,
                                   on_release=lambda b, k=keys: LINK.send({"t": "hotkey", "keys": k})))
        self.add_widget(row2)

    def on_text(self, inst, value):
        if self._busy or value == self.SENT:
            return
        self._busy = True
        try:
            if len(value) < len(self.SENT) or value == "":
                LINK.send({"t": "hotkey", "keys": "backspace"})
            else:
                parts = value.replace(self.SENT, "").split("\n")
                for i, part in enumerate(parts):
                    if i > 0:
                        LINK.send({"t": "hotkey", "keys": "enter"})
                    if part:
                        LINK.send({"t": "text", "text": part})
            inst.text = self.SENT
            inst.cursor = (1, 0)
        finally:
            self._busy = False


# ---------------- КОМАНДЫ (назначение действий) ----------------
class CommandsTab(ScrollView):
    def __init__(self, **kw):
        super().__init__(**kw)
        box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6), padding=dp(8))
        box.bind(minimum_height=box.setter("height"))
        box.add_widget(autolabel(HELP))
        box.add_widget(wrap("НАЗНАЧЕНИЕ ЖЕСТОВ ТАЧПАДА", size_hint_y=None, height=dp(36)))
        for key, title in TOUCH_KEYS:
            row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
            row.add_widget(wrap(title, size_hint_x=0.42))
            sp = Spinner(text=CFG["touch"].get(key, ""), values=list(ACTIONS.keys()), size_hint_x=0.58)
            sp.bind(text=lambda i, v, k=key: self.set_touch(k, v))
            row.add_widget(sp)
            box.add_widget(row)
        self.add_widget(box)

    def set_touch(self, key, value):
        CFG["touch"][key] = value
        save_json("config.json", CFG)


# ---------------- СВЯЗЬ ----------------
class ConnectTab(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", padding=dp(12), spacing=dp(8), **kw)
        self.ip = TextInput(text=CFG["ip"], hint_text="IP ПК, например 192.168.1.20",
                            multiline=False, size_hint_y=None, height=dp(48))
        self.port = TextInput(text=str(CFG["port"]), multiline=False, input_filter="int",
                              size_hint_y=None, height=dp(48))
        self.status = wrap("Не подключено", size_hint_y=None, height=dp(40))
        LINK.on_status = self.set_status

        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        row.add_widget(Button(text="Подключиться", on_release=self.do_connect))
        row.add_widget(Button(text="Отключиться", on_release=lambda *a: LINK.disconnect()))

        self.sens = Slider(min=0.5, max=4, value=CFG["sens"], size_hint_y=None, height=dp(40))
        self.sens.bind(value=self.on_sens)

        for w in (self.ip, self.port, row,
                  wrap("Чувствительность курсора", size_hint_y=None, height=dp(30)),
                  self.sens, self.status,
                  autolabel(
                      "КАК ПОДКЛЮЧИТЬ\n"
                      "1. Запусти pc_server.py на ноутбуке/ПК.\n"
                      "2. Телефон и ПК в одной сети, либо телефон раздаёт интернет по Bluetooth / Wi-Fi.\n"
                      "3. Введи IP ПК и нажми «Подключиться».\n"
                      "4. Порт 5151 должен быть открыт в брандмауэре Windows."),
                  ):
            self.add_widget(w)

    def set_status(self, text):
        self.status.text = text

    def on_sens(self, inst, value):
        CFG["sens"] = round(value, 2)
        save_json("config.json", CFG)

    def do_connect(self, *a):
        try:
            CFG["ip"] = self.ip.text.strip()
            CFG["port"] = int(self.port.text or 5151)
        except ValueError:
            self.set_status("Порт должен быть числом")
            return
        save_json("config.json", CFG)
        self.set_status("Подключение...")
        LINK.connect(CFG["ip"], CFG["port"])


# ---------------- ПРИЛОЖЕНИЕ ----------------
class PlaDeckApp(App):
    def build(self):
        global DATA_DIR, CFG, GESTURES
        DATA_DIR = self.user_data_dir
        CFG = load_json("config.json", None) or {}
        for k, v in DEFAULT_CFG.items():
            if k == "touch":
                CFG.setdefault("touch", {})
                for tk, tv in DEFAULT_TOUCH.items():
                    CFG["touch"].setdefault(tk, tv)
            else:
                CFG.setdefault(k, v)
        GESTURES = load_json("gestures.json", [])

        Window.clearcolor = BG

        self.gesture_tab = GestureTab()
        self.connect_tab = ConnectTab()
        self.touch_tab = BoxLayout(orientation="vertical")
        self.touch_tab.add_widget(wrap("Тапни и води пальцами. Подробно: вкладка «Команды»",
                                       size_hint_y=None, height=dp(30)))
        self.touch_tab.add_widget(TouchPad())

        panel = TabbedPanel(do_default_tab=False, tab_width=dp(120), tab_height=dp(44))
        for title, content in [("Связь", self.connect_tab), ("Тачпад", self.touch_tab),
                               ("Жесты", self.gesture_tab), ("Клавиатура", KeyboardTab()),
                               ("Команды", CommandsTab())]:
            item = TabbedPanelItem(text=title)
            item.add_widget(content)
            panel.add_widget(item)
        panel.default_tab = panel.tab_list[-1] if False else panel.default_tab
        return panel

    def on_stop(self):
        save_json("config.json", CFG)
        save_json("gestures.json", GESTURES)
        LINK.disconnect(silent=True)


if __name__ == "__main__":
    PlaDeckApp().run()

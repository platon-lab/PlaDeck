import json, math, os, queue, socket, threading, time

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

BG = (0.04, 0.04, 0.07, 1)
CARD = (0.10, 0.10, 0.17, 1)
ACCENT = (0.0, 0.55, 0.5, 1)
NEON = (0.2, 1.0, 0.9, 1)
PINK = (1.0, 0.2, 0.8, 1)
TEXT = (0.92, 0.96, 1, 1)
RED = (0.6, 0.12, 0.2, 1)
TOUCH_CFG_VERSION = 2


def btn(text, cb=None, color=CARD, **kw):
    b = Button(text=text, background_normal="", background_color=color,
               color=TEXT, font_size=dp(15), **kw)
    if cb:
        b.bind(on_release=cb)
    return b


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
    # --- новые ---
    ("Следующая вкладка", "ctrl+tab"), ("Предыдущая вкладка", "ctrl+shift+tab"),
    ("Вкладка 1", "ctrl+1"), ("Вкладка 2", "ctrl+2"), ("Вкладка 3", "ctrl+3"),
    ("Вкладка 9 (последняя)", "ctrl+9"), ("Перенос строки", "shift+enter"),
    ("Стрелка вверх + Shift", "shift+up"), ("Стрелка вниз + Shift", "shift+down"),
    ("Выделить слово влево", "ctrl+shift+left"), ("Выделить слово вправо", "ctrl+shift+right"),
    ("Выделить до начала строки", "shift+home"), ("Выделить до конца строки", "shift+end"),
    ("Пробел", "space"), ("Shift+Tab", "shift+tab"), ("Ctrl+Enter", "ctrl+enter"),
    ("Пуск (Win)", "win"), ("Меню Пуск (Ctrl+Esc)", "ctrl+esc"), ("Alt+Пробел (меню окна)", "alt+space"),
    ("Новый виртуальный рабочий стол", "win+ctrl+d"), ("Закрыть виртуальный стол", "win+ctrl+f4"),
    ("Виртуальный стол влево", "win+ctrl+left"), ("Виртуальный стол вправо", "win+ctrl+right"),
    ("Win+X (меню Пуск)", "win+x"), ("Win+A (центр уведомлений)", "win+a"), ("Win+N (календарь)", "win+n"),
    ("Win+K (трансляция)", "win+k"), ("Win+P (проекция)", "win+p"), ("Win+Shift+влево", "win+shift+left"),
    ("Win+Shift+вправо", "win+shift+right"), ("Win+Alt+D (дата)", "win+alt+d"), ("Alt+Esc", "alt+esc"),
    ("Режим разработчика (F12)", "f12"), ("Консоль браузера", "ctrl+shift+i"), ("Жёсткое обновление", "ctrl+shift+r"),
    ("Очистить историю", "ctrl+shift+delete"), ("Загрузки в браузере", "ctrl+j"),
    ("Диспетчер браузера (Ctrl+Shift+M)", "ctrl+shift+m"), ("Закладки менеджер", "ctrl+shift+o"),
    ("Поиск по файлам (Ctrl+Shift+F)", "ctrl+shift+f"), ("Новая папка (Ctrl+Shift+N)", "ctrl+shift+n"),
    ("Ctrl+Shift+V (вставка текстом)", "ctrl+shift+v"), ("Командная палитра (Ctrl+Shift+P)", "ctrl+shift+p"),
    ("Ctrl+/ (комментарий)", "ctrl+/"), ("Ctrl+, (настройки)", "ctrl+,"),
    ("Ctrl+Shift+L", "ctrl+shift+l"), ("Ctrl+Shift+B", "ctrl+shift+b"), ("Ctrl+Shift+E", "ctrl+shift+e"),
    ("Ctrl+Shift+M", "ctrl+shift+m_"), ("Браузер: Назад (медиа)", "browserback"),
    ("Браузер: Вперёд (медиа)", "browserforward"), ("Браузер: Обновить", "browserrefresh"),
    ("Браузер: Домой", "browserhome"), ("Браузер: Поиск", "browsersearch"),
    ("Почта (клавиша)", "launchmail"), ("Стоп (клавиша)", "stop"),
    ("Печать экрана (клавиша)", "prtsc"), ("Scroll Lock", "scrolllock"), ("Pause/Break", "pause"),
    ("Insert", "insert"), ("Num Lock", "numlock"),
]
HOTKEYS = [h for h in HOTKEYS if "_" not in h[1]]  # отсекаем нерабочие заготовки
HOTKEYS += [(f"F{i}", f"f{i}") for i in range(1, 13)]

APPS = [
    ("Блокнот", "notepad"), ("Калькулятор", "calc"), ("Paint", "mspaint"),
    ("Командная строка", "cmd"), ("PowerShell", "powershell"), ("Панель управления", "control"),
    ("Параметры Windows", "ms-settings:"), ("Загрузки", "shell:Downloads"),
    ("Корзина", "shell:RecycleBinFolder"), ("Документы", "shell:Personal"),
    ("Рабочий стол (папка)", "shell:Desktop"), ("Изображения", "shell:My Pictures"),
    ("Видео", "shell:My Video"), ("Музыка", "shell:My Music"), ("Этот компьютер", "shell:MyComputerFolder"),
    ("Диспетчер задач (программа)", "taskmgr"), ("Ножницы (Снипинг)", "snippingtool"),
    ("Экранная клавиатура", "osk"), ("Лупа", "magnify"), ("Таблица символов", "charmap"),
    ("Монитор ресурсов", "resmon"), ("Сведения о системе", "msinfo32"),
    ("Службы", "services.msc"), ("Диспетчер устройств", "devmgmt.msc"), ("Редактор реестра", "regedit"),
    ("WordPad", "write"), ("Google Chrome", "chrome"), ("Microsoft Edge", "msedge"),
    ("Автозагрузка", "shell:Startup"),
]

URLS = [
    ("Google", "https://www.google.com"), ("YouTube", "https://www.youtube.com"),
    ("Gmail", "https://mail.google.com"), ("Google Диск", "https://drive.google.com"),
    ("Google Карты", "https://maps.google.com"), ("GitHub", "https://github.com"),
    ("Telegram Web", "https://web.telegram.org"), ("ChatGPT", "https://chatgpt.com"),
    ("Claude", "https://claude.ai"), ("Wikipedia", "https://www.wikipedia.org"),
    ("Google Календарь", "https://calendar.google.com"), ("Google Документы", "https://docs.google.com"),
    ("Google Таблицы", "https://sheets.google.com"), ("Google Фото", "https://photos.google.com"),
    ("Google Переводчик", "https://translate.google.com"), ("Google Meet", "https://meet.google.com"),
    ("Яндекс", "https://ya.ru"), ("ВКонтакте", "https://vk.com"), ("Twitch", "https://www.twitch.tv"),
    ("Netflix", "https://www.netflix.com"), ("Spotify", "https://open.spotify.com"),
    ("Reddit", "https://www.reddit.com"), ("X (Twitter)", "https://x.com"),
    ("Instagram", "https://www.instagram.com"), ("Steam", "https://store.steampowered.com"),
    ("Amazon", "https://www.amazon.com"), ("Pinterest", "https://www.pinterest.com"),
    ("Stack Overflow", "https://stackoverflow.com"), ("Google Новости", "https://news.google.com"),
    ("Погода (Google)", "https://www.google.com/search?q=погода"),
]

CLICKS = [
    ("ЛКМ", {"t": "click", "btn": "left", "count": 1}),
    ("Двойной ЛКМ", {"t": "click", "btn": "left", "count": 2}),
    ("ПКМ", {"t": "click", "btn": "right", "count": 1}),
    ("Средняя кнопка", {"t": "click", "btn": "middle", "count": 1}),
]

ACTIONS = {"Ничего": {"t": "none"}}
for _label, _keys in HOTKEYS:
    ACTIONS[_label] = {"t": "hotkey", "keys": _keys}
for _label, _cmd in APPS:
    ACTIONS[_label] = {"t": "app", "cmd": _cmd}
for _label, _url in URLS:
    ACTIONS[_label] = {"t": "url", "url": _url}
for _label, _payload in CLICKS:
    ACTIONS[_label] = _payload

DEFAULT_TOUCH = {
    "1": "ЛКМ", "dbl": "Двойной ЛКМ", "2": "Ничего", "2h": "ПКМ", "3": "Средняя кнопка",
    "4": "Рабочий стол (Win+D)", "5": "Задачи (Win+Tab)",
    "3L": "Назад", "3R": "Вперёд", "3U": "Задачи (Win+Tab)", "3D": "Рабочий стол (Win+D)",
    "4L": "Переключить окна", "4R": "Переключить окна", "4U": "Развернуть всё", "4D": "Свернуть всё",
}
TOUCH_KEYS = [
    ("1", "1 палец: тап"), ("dbl", "1 палец: двойной тап"),
    ("2", "2 пальца: быстрый тап"), ("2h", "2 пальца: удержание (0.5 с) = ПКМ"),
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
• 2 пальца: УДЕРЖАТЬ 0.5 с = ПКМ (быстрый тап ничего не делает)
• 3 пальца: тап = средняя кнопка
• 4 пальца: тап = рабочий стол
• 5 пальцев: тап = задачи
• 3 или 4 пальца: свайп в любую сторону

Все назначения меняются во вкладке «Команды».

ЖЕСТЫ
Нарисуй фигуру (круг, квадрат, галочку, букву). Приложение её распознает и выполнит привязанное действие.

КЛАВИАТУРА
Вкладка «Клавиатура»: текст сразу печатается на ПК.
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
    kw.setdefault("size_hint_y", None)
    lbl = Label(text=text, halign="left", valign="top", color=TEXT, **kw)
    lbl.bind(width=lambda i, w: setattr(i, "text_size", (w, None)),
             texture_size=lambda i, s: setattr(i, "height", s[1]))
    return lbl


def wrap(text, **kw):
    lbl = Label(text=text, halign="left", valign="middle", color=TEXT, **kw)
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


# ---------------- ВЫБОР ДЕЙСТВИЯ (поиск + список) ----------------
class ActionPicker(Popup):
    def __init__(self, current, on_pick, **kw):
        super().__init__(title="Выбери действие", size_hint=(0.94, 0.92), **kw)
        self.on_pick = on_pick
        self.current = current
        box = BoxLayout(orientation="vertical", spacing=dp(6), padding=dp(6))
        self.search = TextInput(hint_text="Поиск по названию", multiline=False,
                                size_hint_y=None, height=dp(46))
        self.search.bind(text=self.fill)
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(5))
        self.grid.bind(minimum_height=self.grid.setter("height"))
        sc = ScrollView()
        sc.add_widget(self.grid)
        box.add_widget(self.search)
        box.add_widget(sc)
        self.content = box
        self.fill()

    def fill(self, *a):
        q = self.search.text.lower().strip()
        self.grid.clear_widgets()
        for name in ACTIONS:
            if q and q not in name.lower():
                continue
            color = ACCENT if name == self.current else CARD
            self.grid.add_widget(btn(name, lambda b, n=name: self.pick(n),
                                     color=color, size_hint_y=None, height=dp(46)))

    def pick(self, name):
        self.dismiss()
        self.on_pick(name)


def action_button(get_value, set_value):
    """Кнопка, которая открывает выбор действия и показывает текущее значение."""
    b = btn(get_value(), size_hint_y=None, height=dp(46))

    def open_picker(*a):
        def done(name):
            set_value(name)
            b.text = name
        ActionPicker(get_value(), done).open()

    b.bind(on_release=open_picker)
    return b


# ---------------- ТАЧПАД ----------------
class TouchPad(Widget):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.touches = {}
        self.last_tap_pending = None
        self.hold_ev = None
        self.hold_done = False
        self.reset()
        self.bind(pos=self.redraw, size=self.redraw)

    def reset(self):
        self.t0 = 0
        self.moved = 0
        self.maxf = 0
        self.sx = self.sy = 0
        self.ax = self.ay = 0
        self.acc_scroll = 0
        self.hold_done = False

    def cancel_hold(self):
        if self.hold_ev:
            self.hold_ev.cancel()
            self.hold_ev = None

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
            self.cancel_hold()
            self.reset()
            self.t0 = time.time()
        self.touches[touch.uid] = touch.pos
        self.maxf = max(self.maxf, len(self.touches))
        self.cancel_hold()
        if len(self.touches) == 2:
            self.hold_ev = Clock.schedule_once(self._hold, 0.5)
        self.draw_dots()
        return True

    def _hold(self, dt):
        self.hold_ev = None
        if len(self.touches) == 2 and self.moved < dp(25) and self.maxf == 2:
            self.hold_done = True
            self.fire("2h")

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return False
        old = self.touches.get(touch.uid, touch.pos)
        self.touches[touch.uid] = touch.pos
        dx = touch.x - old[0]
        dy = touch.y - old[1]
        n = len(self.touches)
        self.moved += abs(dx) + abs(dy)
        if self.moved >= dp(25):
            self.cancel_hold()
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
        if len(self.touches) < 2:
            self.cancel_hold()
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
        if self.hold_done:
            return
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
            Color(*CARD)
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
        super().__init__(orientation="vertical", spacing=dp(6), padding=dp(8), **kw)
        self.last_points = None
        self.chosen = "ЛКМ"
        self.info = wrap("Нарисуй фигуру, и приложение выполнит действие",
                         size_hint_y=None, height=dp(40))
        self.pad = DrawPad(self.on_stroke, size_hint_y=0.4)
        self.name_in = TextInput(hint_text="Название жеста, например: Круг",
                                 multiline=False, size_hint_y=None, height=dp(46))
        self.action_btn = action_button(lambda: self.chosen, self._set_chosen)
        save_btn = btn("Сохранить последний рисунок", self.save_last,
                       color=ACCENT, size_hint_y=None, height=dp(46))
        self.del_btn = btn("Удалить жест (нажми, чтобы выбрать)", self.open_delete,
                           color=RED, size_hint_y=None, height=dp(46))
        self.list_lbl = autolabel("", size_hint_y=None)
        scroll = ScrollView()
        scroll.add_widget(self.list_lbl)

        for w in (self.info, self.pad, self.name_in, self.action_btn, save_btn, self.del_btn):
            self.add_widget(w)
        self.add_widget(scroll)
        self.refresh()

    def _set_chosen(self, name):
        self.chosen = name

    def refresh(self):
        text = "\n".join(f"• {g['name']} → {g['action']}" for g in GESTURES)
        self.list_lbl.text = text or "Сохранённых жестов пока нет"

    def open_delete(self, *a):
        if not GESTURES:
            self.info.text = "Жестов для удаления нет"
            return
        box = BoxLayout(orientation="vertical", spacing=dp(6), padding=dp(6))
        pop = Popup(title="Удалить жест", size_hint=(0.9, 0.7), content=box)
        for g in list(GESTURES):
            def remove(b, name=g["name"]):
                GESTURES[:] = [x for x in GESTURES if x["name"] != name]
                save_json("gestures.json", GESTURES)
                self.refresh()
                pop.dismiss()
            box.add_widget(btn(g["name"], remove, color=RED, size_hint_y=None, height=dp(46)))
        pop.open()

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
        GESTURES.append({"name": name, "points": self.last_points, "action": self.chosen})
        save_json("gestures.json", GESTURES)
        self.info.text = f"Жест «{name}» сохранён"
        self.refresh()


# ---------------- КЛАВИАТУРА ----------------
class KeyboardTab(BoxLayout):
    SENT = "\u200b"

    def __init__(self, **kw):
        super().__init__(orientation="vertical", spacing=dp(6), padding=dp(8), **kw)
        self._busy = False
        self.inp = TextInput(text=self.SENT, multiline=True,
                             hint_text="Пиши здесь, текст сразу печатается на ПК",
                             size_hint_y=0.45, font_size=dp(18))
        self.inp.bind(text=self.on_text)
        self.add_widget(self.inp)

        quick = [("Enter", "enter"), ("Esc", "esc"), ("Tab", "tab"), ("⌫", "backspace"),
                 ("Del", "delete"), ("←", "left"), ("→", "right"), ("↑", "up"), ("↓", "down")]
        grid = GridLayout(cols=5, size_hint_y=None, height=dp(100), spacing=dp(4))
        for label, key in quick:
            grid.add_widget(btn(label, lambda b, k=key: LINK.send({"t": "hotkey", "keys": k})))
        self.add_widget(grid)

        row2 = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(4))
        for label, keys in [("Копировать", "ctrl+c"), ("Вставить", "ctrl+v"),
                            ("Отменить", "ctrl+z"), ("Выделить всё", "ctrl+a")]:
            row2.add_widget(btn(label, lambda b, k=keys: LINK.send({"t": "hotkey", "keys": k}),
                                color=ACCENT))
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


# ---------------- КОМАНДЫ ----------------
class CommandsTab(ScrollView):
    def __init__(self, **kw):
        super().__init__(**kw)
        box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=dp(10))
        box.bind(minimum_height=box.setter("height"))
        box.add_widget(autolabel(HELP))
        box.add_widget(wrap("НАЗНАЧЕНИЕ ЖЕСТОВ ТАЧПАДА", size_hint_y=None, height=dp(36)))
        for key, title in TOUCH_KEYS:
            row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(6))
            row.add_widget(wrap(title, size_hint_x=0.45))
            row.add_widget(action_button(
                lambda k=key: CFG["touch"].get(k, "Ничего"),
                lambda name, k=key: self.set_touch(k, name)))
            box.add_widget(row)
        self.add_widget(box)

    def set_touch(self, key, value):
        CFG["touch"][key] = value
        save_json("config.json", CFG)


# ---------------- СВЯЗЬ ----------------
class ConnectTab(BoxLayout):
    PREFIXES = ["192.168.0.", "192.168.1.", "192.168.137.", "192.168.43.", "10.0.0.", "172.20.10."]

    def __init__(self, **kw):
        super().__init__(orientation="vertical", padding=dp(14), spacing=dp(10), **kw)
        self.ip = TextInput(text=CFG["ip"], hint_text="IP ПК, например 192.168.0.8",
                            multiline=False, size_hint_y=None, height=dp(50), font_size=dp(18))
        self.port = TextInput(text=str(CFG["port"]), multiline=False, input_filter="int",
                              size_hint_y=None, height=dp(50), font_size=dp(18))
        self.status = wrap("Не подключено", size_hint_y=None, height=dp(44))
        LINK.on_status = self.set_status

        row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(6))
        row.add_widget(btn("Подключиться", self.do_connect, color=ACCENT))
        row.add_widget(btn("Отключиться", lambda *a: LINK.disconnect(), color=RED))

        self.scan_btn = btn("Найти ПК в сети (сканирование)", self.scan_network,
                            size_hint_y=None, height=dp(50))

        self.sens = Slider(min=0.5, max=4, value=CFG["sens"], size_hint_y=None, height=dp(40))
        self.sens.bind(value=self.on_sens)

        self.add_widget(wrap("IP ПК", size_hint_y=None, height=dp(24)))
        self.add_widget(self.ip)
        self.add_widget(wrap("Порт", size_hint_y=None, height=dp(24)))
        self.add_widget(self.port)
        self.add_widget(row)
        self.add_widget(self.scan_btn)
        self.add_widget(self.status)
        self.add_widget(wrap("Чувствительность курсора", size_hint_y=None, height=dp(28)))
        self.add_widget(self.sens)
        self.add_widget(autolabel(
            "КАК ПОДКЛЮЧИТЬ\n"
            "1. Запусти pc_server.py на ПК.\n"
            "2. Обычный Wi-Fi: телефон и ПК в одной сети. Нажми «Найти ПК» или введи IP.\n"
            "3. Раздача с ноута: включи «Мобильный хот-спот» на ПК, подключи телефон к нему.\n"
            "   Нажми «Найти ПК», приложение проверит адреса хот-спота.\n"
            "4. Если телефон раздаёт Wi-Fi, ПК подключается к нему, и сканер найдёт ПК в его сети.\n"
            "5. Порт 5151 должен быть открыт в брандмауэре."))

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

    def scan_network(self, *a):
        self.set_status("Ищу ПК в сети, подожди...")
        self.scan_btn.disabled = True
        port = int(self.port.text or 5151)

        def probe(ip, found, lock):
            try:
                s = socket.create_connection((ip, port), timeout=0.5)
                s.close()
                with lock:
                    found.append(ip)
            except OSError:
                pass

        def run():
            found, lock = [], threading.Lock()
            for prefix in self.PREFIXES:
                threads = [threading.Thread(target=probe, args=(prefix + str(i), found, lock),
                                            daemon=True) for i in range(1, 255)]
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()
            Clock.schedule_once(lambda dt: self.scan_done(found))

        threading.Thread(target=run, daemon=True).start()

    def scan_done(self, found):
        self.scan_btn.disabled = False
        if not found:
            self.set_status("ПК не найден. Проверь, что сервер запущен и сеть одна и та же.")
            return
        self.ip.text = found[0]
        extra = f" (ещё: {', '.join(found[1:])})" if len(found) > 1 else ""
        self.set_status(f"Найден ПК: {found[0]}{extra}. Нажми «Подключиться».")


# ---------------- ПРИЛОЖЕНИЕ ----------------
class PlaDeckApp(App):
    def build(self):
        global DATA_DIR, CFG, GESTURES
        DATA_DIR = self.user_data_dir
        CFG = load_json("config.json", None) or {}
        for k, v in DEFAULT_CFG.items():
            if k == "touch":
                continue
            CFG.setdefault(k, v)
        if CFG.get("touch_v") != TOUCH_CFG_VERSION:
            CFG["touch"] = dict(DEFAULT_TOUCH)
            CFG["touch_v"] = TOUCH_CFG_VERSION
        for tk, tv in DEFAULT_TOUCH.items():
            CFG["touch"].setdefault(tk, tv)
        GESTURES = load_json("gestures.json", [])

        Window.clearcolor = BG

        self.gesture_tab = GestureTab()
        self.connect_tab = ConnectTab()
        self.touch_tab = BoxLayout(orientation="vertical")
        self.touch_tab.add_widget(wrap("Один тап, два, три, свайпы. Подробно: вкладка «Команды»",
                                       size_hint_y=None, height=dp(34)))
        self.touch_tab.add_widget(TouchPad())

        panel = TabbedPanel(do_default_tab=False, tab_width=dp(130), tab_height=dp(48))
        for title, content in [("Связь", self.connect_tab), ("Тачпад", self.touch_tab),
                               ("Жесты", self.gesture_tab), ("Клавиатура", KeyboardTab()),
                               ("Команды", CommandsTab())]:
            item = TabbedPanelItem(text=title)
            item.add_widget(content)
            panel.add_widget(item)
        return panel

    def on_stop(self):
        save_json("config.json", CFG)
        save_json("gestures.json", GESTURES)
        LINK.disconnect(silent=True)


if __name__ == "__main__":
    PlaDeckApp().run()

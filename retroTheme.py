# retroTheme.py
# 슈퍼 패미컴(SNES) 게임기 스타일 GUI 테마

import tkinter as tk
from tkinter import ttk

# 색상 상수 (슈퍼 패미컴 본체 색상 기반)
COLORS = {
    # 본체 색상
    'console_gray': '#C8C8C8',      # 본체 밝은 회색
    'console_dark': '#A0A0A0',      # 본체 어두운 회색
    'console_light': '#E8E8E8',     # 본체 하이라이트

    # 컨트롤러 버튼 색상 (ABXY)
    'btn_a_red': '#CC0000',         # A 버튼 빨강
    'btn_b_yellow': '#CCCC00',      # B 버튼 노랑
    'btn_x_blue': '#0000CC',        # X 버튼 파랑
    'btn_y_green': '#00CC00',       # Y 버튼 녹색

    # 로고 레인보우 색상
    'logo_red': '#E60012',
    'logo_blue': '#0066CC',
    'logo_green': '#00A651',
    'logo_yellow': '#FFCC00',

    # 기타 색상
    'purple_accent': '#6666AA',     # 보라색 악센트 (슬롯/포트)
    'dark_gray': '#404040',         # 어두운 회색 (텍스트)
    'black': '#1A1A1A',             # 검정
    'white': '#FFFFFF',             # 흰색
    'select_purple': '#8080C0',     # 선택 보라색
}

# 폰트 설정
FONTS = {
    'title': ('Segoe UI', 12, 'bold'),
    'normal': ('Segoe UI', 10),
    'button': ('Segoe UI', 9, 'bold'),
    'small': ('Segoe UI', 9),
}


def apply_mario_theme(root, style):
    """
    슈퍼 패미컴 스타일 테마를 적용하는 함수

    Args:
        root: tk.Tk 인스턴스 (메인 윈도우)
        style: ttk.Style 인스턴스
    """

    # 메인 윈도우 배경색 설정 (슈퍼패미컴 본체 회색)
    root.configure(bg=COLORS['console_gray'])

    # ttk 테마 설정
    style.theme_use('clam')

    # TFrame 스타일
    style.configure('TFrame',
                    background=COLORS['console_gray'])

    # TLabelframe 스타일 (그룹 프레임)
    style.configure('TLabelframe',
                    background=COLORS['console_gray'],
                    borderwidth=2,
                    relief='groove')

    style.configure('TLabelframe.Label',
                    background=COLORS['console_gray'],
                    foreground=COLORS['dark_gray'],
                    font=FONTS['normal'])

    # TLabel 스타일
    style.configure('TLabel',
                    background=COLORS['console_gray'],
                    foreground=COLORS['dark_gray'],
                    font=FONTS['normal'])

    # Title Label 스타일
    style.configure('Title.TLabel',
                    background=COLORS['console_gray'],
                    foreground=COLORS['purple_accent'],
                    font=FONTS['title'])

    # TButton 스타일 (슈퍼패미컴 버튼 스타일)
    style.configure('TButton',
                    background=COLORS['console_dark'],
                    foreground=COLORS['dark_gray'],
                    font=FONTS['button'],
                    borderwidth=2,
                    relief='raised',
                    padding=(8, 4))

    style.map('TButton',
              background=[('active', COLORS['console_light']),
                          ('pressed', COLORS['select_purple'])],
              foreground=[('active', COLORS['black']),
                          ('pressed', COLORS['white'])],
              relief=[('pressed', 'sunken')])

    # TEntry 스타일
    style.configure('TEntry',
                    fieldbackground=COLORS['white'],
                    foreground=COLORS['dark_gray'],
                    insertcolor=COLORS['dark_gray'],
                    font=FONTS['normal'],
                    borderwidth=2,
                    relief='sunken')

    style.map('TEntry',
              fieldbackground=[('focus', COLORS['white']),
                               ('!focus', COLORS['console_light'])])

    # TCombobox 스타일
    style.configure('TCombobox',
                    fieldbackground=COLORS['white'],
                    background=COLORS['console_dark'],
                    foreground=COLORS['dark_gray'],
                    arrowcolor=COLORS['dark_gray'],
                    font=FONTS['normal'],
                    borderwidth=2)

    style.map('TCombobox',
              fieldbackground=[('readonly', COLORS['white'])],
              foreground=[('readonly', COLORS['dark_gray'])],
              selectbackground=[('readonly', COLORS['select_purple'])],
              selectforeground=[('readonly', COLORS['white'])])

    # TProgressbar 스타일 (Y버튼 녹색)
    style.configure('TProgressbar',
                    background=COLORS['btn_y_green'],
                    troughcolor=COLORS['console_dark'],
                    borderwidth=2,
                    relief='sunken')

    # TScrollbar 스타일
    style.configure('TScrollbar',
                    background=COLORS['console_dark'],
                    troughcolor=COLORS['console_gray'],
                    arrowcolor=COLORS['dark_gray'],
                    borderwidth=1)

    style.map('TScrollbar',
              background=[('active', COLORS['select_purple'])])

    # Danger 버튼 스타일 (A버튼 빨강)
    style.configure('Danger.TButton',
                    background=COLORS['btn_a_red'],
                    foreground=COLORS['white'],
                    font=FONTS['button'])

    style.map('Danger.TButton',
              background=[('active', '#FF3333'),
                          ('pressed', '#990000')],
              foreground=[('active', COLORS['white'])])

    # Green 버튼 스타일 (Y버튼 녹색)
    style.configure('Green.TButton',
                    background=COLORS['btn_y_green'],
                    foreground=COLORS['white'],
                    font=FONTS['button'])

    style.map('Green.TButton',
              background=[('active', '#33FF33'),
                          ('pressed', '#009900')],
              foreground=[('active', COLORS['white']),
                          ('pressed', COLORS['white'])])

    # Blue 버튼 스타일 (X버튼 파랑)
    style.configure('Blue.TButton',
                    background=COLORS['btn_x_blue'],
                    foreground=COLORS['white'],
                    font=FONTS['button'])

    style.map('Blue.TButton',
              background=[('active', '#3333FF'),
                          ('pressed', '#000099')],
              foreground=[('active', COLORS['white'])])

    # Yellow 버튼 스타일 (B버튼 노랑)
    style.configure('Yellow.TButton',
                    background=COLORS['btn_b_yellow'],
                    foreground=COLORS['dark_gray'],
                    font=FONTS['button'])

    style.map('Yellow.TButton',
              background=[('active', '#FFFF33'),
                          ('pressed', '#999900')],
              foreground=[('active', COLORS['dark_gray'])])


def apply_listbox_style(listbox):
    """
    Listbox에 슈퍼 패미컴 스타일 적용

    Args:
        listbox: tk.Listbox 인스턴스
    """
    listbox.configure(
        bg=COLORS['white'],
        fg=COLORS['dark_gray'],
        selectbackground=COLORS['select_purple'],
        selectforeground=COLORS['white'],
        font=FONTS['normal'],
        borderwidth=2,
        relief='sunken',
        highlightthickness=1,
        highlightbackground=COLORS['console_dark'],
        highlightcolor=COLORS['purple_accent']
    )


def apply_text_style(text_widget):
    """
    Text 위젯에 슈퍼 패미컴 스타일 적용

    Args:
        text_widget: tk.Text 또는 scrolledtext.ScrolledText 인스턴스
    """
    text_widget.configure(
        bg=COLORS['white'],
        fg=COLORS['dark_gray'],
        insertbackground=COLORS['dark_gray'],
        selectbackground=COLORS['select_purple'],
        selectforeground=COLORS['white'],
        font=FONTS['normal'],
        borderwidth=2,
        relief='sunken',
        highlightthickness=1,
        highlightbackground=COLORS['console_dark'],
        highlightcolor=COLORS['purple_accent']
    )


def apply_toplevel_style(toplevel):
    """
    Toplevel 윈도우에 슈퍼 패미컴 스타일 적용

    Args:
        toplevel: tk.Toplevel 인스턴스
    """
    toplevel.configure(bg=COLORS['console_gray'])

# ShellOS Shell GUI
# Refer to Line 84 for Launcher Entries

import pygame
import sys
import os
import time
import subprocess
from datetime import datetime
from pygame import mixer
import platform
import socket
import threading
import win32gui
import win32process
import win32con
import ctypes
from PIL import Image

pygame.init()
mixer.init()

# --- CONFIGURATION & SCALING ---
WIDTH, HEIGHT = 1280, 720
TASKBAR_HEIGHT = 40  # Set to exactly 40px
ICON_SIZE = 32       # Scaled to fit 40px height comfortably
DEFAULT_BG = "ShellOS_1.png"

# --- COLOR PALETTE (Centered around #0D3772) ---
PRIMARY_BLUE = (13, 55, 114)   # #0D3772
DARK_BLUE    = (8, 25, 55)     # Deep navy for menus
HOVER_BLUE   = (30, 80, 150)   # Brighter blue for interaction
TASKBAR_DARK = (5, 12, 30)     # Deep navy taskbar
WHITE        = (255, 255, 255)
PROGRESS_BG  = (20, 20, 40)

# --- DIRECTORIES & PATHS ---
GRAPHICAL_SHELL_DIR = os.path.dirname(os.path.abspath(__file__))
SHELLOS_DIR = os.path.abspath(os.path.join(GRAPHICAL_SHELL_DIR, "..", ".."))
ICON_PATH = os.path.join(SHELLOS_DIR, "SYSTEM", "Graphical_Shell", "icons", "shellos.png")
ICO_PATH = os.path.join(SHELLOS_DIR, "SYSTEM", "Graphical_Shell", "icons", "shellos.ico")
SOUND_PATH = os.path.join(SHELLOS_DIR, "SYSTEM", "Graphical_Shell", "sounds", "ShlosStartup.mp3")
BACKGROUND_FOLDER = os.path.join(SHELLOS_DIR, "SYSTEM", "Graphical_Shell", "backgrounds")
LAUNCHER_ICON_PATH = os.path.join(SHELLOS_DIR, "SYSTEM", "Graphical_Shell", "icons", "launcher.png")
FILEMGR_ICON_PATH = os.path.join(SHELLOS_DIR, "SYSTEM", "Graphical_Shell", "icons", "filemgr.png")
BROWSER_ICON_PATH = os.path.join(SHELLOS_DIR, "SYSTEM", "Graphical_Shell", "icons", "browser.ico")
TERMINAL_ICON_PATH = os.path.join(SHELLOS_DIR, "SYSTEM", "Graphical_Shell", "icons", "terminal.png")

CONNECTED_ICON_PATH = os.path.join(SHELLOS_DIR, "SYSTEM", "Graphical_Shell", "icons", "connected.ico")
NOTCONNECTED_ICON_PATH = os.path.join(SHELLOS_DIR, "SYSTEM", "Graphical_Shell", "icons", "notconnected.ico")

# --- Network Threading Logic ---
is_connected = False
network_thread_running = True

def network_check_thread():
    global is_connected, network_thread_running
    while network_thread_running:
        try:
            host = socket.gethostbyname("www.google.com")
            s = socket.create_connection((host, 80), timeout=2)
            s.close()
            is_connected = True
        except:
            is_connected = False
        for _ in range(50): 
            if not network_thread_running: break
            time.sleep(0.1)

wifi_thread = threading.Thread(target=network_check_thread, daemon=True)
wifi_thread.start()

# --- Assets Loading ---
try:
    DEFAULT_PROGRAM_ICON = pygame.image.load(ICON_PATH).convert_alpha()
    DEFAULT_PROGRAM_ICON = pygame.transform.smoothscale(DEFAULT_PROGRAM_ICON, (ICON_SIZE, ICON_SIZE))
except:
    DEFAULT_PROGRAM_ICON = pygame.Surface((ICON_SIZE, ICON_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(DEFAULT_PROGRAM_ICON, PRIMARY_BLUE, DEFAULT_PROGRAM_ICON.get_rect(), border_radius=4)

PROGRESS_BAR_WIDTH = 400
PROGRESS_BAR_HEIGHT = 14
PROGRESS_BAR_BORDER = 3

programs = {
    "About Shellos": "System64/Programs/about.py",
    "Calculator": "System64/Programs/calc.py",
    "File Manager": "System64/Programs/filemgr.py",
    "Terminal": "System64/Programs/terminal.py",
    "Notepad": "System64/Programs/notepad.py",
    "ShellOS Browser": "System64/Programs/ShellOS-Browser/browser.py",
    "ShellOS Music": "System64/Programs/shellos-music/shlosmusic.py",
    "Tic Tac Toe": "System64/Programs/games/ttt.py",
    "Settings": "System64/Programs/settings.py",
}

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("ShellOS: Python Edition")

try:
    pygame.display.set_icon(pygame.image.load(ICON_PATH))
except:
    pygame.display.set_icon(pygame.Surface((32, 32), pygame.SRCALPHA))

if sys.platform == "win32":
    hwnd = pygame.display.get_wm_info()["window"]
    ctypes.windll.user32.SendMessageW(hwnd, 0x80, 0, ctypes.windll.shell32.ExtractIconW(0, ICO_PATH, 0))

try:
    logo_img = pygame.image.load(ICON_PATH).convert_alpha()
except:
    logo_img = pygame.Surface((100, 100), pygame.SRCALPHA)

def get_scaled_logo():
    max_width, max_height = WIDTH * 0.8, HEIGHT * 0.6
    if logo_img.get_width() == 0 or logo_img.get_height() == 0:
        return pygame.Surface((1,1), pygame.SRCALPHA)
    ratio = min(max_width / logo_img.get_width(), max_height / logo_img.get_height())
    new_size = (int(logo_img.get_width() * ratio), int(logo_img.get_height() * ratio))
    return pygame.transform.smoothscale(logo_img, new_size)

def draw_progress_bar(screen, x, y, width, height, progress, border=3):
    border_rect = pygame.Rect(x - border, y - border, width + border * 2, height + border * 2)
    pygame.draw.rect(screen, PRIMARY_BLUE, border_rect, border_radius=7)
    bg_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, PROGRESS_BG, bg_rect, border_radius=5)
    if progress > 0:
        progress_width = int(width * progress)
        progress_rect = pygame.Rect(x, y, progress_width, height)
        pygame.draw.rect(screen, WHITE, progress_rect, border_radius=5)

# Splash Screen
scaled_logo = get_scaled_logo()
start_time = time.time()
clock_splash = pygame.time.Clock()
running_splash = True

while running_splash:
    elapsed = time.time() - start_time
    progress = min(elapsed / 10.0, 1.0)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            network_thread_running = False
            pygame.quit(); sys.exit()
    screen.fill((5, 10, 25))
    logo_rect = scaled_logo.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
    screen.blit(scaled_logo, logo_rect)
    draw_progress_bar(screen, (WIDTH - PROGRESS_BAR_WIDTH) // 2, HEIGHT - 100, PROGRESS_BAR_WIDTH, PROGRESS_BAR_HEIGHT, progress)
    pygame.display.flip()
    clock_splash.tick(60)
    if progress >= 1.0 and elapsed >= 10:
        try:
            mixer.music.load(SOUND_PATH)
            mixer.music.play()
        except: pass
        running_splash = False

# UI Assets Loading
def load_background():
    bg_path = os.path.join(BACKGROUND_FOLDER, DEFAULT_BG)
    if os.path.exists(bg_path): return pygame.image.load(bg_path).convert()
    return None

bg_image = load_background()
if bg_image is None: bg_image = pygame.Surface((WIDTH, HEIGHT))

# Launcher and taskbar buttons scaled for 40px height
launcher_button_rect = pygame.Rect(5, HEIGHT - TASKBAR_HEIGHT + 4, ICON_SIZE, ICON_SIZE)
try:
    launcher_icon_scaled = pygame.transform.smoothscale(pygame.image.load(LAUNCHER_ICON_PATH).convert_alpha(), (ICON_SIZE, ICON_SIZE))
except: launcher_icon_scaled = pygame.Surface((ICON_SIZE, ICON_SIZE))

filemgr_button_rect = pygame.Rect(launcher_button_rect.right + 10, HEIGHT - TASKBAR_HEIGHT + 4, ICON_SIZE, ICON_SIZE) 
try:
    filemgr_icon_scaled = pygame.transform.smoothscale(pygame.image.load(FILEMGR_ICON_PATH).convert_alpha(), (ICON_SIZE, ICON_SIZE))
    filemgr_icon_available = True
except: filemgr_icon_available = False

browser_button_rect = pygame.Rect(filemgr_button_rect.right + 5, HEIGHT - TASKBAR_HEIGHT + 4, ICON_SIZE, ICON_SIZE)
try:
    browser_icon_scaled = pygame.transform.smoothscale(pygame.image.load(BROWSER_ICON_PATH).convert_alpha(), (ICON_SIZE, ICON_SIZE))
    browser_icon_available = True
except: browser_icon_available = False

terminal_button_rect = pygame.Rect(browser_button_rect.right + 5, HEIGHT - TASKBAR_HEIGHT + 4, ICON_SIZE, ICON_SIZE) 
try:
    terminal_icon_scaled = pygame.transform.smoothscale(pygame.image.load(TERMINAL_ICON_PATH).convert_alpha(), (ICON_SIZE, ICON_SIZE))
    terminal_icon_available = True
except: terminal_icon_available = False

try:
    connected_icon_scaled = pygame.transform.smoothscale(pygame.image.load(CONNECTED_ICON_PATH).convert_alpha(), (ICON_SIZE - 6, ICON_SIZE - 6))
    notconnected_icon_scaled = pygame.transform.smoothscale(pygame.image.load(NOTCONNECTED_ICON_PATH).convert_alpha(), (ICON_SIZE - 6, ICON_SIZE - 6))
    network_icons_available = True
except: network_icons_available = False

# Fonts
font = pygame.font.SysFont("Segoe UI", 20)
clock_font = pygame.font.SysFont("Segoe UI", 20)
program_font = pygame.font.SysFont("Segoe UI", 16)

menu_visible = False
menu_items = sorted(list(programs.keys()))
menu_item_height = 32
menu_width = 220
scroll_offset = 0
special_menu_open = False
special_menu_items = ["Shutdown", "About ShellOS", "Settings Panel"]
special_menu_rects = []

class LaunchedProgram:
    def __init__(self, name, process_obj):
        self.name, self.process, self.is_running = name, process_obj, True
        self.window_handle, self.window_title = None, name
        self.taskbar_rect = pygame.Rect(0, 0, 0, 0)
        self._find_window_and_title()

    def _find_window_and_title(self, retries=5, delay=0.5):
        if sys.platform == "win32":
            for i in range(retries):
                time.sleep(delay)
                hwnds = []
                def callback(hwnd, extra):
                    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        if pid == self.process.pid:
                            hwnds.append(hwnd)
                            return False
                    return True
                win32gui.EnumWindows(callback, None)
                if hwnds:
                    self.window_handle = hwnds[0]
                    self.window_title = win32gui.GetWindowText(self.window_handle)
                    return True
            return False

    def update_status(self):
        if self.process.poll() is not None: self.is_running = False
        if sys.platform == "win32" and self.window_handle:
            if win32gui.IsWindow(self.window_handle):
                new_title = win32gui.GetWindowText(self.window_handle)
                if new_title: self.window_title = new_title
            else:
                self.window_handle = None
                if not self._find_window_and_title(retries=1, delay=0.1): self.is_running = False

    def focus_window(self):
        if self.is_running and self.window_handle:
            try:
                win32gui.SetForegroundWindow(self.window_handle)
                if win32gui.IsIconic(self.window_handle):
                    win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)
            except: pass

launched_programs = []

def launch_program(program_name, path):
    full_path = os.path.join(SHELLOS_DIR, path)
    if os.path.exists(full_path):
        try:
            process = subprocess.Popen([sys.executable, full_path])
            launched_programs.append(LaunchedProgram(program_name, process))
        except: pass

def draw_transparent_taskbar(surface, rect, color, alpha):
    taskbar_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    taskbar_surface.fill((*color, alpha))
    surface.blit(taskbar_surface, rect.topleft)

def draw_rounded_transparent_rect(surface, rect, color_rgb, alpha, radius):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color_rgb, alpha), (0, 0, rect.width, rect.height), border_radius=radius)
    surface.blit(s, rect.topleft)

# Main Loop
running = True
clock = pygame.time.Clock()
bg_image_scaled = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
TASKBAR_TEXT_PADDING = 10

# Calculate initial button positions
launcher_button_rect = pygame.Rect(5, HEIGHT - TASKBAR_HEIGHT + 4, ICON_SIZE, ICON_SIZE)
filemgr_button_rect = pygame.Rect(launcher_button_rect.right + 10, HEIGHT - TASKBAR_HEIGHT + 4, ICON_SIZE, ICON_SIZE)
browser_button_rect = pygame.Rect(filemgr_button_rect.right + 5, HEIGHT - TASKBAR_HEIGHT + 4, ICON_SIZE, ICON_SIZE)
terminal_button_rect = pygame.Rect(browser_button_rect.right + 5, HEIGHT - TASKBAR_HEIGHT + 4, ICON_SIZE, ICON_SIZE)
DYNAMIC_TASKBAR_START_X = terminal_button_rect.right + 20

while running:
    launched_programs = [p for p in launched_programs if p.is_running]
    for p in launched_programs: p.update_status()

    # Ensure background is always scaled to current window size
    bg_image_scaled = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    
    # Recalculate button positions every frame based on current dimensions
    launcher_button_rect = pygame.Rect(5, HEIGHT - TASKBAR_HEIGHT + 4, ICON_SIZE, ICON_SIZE)
    filemgr_button_rect = pygame.Rect(launcher_button_rect.right + 10, HEIGHT - TASKBAR_HEIGHT + 4, ICON_SIZE, ICON_SIZE)
    browser_button_rect = pygame.Rect(filemgr_button_rect.right + 5, HEIGHT - TASKBAR_HEIGHT + 4, ICON_SIZE, ICON_SIZE)
    terminal_button_rect = pygame.Rect(browser_button_rect.right + 5, HEIGHT - TASKBAR_HEIGHT + 4, ICON_SIZE, ICON_SIZE)
    DYNAMIC_TASKBAR_START_X = terminal_button_rect.right + 20

    screen.blit(bg_image_scaled, (0, 0))
    draw_transparent_taskbar(screen, pygame.Rect(0, HEIGHT - TASKBAR_HEIGHT, WIDTH, TASKBAR_HEIGHT), TASKBAR_DARK, 230)
    
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    launcher_hover = launcher_button_rect.collidepoint((mouse_x, mouse_y))
    pygame.draw.rect(screen, HOVER_BLUE if launcher_hover else PRIMARY_BLUE, launcher_button_rect, border_radius=6)
    screen.blit(launcher_icon_scaled, launcher_button_rect.topleft)

    for rect, icon, available in [(filemgr_button_rect, filemgr_icon_scaled, filemgr_icon_available), 
                                  (browser_button_rect, browser_icon_scaled, browser_icon_available), 
                                  (terminal_button_rect, terminal_icon_scaled, terminal_icon_available)]:
        bg_color = HOVER_BLUE if rect.collidepoint((mouse_x, mouse_y)) else PRIMARY_BLUE
        pygame.draw.rect(screen, bg_color, rect, border_radius=6)
        if available: screen.blit(icon, rect.topleft)

    current_text_x = DYNAMIC_TASKBAR_START_X
    for p in launched_programs:
        txt_surf = program_font.render(p.window_title[:18], True, WHITE)
        btn_w = txt_surf.get_width() + TASKBAR_TEXT_PADDING * 2
        p.taskbar_rect = pygame.Rect(current_text_x, HEIGHT - TASKBAR_HEIGHT + 4, btn_w, TASKBAR_HEIGHT - 8)
        item_bg = HOVER_BLUE if p.taskbar_rect.collidepoint((mouse_x, mouse_y)) else PRIMARY_BLUE
        draw_rounded_transparent_rect(screen, p.taskbar_rect, item_bg, 200, 6)
        screen.blit(txt_surf, (p.taskbar_rect.x + TASKBAR_TEXT_PADDING, p.taskbar_rect.y + (p.taskbar_rect.height - txt_surf.get_height()) // 2))
        current_text_x += btn_w + 6

    time_str = datetime.now().strftime("%H:%M %b %d, %Y")
    clock_text = clock_font.render(time_str, True, WHITE)
    clock_x = WIDTH - clock_text.get_width() - 15
    network_icon_rect = pygame.Rect(clock_x - 45, HEIGHT - TASKBAR_HEIGHT + 4, ICON_SIZE, ICON_SIZE)
    pygame.draw.rect(screen, HOVER_BLUE if network_icon_rect.collidepoint((mouse_x, mouse_y)) else PRIMARY_BLUE, network_icon_rect, border_radius=6)
    
    if network_icons_available:
        screen.blit(connected_icon_scaled if is_connected else notconnected_icon_scaled, (network_icon_rect.x + 3, network_icon_rect.y + 3))

    screen.blit(clock_text, (clock_x, HEIGHT - TASKBAR_HEIGHT + (TASKBAR_HEIGHT - clock_text.get_height()) // 2))

    dots_menu_rect = pygame.Rect(network_icon_rect.x - 35, HEIGHT - TASKBAR_HEIGHT + (TASKBAR_HEIGHT - 26) // 2, 26, 26)
    pygame.draw.rect(screen, HOVER_BLUE if dots_menu_rect.collidepoint((mouse_x, mouse_y)) else DARK_BLUE, dots_menu_rect, border_radius=6)
    for i in [-5, 0, 5]: pygame.draw.circle(screen, WHITE, (dots_menu_rect.centerx, dots_menu_rect.centery + i), 2)

    if special_menu_open:
        special_menu_rects = []
        for i, label in enumerate(special_menu_items):
            # Stack items upward: first item at top, last item closest to dots menu
            y_pos = dots_menu_rect.top - 10 - ((len(special_menu_items) - i) * 40)
            rect = pygame.Rect(dots_menu_rect.centerx - 95, y_pos, 190, 35)
            special_menu_rects.append((rect, label))
            draw_rounded_transparent_rect(screen, rect, HOVER_BLUE if rect.collidepoint((mouse_x, mouse_y)) else DARK_BLUE, 240, 8)
            screen.blit(font.render(label, True, WHITE), (rect.x + 10, rect.y + 8))

    if menu_visible:
        items = menu_items[scroll_offset:scroll_offset + 10]
        menu_height = len(items) * menu_item_height + 10
        # Position launcher menu above taskbar
        menu_y = HEIGHT - TASKBAR_HEIGHT - menu_height - 5
        menu_bg = pygame.Rect(5, menu_y, menu_width, menu_height)
        draw_rounded_transparent_rect(screen, menu_bg, DARK_BLUE, 240, 10)
        for i, item in enumerate(items):
            item_rect = pygame.Rect(5, menu_y + 5 + i * menu_item_height, menu_width, menu_item_height)
            if item_rect.collidepoint((mouse_x, mouse_y)):
                pygame.draw.rect(screen, PRIMARY_BLUE, item_rect, border_radius=4)
            screen.blit(font.render(item, True, WHITE), (item_rect.x + 12, item_rect.y + 8))

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            bg_image_scaled = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if launcher_button_rect.collidepoint(event.pos):
                menu_visible, special_menu_open = not menu_visible, False
            elif filemgr_button_rect.collidepoint(event.pos): launch_program("File Manager", "System64/Programs/filemgr.py")
            elif browser_button_rect.collidepoint(event.pos): launch_program("ShellOS Browser", "System64/Programs/ShellOS-Browser/browser.py")
            elif terminal_button_rect.collidepoint(event.pos): launch_program("Terminal", "System64/Programs/terminal.py")
            elif dots_menu_rect.collidepoint(event.pos): 
                special_menu_open, menu_visible = not special_menu_open, False
            elif special_menu_open:
                for rect, label in special_menu_rects:
                    if rect.collidepoint(event.pos):
                        if label == "Shutdown": running = False
                        elif label == "About ShellOS": launch_program("About Shellos", "System64/Programs/about.py")
                        elif label == "Settings Panel": launch_program("Settings", "System64/Programs/settings.py")
                        special_menu_open = False
            elif menu_visible:
                for i, item in enumerate(menu_items[scroll_offset:scroll_offset+10]):
                    items = menu_items[scroll_offset:scroll_offset + 10]
                    menu_height = len(items) * menu_item_height + 10
                    menu_y = HEIGHT - TASKBAR_HEIGHT - menu_height - 5
                    if pygame.Rect(5, menu_y + 5 + i * menu_item_height, menu_width, menu_item_height).collidepoint(event.pos):
                        launch_program(item, programs[item]); menu_visible = False
            else:
                for p in launched_programs:
                    if p.taskbar_rect.collidepoint(event.pos): p.focus_window()

    pygame.display.update()
    clock.tick(30)

network_thread_running = False
pygame.quit()
sys.exit()
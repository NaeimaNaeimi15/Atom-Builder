"""
Atom Builder (Pygame) — نسخه کارتونی و کلیکی
نحوهٔ کار:
- کلیک روی دکمه Proton/Neutron/Electron -> ذره ساخته می‌شود
- پروتون/نوترون داخل هسته قرار می‌گیرند (چیدمان پویا)
- الکترون‌ها به ترتیب در اولین مدار خالی قرار می‌گیرند (مدل بوهر ساده)
- اطلاعات عنصر (نام، عدد اتمی، عدد جرمی، یون و الکترون‌ها در لایه‌ها) نمایش داده می‌شود

اجرا:
> pip install pygame
> python atom_builder.py
"""

import pygame
import sys
import math
import random

pygame.init()
WIDTH, HEIGHT = 1000, 650
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Atom Builder — شبیه‌ساز ساخت اتم")

FPS = 60
CLOCK = pygame.time.Clock()

# ---------------------------
# تنظیمات بصری (کارتونی)
# ---------------------------
BG_COLOR = (30, 35, 40)
PANEL_COLOR = (40, 45, 55)
ACCENT = (100, 160, 255)
PROTON_COLOR = (235, 85, 85)    # قرمز
NEUTRON_COLOR = (200, 200, 200) # خاکستری روشن
ELECTRON_COLOR = (95, 140, 255) # آبی کارتونی
NUCLEUS_BORDER = (255, 220, 120)
SHELL_COLOR = (150, 150, 150)

FONT = pygame.font.SysFont("arial", 18)
BIGFONT = pygame.font.SysFont("arial", 26, bold=True)

# ---------------------------
# جدول عنصرها (نماد و نام) — تا 36 کافی برای نهم
# ---------------------------
ELEMENTS = {
    1: ("H", "Hydrogen"),
    2: ("He", "Helium"),
    3: ("Li", "Lithium"),
    4: ("Be", "Beryllium"),
    5: ("B", "Boron"),
    6: ("C", "Carbon"),
    7: ("N", "Nitrogen"),
    8: ("O", "Oxygen"),
    9: ("F", "Fluorine"),
    10: ("Ne", "Neon"),
    11: ("Na", "Sodium"),
    12: ("Mg", "Magnesium"),
    13: ("Al", "Aluminium"),
    14: ("Si", "Silicon"),
    15: ("P", "Phosphorus"),
    16: ("S", "Sulfur"),
    17: ("Cl", "Chlorine"),
    18: ("Ar", "Argon"),
    19: ("K", "Potassium"),
    20: ("Ca", "Calcium"),
    21: ("Sc", "Scandium"),
    22: ("Ti", "Titanium"),
    23: ("V", "Vanadium"),
    24: ("Cr", "Chromium"),
    25: ("Mn", "Manganese"),
    26: ("Fe", "Iron"),
    27: ("Co", "Cobalt"),
    28: ("Ni", "Nickel"),
    29: ("Cu", "Copper"),
    30: ("Zn", "Zinc"),
    31: ("Ga", "Gallium"),
    32: ("Ge", "Germanium"),
    33: ("As", "Arsenic"),
    34: ("Se", "Selenium"),
    35: ("Br", "Bromine"),
    36: ("Kr", "Krypton"),
}

# ---------------------------
# محل‌ها و اندازه‌ها
# ---------------------------
SIDEBAR_X = WIDTH - 260
SIDEBAR_W = 240
CENTER = (WIDTH//2 - 100, HEIGHT//2)  # مرکز نمایش اتم (کمی به چپ برای پنل)
NUCLEUS_RADIUS = 60
SHELL_RADII = [NUCLEUS_RADIUS + 40, NUCLEUS_RADIUS + 90, NUCLEUS_RADIUS + 140, NUCLEUS_RADIUS + 190]  # سه مدار
SHELL_CAPACITIES = [2, 8, 18, 32]  # سادگی: سه لایه اصلی

# دکمه‌ها
BUTTON_W, BUTTON_H = 200, 44
BUTTON_START_Y = 40

# ---------------------------
# وضعیت اتم (داده‌ها)
# ---------------------------
protons = []   # هر پروتون: (x,y) برای نمایش داخل هسته
neutrons = []  # هر نوترون: (x,y)
electrons = [[], [], [], []]  # هر لیست داخل نمایشگر برای هر مدار: داخل هر آیتم زاویه (radians)

# تاریخچه برای undo ساده
history = []  # لیستی از ('p'/'n'/'e', extra_info)

# ---------------------------
# توابع کمکی طراحی
# ---------------------------
def draw_rounded_rect(surface, rect, color, radius=8):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_sidebar():
    # پنل سمت راست
    panel_rect = pygame.Rect(SIDEBAR_X, 0, SIDEBAR_W, HEIGHT)
    draw_rounded_rect(SCREEN, panel_rect, PANEL_COLOR, radius=12)

    # عنوان
    title_surf = BIGFONT.render("Atom Builder", True, ACCENT)
    SCREEN.blit(title_surf, (SIDEBAR_X + 14, 8))

    # دکمه‌ها
    bx = SIDEBAR_X + 20
    y = BUTTON_START_Y + 10

    # proton button
    p_rect = pygame.Rect(bx, y, BUTTON_W, BUTTON_H)
    draw_rounded_rect(SCREEN, p_rect, PROTON_COLOR)
    SCREEN.blit(FONT.render("Add Proton", True, (255,255,255)), (bx + 12, y + 12))
    y += BUTTON_H + 12

    # neutron button
    n_rect = pygame.Rect(bx, y, BUTTON_W, BUTTON_H)
    draw_rounded_rect(SCREEN, n_rect, NEUTRON_COLOR)
    SCREEN.blit(FONT.render("Add Neutron", True, (0,0,0)), (bx + 12, y + 12))
    y += BUTTON_H + 12

# electron button
    e_rect = pygame.Rect(bx, y, BUTTON_W, BUTTON_H)
    draw_rounded_rect(SCREEN, e_rect, ELECTRON_COLOR)
    SCREEN.blit(FONT.render("Add Electron ", True, (255,255,255)), (bx + 12, y + 12))
    y += BUTTON_H + 18

    # reset و undo
    r_rect = pygame.Rect(bx, y, 95, 36)
    u_rect = pygame.Rect(bx+105, y, 95, 36)
    draw_rounded_rect(SCREEN, r_rect, (220,70,120))
    draw_rounded_rect(SCREEN, u_rect, (120,200,140))
    SCREEN.blit(FONT.render("Reset", True, (255,255,255)), (bx + 32, y + 8))
    SCREEN.blit(FONT.render("Undo", True, (0,0,0)), (bx + 140, y + 8))
    y += 48

    # توضیحات کوتاه
    lines = [
    "Guide:",
    "-Click buttons to add particles",
    "-Protons/Neutrons go into nucleus",
    "-Electrons fill shells(2-8-8-2 rule)",
    "-Use Undo or Reset buttons"
    ]
    ly = y + 6
    for l in lines:
        SCREEN.blit(FONT.render(l, True, (220,220,220)), (SIDEBAR_X + 14, ly))
        ly += 20

    # بازگرداندن rectها تا رویدادها بررسی شوند
    return {
        "proton": p_rect,
        "neutron": n_rect,
        "electron": e_rect,
        "reset": r_rect,
        "undo": u_rect,
    }

def place_proton():
    # موقعیت تصادفی منظم داخل هسته (بدون بیرون زدن)
    for _ in range(100):
        angle = random.random() * math.tau
        r = random.random() * (NUCLEUS_RADIUS - 12)
        x = CENTER[0] + r * math.cos(angle)
        y = CENTER[1] + r * math.sin(angle)
        # ساده: بدون چک برخورد
        protons.append((x,y))
        history.append(('p',))
        return

def place_neutron():
    for _ in range(100):
        angle = random.random() * math.tau
        r = random.random() * (NUCLEUS_RADIUS - 12)
        x = CENTER[0] + r * math.cos(angle)
        y = CENTER[1] + r * math.sin(angle)
        neutrons.append((x,y))
        history.append(('n',))
        return

# تغيير داده شده: تابع جدید برای تعیین لایه مناسب بر اساس قانون 8-18-8
def get_target_shell():
    """
    تعیین می‌کند الکترون جدید باید در کدام لایه قرار بگیرد
    قانون: 2, 8, 8, 2, سپس ادامه پر شدن لایه سوم تا 18, سپس لایه چهارم تا 32
    """
    current_shells = [len(lst) for lst in electrons]
    
    # لایه اول: حداکثر 2
    if current_shells[0] < 2:
        return 0
    
    # لایه دوم: حداکثر 8
    if current_shells[1] < 8:
        return 1
    
    # لایه سوم: مرحله اول - تا 8 الکترون اول
    if current_shells[2] < 8:
        return 2
    
    # لایه چهارم: 2 الکترون اول (پتاسیم و کلسیم)
    if current_shells[3] < 2:
        return 3
    
    # برگشت به لایه سوم: از 8 تا 18 (اسکاندیم تا روی)
    if current_shells[2] < 18:
        return 2
    
    # ادامه لایه چهارم: از 2 به بعد
    if current_shells[3] < 32:
        return 3
    
    # همه لایه‌ها پر شده
    return None

# تغيير داده شده: تابع به‌روزرسانی شده برای زاویه‌دهی
def get_electron_angle(shell_index, electron_number):
    """
    الگوی قرارگیری الکترون‌ها در لایه:
    - لایه اول (ظرفیت 2): دو الکترون در دو سمت مخالف -> زاویه 0 و π
    - لایه‌های دیگر: الکترون‌ها به صورت جفت‌های مخالف قرار می‌گیرند
    """
    if shell_index == 0:  # لایه K (ظرفیت 2)
        angles = [0, math.pi]  # 0° و 180°
        return angles[electron_number % 2]
    
    # برای لایه‌های دوم، سوم و چهارم: الگوی متقارن با جفت‌های مخالف
    # الگوی پایه: 8 جهت اصلی (هر 45 درجه یک جهت)
    base_angles = [0, math.pi, math.pi/2, 3*math.pi/2, 
                  math.pi/4, 5*math.pi/4, 3*math.pi/4, 7*math.pi/4]
    
    # اگر تعداد الکترون‌ها کمتر از 8 باشد، از زوایای اصلی استفاده کن
    if electron_number < len(base_angles):
        return base_angles[electron_number]
    else:
        # برای الکترون‌های بیشتر، از زوایای میانی استفاده کن
        extra = electron_number - len(base_angles)
        step = (2 * math.pi) / (len(base_angles) + extra)
        return (extra * step) % (2 * math.pi)
    
# تغيير داده شده: تابع place_electron بازنویسی شده
def place_electron():
    # تعیین لایه هدف
    target_shell = get_target_shell()
    
    if target_shell is None:
        print("تمامی لایه‌های الکترونی پر شده‌اند!")
        return
    
    # محاسبه زاویه مناسب بر اساس تعداد فعلی الکترون‌های آن لایه
    current_count = len(electrons[target_shell])
    angle = get_electron_angle(target_shell, current_count)
    # اضافه کردن نوسان بسیار کم برای ظاهر طبیعی
    angle += random.uniform(-0.03, 0.03)
    
    electrons[target_shell].append(angle)
    history.append(('e', target_shell))

def undo_last():
    if not history:
        return
    last = history.pop()
    if last[0] == 'p':
        if protons:
            protons.pop()
    elif last[0] == 'n':
        if neutrons:
            neutrons.pop()
    elif last[0] == 'e':
        shell = last[1]
        if electrons[shell]:
            electrons[shell].pop()

def reset_all():
    protons.clear()
    neutrons.clear()
    for lst in electrons:
        lst.clear()
    history.clear()

# ---------------------------
# محاسبات اتمی
# ---------------------------
def atomic_number():
    return len(protons)

def mass_number():
    return len(protons) + len(neutrons)

def electrons_count():
    return sum(len(lst) for lst in electrons)

def element_info():
    z = atomic_number()
    # مقدار پیش‌فرض برای زمانی که Z در جدول نباشد
    symbol = "?"
    name = "Unknown"
    if z in ELEMENTS:
        symbol, name = ELEMENTS[z]
    
    # یون یا اتم؟
    e_count = electrons_count()
    ion = ""
    if e_count == z:
        ion = "Neutral"
    elif e_count < z:
        ion = f"{symbol}⁺{z - e_count}" if z in ELEMENTS else f"cations (+{z - e_count})"
    else:
        ion = f"{symbol}⁻{e_count - z}" if z in ELEMENTS else f"anions ({e_count - z} -)"
    # electrons per shell (نمایش ظرفیت نهایی برای شفافیت)
    shells = [len(lst) for lst in electrons]
    return {
        "z": z,
        "mass": mass_number(),
        "symbol": symbol,
        "name": name,
        "ion": ion,
        "shells": shells,
        "electrons": e_count
    }

# ---------------------------
# رسم اتم و ذرات
# ---------------------------
def draw_nucleus():
    # حلقه بیرونی هسته
    pygame.draw.circle(SCREEN, NUCLEUS_BORDER, CENTER, NUCLEUS_RADIUS+6, width=3)
    # هسته پر: محتوای پروتون/نوترون به صورت دایره‌های کوچک داخل هسته
    # رسم پروتون‌ها و نوترون‌ها به طور لایه‌ای برای نرمی نمایش
    # اول نوترون‌ها (خاکستری) بعد پروتون‌ها (قرمز) برای جلوه
    for x,y in neutrons:
        pygame.draw.circle(SCREEN, NEUTRON_COLOR, (int(x),int(y)), 10)
        pygame.draw.circle(SCREEN, (180,180,180), (int(x),int(y)), 10, 2)
    for x,y in protons:
        pygame.draw.circle(SCREEN, PROTON_COLOR, (int(x),int(y)), 10)
        pygame.draw.circle(SCREEN, (180,50,50), (int(x),int(y)), 10, 2)
    # مرکز هسته نمایش (نرمی)
    pygame.draw.circle(SCREEN, (255,255,255,30), CENTER, 6)

def draw_shells_and_electrons(frame_count):
    # رسم مدارها (4 مدار)
    for i, r in enumerate(SHELL_RADII):
        # نوسان ریز برای کارتونی شدن
        wobble = math.sin(frame_count * 0.01 + i) * 1.8
        pygame.draw.circle(SCREEN, SHELL_COLOR, CENTER, int(r + wobble), width=2)

        # رسم الکترون‌ها روی مدار i
        for idx, angle in enumerate(electrons[i]):
            # زاویه نهایی کمی بر اساس frame تغییر کند تا نقطه انگار کمی در حال حرکت باشد
            ang = angle + math.sin(frame_count * 0.02 + idx) * 0.04
            x = CENTER[0] + (r) * math.cos(ang)
            y = CENTER[1] + (r) * math.sin(ang)
            # الکترون: دایره براق با هاله
            ex, ey = int(x), int(y)
            pygame.draw.circle(SCREEN, (255,255,255), (ex,ey), 8)  # نور
            pygame.draw.circle(SCREEN, ELECTRON_COLOR, (ex,ey), 6)
            pygame.draw.circle(SCREEN, (30,30,60), (ex,ey), 6, 2)

def draw_center_label():
    info = element_info()
    x = 310
    y = 20
    # جعبه اطلاعات کوچک بالای جدول
    title = BIGFONT.render(f"{info['symbol'] or '?'}  {info['name']}", True, (240,240,240))
    SCREEN.blit(title, (x - title.get_width(), y))
    y += 36
    
    
    lines = [
        f"Atomic number (Z): {info['z']}",
        f"Mass number (A): {info['mass']}",
        f"Total electrons: {info['electrons']}",
        f"Ion state: {info['ion']}",
        f"Electrons per shell: {','.join(str(s)for s in info['shells'])}",
    ]
    for l in lines:
        SCREEN.blit(FONT.render(l, True, (220,220,220)), (x - 280, y))
        y += 20

# ---------------------------
# Main loop
# ---------------------------
def main():
    frame = 0
    running = True

    while running:
        CLOCK.tick(FPS)
        frame += 1
        SCREEN.fill(BG_COLOR)

        # رسم پنل و دکمه‌ها و گرفتن رفرنس
        btns = draw_sidebar()

        # رسم اتم (در وسط)
        draw_shells_and_electrons(frame)
        draw_nucleus()
        draw_center_label()

        # رسم توضیحات پایینِ صفحه (راهنما/وضعیت)
        info = element_info()
        status_text = f"{info['name']}  |  Z={info['z']}  A={info['mass']}  |  {info['ion']}"
        status_surf = FONT.render(status_text, True, (200,200,200))
        SCREEN.blit(status_surf, (20, HEIGHT - 40))

        # نمایش تعداد پروتون/نوترون بزرگ‌تر روی هسته
        pcount = len(protons)
        ncount = len(neutrons)
        center_text = FONT.render(f"P: {pcount}   N: {ncount}", True, (240,240,240))
        SCREEN.blit(center_text, (CENTER[0] - 40, CENTER[1] - 10))
        
        SIGN_FONT = pygame.font.SysFont("arial", 15, bold = True, italic = True)
        signature = SIGN_FONT.render(" Created by Elina Taj and Naeima Naeimi", True, (80,80,95))
        signature_rect = signature.get_rect(bottomright = (WIDTH - 24, HEIGHT - 30))
        SCREEN.blit(signature, signature_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # اگر روی دکمهٔ پروتون کلیک شد
                if btns["proton"].collidepoint((mx,my)):
                    place_proton()
                elif btns["neutron"].collidepoint((mx,my)):
                    place_neutron()
                elif btns["electron"].collidepoint((mx,my)):
                    place_electron()
                elif btns["reset"].collidepoint((mx,my)):
                    reset_all()
                elif btns["undo"].collidepoint((mx,my)):
                    undo_last()
                else:
                    # کلیک روی صفحهٔ اصلی (در صورت نیاز مستقبلاً می‌توانیم کلیک روی مدار خاص اضافه کنیم)
                    pass

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
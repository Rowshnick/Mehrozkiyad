# ============================================================
#   Theme System for Astrology Chart Renderer
#   Author: Roshina Project
#   Description:
#       Centralized theme definitions for rendering charts.
#       Each theme controls:
#           - Background colors
#           - Zodiac ring colors
#           - House line colors
#           - Planet glyph colors
#           - Aspect line colors
#           - Fonts and sizes
#           - Special styling parameters
# ============================================================

THEMES = {

    # --------------------------------------------------------
    #  LIGHT THEME
    # --------------------------------------------------------
   "light": {
    "background": "#FAFAFA",          # سفید ملایم، نه سفید خالص
    "zodiac_circle": "#555555",       # خاکستری تیره‌تر برای وضوح بهتر
    "zodiac_text": "#1A1A1A",         # مشکی ملایم، خوانایی بالا
    "house_lines": "#B0B0B0",         # خاکستری روشن و ظریف
    "house_numbers": "#333333",       # کمی تیره‌تر برای خوانایی

    "planet_color": "#000000",        # سیارات مشکی برای وضوح
    "planet_label_color": "#444444",  # درجه‌ها کمی روشن‌تر

    "aspect_colors": {
        "conjunction": "#000000",     # مشکی
        "opposition": "#E53935",      # قرمز ملایم‌تر و مدرن‌تر
        "square": "#E53935",          # همان رنگ برای هماهنگی
        "trine": "#1E88E5",           # آبی روشن و شیک
        "sextile": "#43A047"          # سبز ملایم و هماهنگ
    },

    "font": "Vazirmatn-Regular",

    "planet_size": 20,                # کمی بزرگ‌تر برای زیبایی
    "planet_label_size": 11,
    "zodiac_size": 22,                # خوانایی بهتر
    "house_number_size": 13,

    "zodiac_ring_width": 2.0,         # کمی ضخیم‌تر برای وضوح
    "house_line_width": 1.1,          # ظریف و مینیمال
    "aspect_line_alpha": 0.80         # ملایم‌تر از نسخه قبلی
    },

    # --------------------------------------------------------
    #  DARK THEME (DEFAULT)
    # --------------------------------------------------------
    "dark": {
        "background": "#000000",
        "zodiac_circle": "#AAAAAA",
        "zodiac_text": "#DDDDDD",
        "house_lines": "#888888",
        "house_numbers": "#BBBBBB",

        "planet_color": "#FFFFFF",
        "planet_label_color": "#DDDDDD",

        "aspect_colors": {
            "conjunction": "#FFFFFF",
            "sextile": "#66CCFF",
            "square": "#FF6666",
            "trine": "#66FF99",
            "opposition": "#FF4444"
        },

        "font": "DejaVu Sans",
        "planet_size": 16,
        "planet_label_size": 10,
        "zodiac_size": 18,
        "house_number_size": 12,

        "zodiac_ring_width": 1.4,
        "house_line_width": 1.0,
        "aspect_line_alpha": 0.90
    },

    # --------------------------------------------------------
    #  GOLD THEME (LUXURY)
    # --------------------------------------------------------
    "gold": {
        "background": "#000000",
        "zodiac_circle": "#D4AF37",
        "zodiac_text": "#FFD700",
        "house_lines": "#B8860B",
        "house_numbers": "#FFD700",

        "planet_color": "#FFFFFF",
        "planet_label_color": "#FFD700",

        "aspect_colors": {
            "conjunction": "#FFD700",
            "sextile": "#E6C200",
            "square": "#FF6666",
            "trine": "#66FF99",
            "opposition": "#FF4444"
        },

        "font": "DejaVu Sans",
        "planet_size": 18,
        "planet_label_size": 11,
        "zodiac_size": 20,
        "house_number_size": 13,

        "zodiac_ring_width": 1.8,
        "house_line_width": 1.2,
        "aspect_line_alpha": 0.95
    },

    # --------------------------------------------------------
    #  MINIMAL THEME (CLEAN & MODERN)
    # --------------------------------------------------------
    "minimal": {
        "background": "#FFFFFF",
        "zodiac_circle": "#000000",
        "zodiac_text": "#000000",
        "house_lines": "#000000",
        "house_numbers": "#000000",

        "planet_color": "#000000",
        "planet_label_color": "#000000",

        "aspect_colors": {
            "conjunction": "#000000",
            "sextile": "#000000",
            "square": "#000000",
            "trine": "#000000",
            "opposition": "#000000"
        },

        "font": "DejaVu Sans",
        "planet_size": 14,
        "planet_label_size": 10,
        "zodiac_size": 16,
        "house_number_size": 12,

        "zodiac_ring_width": 1.0,
        "house_line_width": 0.8,
        "aspect_line_alpha": 0.60
    },

    # --------------------------------------------------------
    #  ROSHINA SIGNATURE THEME (CUSTOM)
    # --------------------------------------------------------
    "roshina": {
        "background": "#0A0A0F",
        "zodiac_circle": "#C77DFF",
        "zodiac_text": "#E0B3FF",
        "house_lines": "#9D4EDD",
        "house_numbers": "#E0B3FF",

        "planet_color": "#FFFFFF",
        "planet_label_color": "#C77DFF",

        "aspect_colors": {
            "conjunction": "#FFFFFF",
            "sextile": "#80FFEA",
            "square": "#FF6B6B",
            "trine": "#8AFF80",
            "opposition": "#FF4D4D"
        },

        "font": "DejaVu Sans",
        "planet_size": 18,
        "planet_label_size": 11,
        "zodiac_size": 20,
        "house_number_size": 13,

        "zodiac_ring_width": 1.8,
        "house_line_width": 1.2,
        "aspect_line_alpha": 0.92
    }
}


# ------------------------------------------------------------
# Helper function to get theme safely
# ------------------------------------------------------------
def get_theme(name: str):
    """Return theme dictionary, fallback to dark theme."""
    return THEMES.get(name.lower(), THEMES["dark"])

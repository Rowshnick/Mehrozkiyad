# ============================================================
#   Theme System for Astrology Chart Renderer
#   Author: Roshina Project
# ============================================================

THEMES = {

    # --------------------------------------------------------
    #  LIGHT THEME
    # --------------------------------------------------------
    "light": {
        "background": "#FAFAFA",
        "zodiac_circle": "#555555",
        "zodiac_text": "#1A1A1A",
        "house_lines": "#B0B0B0",
        "house_numbers": "#333333",

        "planet_color": "#000000",
        "planet_label_color": "#444444",

        "aspect_colors": {
            "conjunction": "#000000",
            "opposition": "#E53935",
            "square": "#E53935",
            "trine": "#1E88E5",
            "sextile": "#43A047"
        },

        "font": "Vazirmatn-Regular",

        "planet_size": 20,
        "planet_label_size": 11,
        "zodiac_size": 22,
        "house_number_size": 13,

        "zodiac_ring_width": 2.0,
        "house_line_width": 1.1,
        "aspect_line_alpha": 0.80
    },

    # --------------------------------------------------------
    #  DARK THEME
    # --------------------------------------------------------
    "dark": {
        "background": "#0B0C10",
        "zodiac_circle": "#9D4EDD",
        "zodiac_text": "#E0B3FF",
        "house_lines": "#6A4FBF",
        "house_numbers": "#C9A7FF",

        "planet_color": "#FFFFFF",
        "planet_label_color": "#C77DFF",

        "aspect_colors": {
            "conjunction": "#FFFFFF",
            "opposition": "#FF4D6D",
            "square": "#FF4D6D",
            "trine": "#80FFEA",
            "sextile": "#8AFF80"
        },

        "font": "Vazirmatn-Regular",

        "planet_size": 20,
        "planet_label_size": 11,
        "zodiac_size": 22,
        "house_number_size": 13,

        "zodiac_ring_width": 2.0,
        "house_line_width": 1.1,
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
    #  MINIMAL THEME
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
    #  ROSHINA SIGNATURE THEME
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
# Theme list for UI / dropdowns
# ------------------------------------------------------------
THEME_OPTIONS = list(THEMES.keys())

# ------------------------------------------------------------
# Helper function
# ------------------------------------------------------------
def get_theme(name: str):
    return THEMES.get(name.lower(), THEMES["dark"])

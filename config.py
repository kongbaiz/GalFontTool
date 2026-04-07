import sys

# 依赖检测
try:
    import opencc
    HAS_OPENCC = True
except ImportError:
    HAS_OPENCC = False

try:
    import brotli
    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False

# 主题定义
THEMES = {
    "简约蓝 (Clean)": {
        "bg_grad": ["#EEF2F5", "#E9EEF2", "#E4EAF0"],
        "accent": "#3A6784",
        "btn_hover": "#30566E",
        "text_main": "#25313C",
        "text_dim": "#556371",
        "card_bg": "#FBFCFD",
        "input_bg": "#FFFFFF",
        "input_focus": "#F8FBFD",
        "border": "#CAD3DC"
    }
}
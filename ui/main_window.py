import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QProgressBar, QFrame, QStackedWidget, QComboBox,
                             QGridLayout, QSizePolicy, QScroller, QSplitter, QTextEdit, QMenu)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QFont, QShortcut, QKeySequence

from config import THEMES
from .widgets import IOSCard, IOSInput, IOSLog, IOSButton, LockToggle

from . import ui_setup
from . import ui_actions
from . import ui_events
from . import ui_utils

MAX_RECENT_FILES = 10

class GalFontTool(QMainWindow):
    IOSInput = IOSInput

    def __init__(self):
        super().__init__()
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.ini")
        self.settings = QSettings(config_path, QSettings.Format.IniFormat)
        self.setWindowTitle("Galgame 字体工具箱")
        self.setMouseTracking(True)
        self.resize(1280, 860)
        self.setMinimumSize(400, 300)
        self.statusBar().showMessage("就绪")
        self.is_max = False

        self.current_theme_name = "简约蓝 (Clean)"
        self.theme = THEMES[self.current_theme_name]
        
        self.generated_font_path = ""
        self.original_font_family = ""
        self.generated_font_family = ""
        
        self.recent_files = []
        self.default_output_dir = ""

        self.bind_methods()
        self.setup_ui()
        self.setup_shortcuts()
        self.setAcceptDrops(True)
        
        self.load_settings()
        self.apply_theme(self.current_theme_name)

        self.log_area.append("欢迎使用 Galgame 字体工具箱")
        self.log_area.append("这是一个全能的游戏字体处理工具，支持字体生成、精简、图片字库制作及更多功能。")
        self.log_area.append("快捷键：Ctrl+O 打开文件 | Ctrl+S 保存预设 | Ctrl+E 导出配置 | F5 刷新字体")
        self.log_area.append("-" * 40)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+O"), self, lambda: ui_utils.browse(self, self.in_src))
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_preset)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, self.do_export_config)
        QShortcut(QKeySequence("Ctrl+E"), self, self.do_export_config)
        QShortcut(QKeySequence("Ctrl+I"), self, self.do_import_config)
        QShortcut(QKeySequence("F5"), self, self.on_source_font_changed)
        QShortcut(QKeySequence("Ctrl+Z"), self, self.do_undo)
        QShortcut(QKeySequence("Ctrl+Y"), self, self.do_redo)
        QShortcut(QKeySequence("Ctrl+Shift+Z"), self, self.do_redo)
        QShortcut(QKeySequence("Ctrl+G"), self, self.do_gen_font)
        QShortcut(QKeySequence("Ctrl+1"), self, lambda: self.switch_tab(0))
        QShortcut(QKeySequence("Ctrl+2"), self, lambda: self.switch_tab(1))
        QShortcut(QKeySequence("Ctrl+3"), self, lambda: self.switch_tab(2))
        QShortcut(QKeySequence("Ctrl+4"), self, lambda: self.switch_tab(3))
        QShortcut(QKeySequence("Ctrl+5"), self, lambda: self.switch_tab(4))
        QShortcut(QKeySequence("Ctrl+H"), self, lambda: self.switch_tab(10))

    def add_to_recent_files(self, file_path):
        if not file_path or not os.path.exists(file_path):
            return
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:MAX_RECENT_FILES]
        self.save_recent_files()

    def save_recent_files(self):
        self.settings.setValue("recent_files", self.recent_files)

    def load_recent_files(self):
        files = self.settings.value("recent_files", [])
        if isinstance(files, list):
            self.recent_files = [f for f in files if os.path.exists(f)]
        else:
            self.recent_files = []

    def show_recent_files_menu(self, button, target_input):
        if not self.recent_files:
            return
        menu = QMenu(self)
        for f in self.recent_files:
            action = menu.addAction(os.path.basename(f))
            action.setToolTip(f)
            action.triggered.connect(lambda checked, path=f: self.open_recent_file(path, target_input))
        menu.addSeparator()
        clear_action = menu.addAction("🗑️ 清空历史")
        clear_action.triggered.connect(self.clear_recent_files)
        menu.exec(button.mapToGlobal(button.rect().bottomLeft()))

    def open_recent_file(self, file_path, target_input):
        if os.path.exists(file_path):
            target_input.setText(file_path)
            self.add_to_recent_files(file_path)
            if target_input == self.in_src:
                self.on_source_font_changed()
            self.log(f"📂 已加载: {os.path.basename(file_path)}")
        else:
            self.log(f"⚠️ 文件不存在: {file_path}")
            if file_path in self.recent_files:
                self.recent_files.remove(file_path)
                self.save_recent_files()

    def clear_recent_files(self):
        self.recent_files = []
        self.save_recent_files()
        self.log("🗑️ 最近文件列表已清空")

    def bind_methods(self):
        self.dragEnterEvent = lambda e: ui_events.dragEnterEvent(self, e)
        self.dropEvent = lambda e: ui_events.dropEvent(self, e)
        self.closeEvent = lambda e: ui_events.closeEvent(self, e)

        self.do_unified_fix = lambda: ui_actions.do_unified_fix(self)
        self.read_unified_metrics = lambda: ui_actions.read_unified_metrics(self)
        self.read_font_metrics = lambda: ui_actions.read_font_metrics(self)
        self.apply_font_metrics = lambda: ui_actions.apply_font_metrics(self)
        self.load_json_to_table = lambda: ui_actions.load_json_to_table(self)
        self.save_table_to_json = lambda: ui_actions.save_table_to_json(self)
        self.add_mapping_row = lambda: ui_actions.add_mapping_row(self)
        self.remove_mapping_row = lambda: ui_actions.remove_mapping_row(self)
        self.do_subset = lambda: ui_actions.do_subset(self)
        self.do_coverage_analysis = lambda: ui_actions.do_coverage_analysis(self)
        self.do_merge_fonts = lambda: ui_actions.do_merge_fonts(self)
        self.do_read_font_info = lambda: ui_actions.do_read_font_info(self)
        self.do_save_font_info = lambda: ui_actions.do_save_font_info(self)
        self.do_compare_fonts = lambda: ui_actions.do_compare_fonts(self)
        self.do_export_diff = lambda: ui_actions.do_export_diff(self)
        self.do_checkup = lambda source: ui_actions.do_checkup(self, source)
        self.do_smart_fallback_scan = lambda: ui_actions.do_smart_fallback_scan(self)
        self.on_smart_scan_done = lambda result: ui_actions.on_smart_scan_done(self, result)
        self.export_smart_result = lambda: ui_actions.export_smart_result(self)
        self.do_gen_woff2 = lambda: ui_actions.do_gen_woff2(self)
        self.do_cleanup = lambda: ui_actions.do_cleanup(self)
        self.do_gen_bmfont = lambda: ui_actions.do_gen_bmfont(self)
        self.do_gen_font = lambda: ui_actions.do_gen_font(self)
        self.do_gen_pic = lambda: ui_actions.do_gen_pic(self)
        self.do_gen_tga = lambda: ui_actions.do_gen_tga(self)
        self.do_gen_bmp = lambda: ui_actions.do_gen_bmp(self)
        self.do_gen_imgfont = lambda: ui_actions.do_gen_imgfont(self)
        self.do_gen_map = lambda: ui_actions.do_gen_map(self)
        self.do_restore_map = lambda: ui_actions.do_restore_map(self)
        self.do_preview_mapping = lambda: ui_actions.do_preview_mapping(self)
        self.do_convert_format = lambda: ui_actions.do_convert_format(self)
        self.do_export_config = lambda: ui_actions.do_export_config(self)
        self.do_import_config = lambda: ui_actions.do_import_config(self)
        self.do_undo = lambda: ui_actions.do_undo(self)
        self.do_redo = lambda: ui_actions.do_redo(self)
        self.show_history_dialog = lambda: ui_actions.show_history_dialog(self)
        self.update_history_buttons = lambda: ui_actions.update_history_buttons(self)

        self.log = lambda m: ui_utils.log(self, m)
        self.browse = lambda target: ui_utils.browse(self, target)
        self.browse_folder = lambda le: ui_utils.browse_folder(self, le)
        self.reset_to_default = lambda: ui_utils.reset_to_default(self)
        self.save_preset = lambda: ui_utils.save_preset(self)
        self.load_preset = lambda: ui_utils.load_preset(self)
        self.run_worker = lambda task, conf: ui_utils.run_worker(self, task, conf)
        self.set_ui_busy = lambda busy: ui_utils.set_ui_busy(self, busy)
        self.on_worker_done = lambda result: ui_utils.on_worker_done(self, result)
        self.toggle_max = lambda: ui_utils.toggle_max(self)
        self.load_settings = lambda: ui_utils.load_settings(self)
        self.load_font_for_preview = lambda path: ui_utils.load_font_for_preview(self, path)
        self.update_previews = lambda: ui_utils.update_previews(self)
        self.on_source_font_changed = lambda: ui_utils.on_source_font_changed(self)
        self.on_mode_change = lambda idx: ui_utils.on_mode_change(self, idx)
        self.create_label = lambda t: ui_utils.create_label(self, t)
        self.create_file_row = lambda inp, btn: ui_utils.create_file_row(self, inp, btn)
        self.apply_theme = lambda name: ui_utils.apply_theme(self, name)
        self.switch_tab = lambda idx: ui_utils.switch_tab(self, idx)
        self.set_help_content = lambda: ui_utils.set_help_content(self)
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        central.setMouseTracking(True)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(10)

        self.title_label = QLabel("Galgame 字体工具箱")
        self.title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self.title_label.setVisible(False)

        content_layout = QVBoxLayout()

        self.left_card = IOSCard()
        left_layout = QVBoxLayout(self.left_card)
        left_layout.setContentsMargins(18, 18, 18, 18)
        left_layout.setSpacing(10)

        self.lbl_theme = self.create_label("界面风格")
        self.lbl_theme.setVisible(False)
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(THEMES.keys())
        self.combo_theme.currentTextChanged.connect(self.apply_theme)
        self.combo_theme.setMinimumHeight(30)
        self.combo_theme.setEnabled(False)
        self.combo_theme.setVisible(False)

        self.btn_reset = QPushButton("↺ 重置")
        self.btn_reset.setMinimumSize(60, 30)
        self.btn_reset.clicked.connect(self.reset_to_default)
        self.btn_reset.setToolTip("清除所有设置并恢复默认值")
        self.btn_save_preset = QPushButton("保存"); self.btn_save_preset.setMinimumSize(48, 30); self.btn_save_preset.clicked.connect(self.save_preset); self.btn_save_preset.setToolTip("保存当前配置为预设")
        self.btn_load_preset = QPushButton("📁"); self.btn_load_preset.setMinimumSize(30, 30); self.btn_load_preset.clicked.connect(self.load_preset); self.btn_load_preset.setToolTip("加载配置预设")

        self.lbl_theme.setText("界面主题：简约蓝")
        self.btn_undo = QPushButton("↩ 撤销"); self.btn_undo.setMinimumHeight(28); self.btn_undo.clicked.connect(self.do_undo); self.btn_undo.setToolTip("撤销上一步文件操作"); self.btn_undo.setEnabled(False)
        self.btn_redo = QPushButton("↪ 重做"); self.btn_redo.setMinimumHeight(28); self.btn_redo.clicked.connect(self.do_redo); self.btn_redo.setToolTip("重做文件操作"); self.btn_redo.setEnabled(False)
        self.btn_history = QPushButton("历史"); self.btn_history.setMinimumHeight(28); self.btn_history.clicked.connect(self.show_history_dialog); self.btn_history.setToolTip("查看文件操作历史记录")

        tools_row = QHBoxLayout()
        tools_row.setSpacing(6)
        tools_row.addWidget(self.btn_save_preset)
        tools_row.addWidget(self.btn_load_preset)
        tools_row.addWidget(self.btn_reset)
        tools_row.addStretch()
        tools_row.addWidget(self.btn_undo)
        tools_row.addWidget(self.btn_redo)
        tools_row.addWidget(self.btn_history)
        left_layout.addLayout(tools_row)

        self.lbl_src = self.create_label("1. 字体资源载入"); left_layout.addWidget(self.lbl_src)
        self.in_src = IOSInput("请拖入或选择字体文件 (.ttf/.otf)", "Font.ttf"); self.in_src.setToolTip("主字体文件路径，支持拖拽"); self.in_src.editingFinished.connect(self.on_source_font_changed)
        self.btn_src = QPushButton("📁"); self.btn_src.setMinimumSize(40, 34)
        self.btn_src_recent = QPushButton("▼"); self.btn_src_recent.setMinimumSize(24, 34); self.btn_src_recent.setToolTip("最近打开的文件")
        self.btn_src_recent.clicked.connect(lambda: self.show_recent_files_menu(self.btn_src_recent, self.in_src))
        self.in_fallback = IOSInput("可选：补全用字体 (如思源黑体.ttf)", ""); self.in_fallback.setToolTip("当主字体缺字时，自动从此字体复制字形补全。")
        self.btn_fallback = QPushButton("📁"); self.btn_fallback.setMinimumSize(40, 34)
        self.in_json = IOSInput("请拖入或选择 .json 码表文件", "custom_map.json"); self.in_json.setToolTip("字符映射表，推荐使用右侧'映射表管理'功能生成")
        self.btn_json = QPushButton("📁"); self.btn_json.setMinimumSize(40, 34)
        
        src_row = QHBoxLayout()
        self.btn_src.clicked.connect(lambda: self.browse(self.in_src))
        src_row.addWidget(self.in_src); src_row.addWidget(self.btn_src); src_row.addWidget(self.btn_src_recent)
        left_layout.addLayout(src_row)
        left_layout.addLayout(self.create_file_row(self.in_fallback, self.btn_fallback))
        left_layout.addLayout(self.create_file_row(self.in_json, self.btn_json))

        left_layout.addSpacing(10)

        self.lbl_font_conf = self.create_label("字体输出设置"); left_layout.addWidget(self.lbl_font_conf)
        f_conf_l = QGridLayout(); f_conf_l.setVerticalSpacing(10); f_conf_l.setColumnMinimumWidth(0, 85)
        self.in_file_name = IOSInput("game.ttf", "game.ttf"); self.in_file_name.setToolTip("生成的文件名，必须以 .ttf 结尾")
        self.in_font_name = IOSInput("My Game Font", "My Game Font"); self.in_font_name.setToolTip("字体内部名称，游戏引擎读取时使用")
        self.in_output_dir = IOSInput("留空则输出到源文件同目录", ""); self.in_output_dir.setToolTip("自定义输出目录，留空则与源字体同目录")
        self.btn_output_dir = QPushButton("📁"); self.btn_output_dir.setMinimumSize(40, 30); self.btn_output_dir.clicked.connect(lambda: self.browse_folder(self.in_output_dir))
        self.combo_mode = QComboBox(); self.combo_mode.addItems(["👉 请选择处理模式...", "✅ 日繁映射: CN -> JP (生成日繁字体)", "🔄 逆向映射: JP -> CN (生成逆向字体)", "🎭 仅修改代码页标识 (不改字形)", "🔀 字形转换: 繁体 -> 简体 (OpenCC)", "🔀 字形转换: 简体 -> 繁体 (OpenCC)"])
        self.combo_mode.setCurrentIndex(0); self.combo_mode.currentIndexChanged.connect(self.on_mode_change); self.combo_mode.setToolTip("通常翻译请选择模式 1，配合生成的映射表使用")
        self.combo_mode.setMinimumHeight(34)
        
        self.combo_charset = QComboBox()
        self.combo_charset.addItems([
            "128 - Shift-JIS (日文)",
            "134 - GB2312 (简体中文)",
            "136 - Big5 (繁体中文)",
            "1 - Default (西欧/通用)",
            "129 - Hangeul (韩文)"
        ])
        self.combo_charset.setToolTip("注入到字体的代码页标识 (ulCodePageRange)。\n游戏引擎通常根据此标志识别字体语言。")
        self.combo_charset.setMinimumHeight(34)
        
        self.chk_lock_file_name = LockToggle(); self.chk_lock_file_name.setObjectName("lockFileToggle"); self.chk_lock_file_name.setToolTip("锁定输出文件名，不随主字体变化")
        self.chk_lock_font_name = LockToggle(); self.chk_lock_font_name.setObjectName("lockFontToggle"); self.chk_lock_font_name.setToolTip("锁定内部字体名，不随主字体变化")
        file_name_row = QHBoxLayout(); file_name_row.setSpacing(8); file_name_row.addWidget(self.in_file_name); file_name_row.addWidget(self.chk_lock_file_name, 0, Qt.AlignmentFlag.AlignVCenter)
        font_name_row = QHBoxLayout(); font_name_row.setSpacing(8); font_name_row.addWidget(self.in_font_name); font_name_row.addWidget(self.chk_lock_font_name, 0, Qt.AlignmentFlag.AlignVCenter)
        f_conf_l.addWidget(QLabel("输出文件名:"), 0, 0); f_conf_l.addLayout(file_name_row, 0, 1)
        f_conf_l.addWidget(QLabel("内部字体名:"), 1, 0); f_conf_l.addLayout(font_name_row, 1, 1)
        out_dir_row = QHBoxLayout(); out_dir_row.addWidget(self.in_output_dir); out_dir_row.addWidget(self.btn_output_dir)
        f_conf_l.addWidget(QLabel("输出目录:"), 2, 0); f_conf_l.addLayout(out_dir_row, 2, 1)
        f_conf_l.addWidget(QLabel("处理模式:"), 3, 0); f_conf_l.addWidget(self.combo_mode, 3, 1)
        f_conf_l.addWidget(QLabel("代码页(Charset):"), 4, 0); f_conf_l.addWidget(self.combo_charset, 4, 1)
        left_layout.addLayout(f_conf_l)
        left_layout.addSpacing(10)

        self.btn_gen_font = IOSButton("生成/处理字体"); self.btn_gen_font.clicked.connect(self.do_gen_font)
        left_layout.addWidget(self.btn_gen_font)

        ui_setup.setup_preview_ui(self, left_layout)

        left_layout.addStretch()

        self.right_card = IOSCard()
        right_layout = QVBoxLayout(self.right_card)
        right_layout.setContentsMargins(20, 20, 20, 20)

        self.tab_container = QWidget()
        tc_layout = QGridLayout(self.tab_container)
        tc_layout.setContentsMargins(5, 5, 5, 5)
        tc_layout.setHorizontalSpacing(8)
        tc_layout.setVerticalSpacing(8)
        
        self.btn_tab_info = QPushButton("字体信息")
        self.btn_tab_mapping = QPushButton("映射表")
        self.btn_tab_analysis = QPushButton("分析对比")
        self.btn_tab_subset = QPushButton("精简瘦身")
        self.btn_tab_merge = QPushButton("合并补字")
        self.btn_tab_imgfont = QPushButton("图片字库")
        self.btn_tab_woff2 = QPushButton("Web转换")
        self.btn_tab_fix = QPushButton("度量修复")
        self.btn_tab_clean = QPushButton("兼容清理")
        self.btn_tab_smart = QPushButton("智能补字")
        self.btn_tab_help = QPushButton("使用帮助")
        
        self.tabs = [self.btn_tab_info, self.btn_tab_mapping, self.btn_tab_analysis,
                     self.btn_tab_subset, self.btn_tab_merge, self.btn_tab_imgfont, 
                     self.btn_tab_woff2, self.btn_tab_fix, self.btn_tab_clean, 
                     self.btn_tab_smart, self.btn_tab_help]

        tab_columns = 5
        for i, b in enumerate(self.tabs):
            row = i // tab_columns
            col = i % tab_columns
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setMinimumHeight(30)
            b.setMinimumWidth(92)
            b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            b.clicked.connect(lambda checked, idx=i: self.switch_tab(idx))
            tc_layout.addWidget(b, row, col)
        for col in range(tab_columns):
            tc_layout.setColumnStretch(col, 1)
        self.tab_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.tab_container.setMinimumHeight(112)
        right_layout.addWidget(self.tab_container)

        self.stack = QStackedWidget()
        
        p_info = QWidget(); ui_setup.setup_info_ui(self, p_info)
        p_mapping = QWidget(); ui_setup.setup_mapping_manager_ui(self, p_mapping)
        p_analysis = QWidget(); ui_setup.setup_font_analysis_ui(self, p_analysis)
        p_subset = QWidget(); ui_setup.setup_subset_ui(self, p_subset)
        p_merge = QWidget(); ui_setup.setup_merge_ui(self, p_merge)
        p_imgfont = QWidget(); ui_setup.setup_image_font_ui(self, p_imgfont)
        p_woff2 = QWidget(); ui_setup.setup_woff2_ui(self, p_woff2)
        p_fix = QWidget(); ui_setup.setup_unified_fix_ui(self, p_fix)
        p_clean = QWidget(); ui_setup.setup_cleanup_ui(self, p_clean)
        p_smart = QWidget(); ui_setup.setup_smart_fallback_ui(self, p_smart)
        
        p_help = QWidget(); l_help = QVBoxLayout(p_help)
        self.help_browser = QTextEdit(); self.help_browser.setReadOnly(True)
        self.set_help_content(); l_help.addWidget(self.help_browser)

        self.stack.addWidget(p_info); self.stack.addWidget(p_mapping); self.stack.addWidget(p_analysis)
        self.stack.addWidget(p_subset); self.stack.addWidget(p_merge); self.stack.addWidget(p_imgfont)
        self.stack.addWidget(p_woff2); self.stack.addWidget(p_fix); self.stack.addWidget(p_clean)
        self.stack.addWidget(p_smart); self.stack.addWidget(p_help)
        
        splitter = QSplitter(Qt.Orientation.Vertical); splitter.setChildrenCollapsible(False)
        splitter.addWidget(self.stack)

        self.log_area = IOSLog()
        self.log_area.setMinimumHeight(110)
        QScroller.grabGesture(self.log_area.viewport(), QScroller.ScrollerGestureType.LeftMouseButtonGesture)
        splitter.addWidget(self.log_area)
        splitter.setStretchFactor(0, 8); splitter.setStretchFactor(1, 2)
        splitter.setSizes([1000, 150])
        right_layout.addWidget(splitter)

        self.progress = QProgressBar(); self.progress.setMinimumHeight(6); self.progress.setTextVisible(False)
        right_layout.addWidget(self.progress)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.setHandleWidth(8)
        self.main_splitter.addWidget(self.left_card)
        self.main_splitter.addWidget(self.right_card)
        self.main_splitter.setStretchFactor(0, 1)
        self.main_splitter.setStretchFactor(1, 1)
        self.main_splitter.setSizes([640, 640])
        content_layout.addWidget(self.main_splitter)
        main_layout.addLayout(content_layout)
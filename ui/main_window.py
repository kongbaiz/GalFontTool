import os
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QProgressBar,
    QFrame,
    QComboBox,
    QFormLayout,
    QScroller,
    QSplitter,
    QMenu,
    QCheckBox,
    QStackedWidget,
    QGridLayout,
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont, QShortcut, QKeySequence

from .widgets import IOSCard, IOSInput, IOSLog, IOSButton
from . import ui_setup
from . import ui_actions
from . import ui_events
from . import ui_utils

MAX_RECENT_FILES = 10
TAB_DEFINITIONS = [
    ("btn_tab_info", "字体信息", ui_setup.setup_info_ui),
    ("btn_tab_mapping", "映射表", ui_setup.setup_mapping_manager_ui),
    ("btn_tab_analysis", "分析对比", ui_setup.setup_font_analysis_ui),
    ("btn_tab_subset", "精简瘦身", ui_setup.setup_subset_ui),
    ("btn_tab_merge", "合并补字", ui_setup.setup_merge_ui),
    ("btn_tab_imgfont", "图片字库", ui_setup.setup_image_font_ui),
    ("btn_tab_woff2", "Web 转换", ui_setup.setup_woff2_ui),
    ("btn_tab_fix", "度量修复", ui_setup.setup_unified_fix_ui),
    ("btn_tab_clean", "兼容清理", ui_setup.setup_cleanup_ui),
    ("btn_tab_smart", "智能补字", ui_setup.setup_smart_fallback_ui),
]


class GalFontTool(QMainWindow):
    IOSInput = IOSInput

    def __init__(self):
        super().__init__()
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.ini"
        )
        self.settings = QSettings(config_path, QSettings.Format.IniFormat)

        self.setWindowTitle("Galgame 字体工具箱")
        self.resize(1350, 900)
        self.setMinimumSize(820, 620)
        self.setAcceptDrops(True)

        self.generated_font_path = ""
        self.original_font_family = ""
        self.generated_font_family = ""
        self.recent_files = []
        self.default_output_dir = ""

        self.bind_methods()
        self.setup_ui()
        self.setup_shortcuts()
        self.load_settings()

        self.log_area.setHtml(
            """
            <h3>欢迎使用 Galgame 字体工具箱</h3>
            <p>支持字体生成、映射处理、精简、补字、图片字库和兼容清理等常用流程。</p>
            <p style='color:#666;'>快捷键：Ctrl+O 打开字体 | Ctrl+S 保存预设 | Ctrl+E 导出配置 | F5 刷新预览</p>
            <hr>
            """
        )

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
        self.load_settings = lambda: ui_utils.load_settings(self)
        self.load_font_for_preview = lambda path: ui_utils.load_font_for_preview(self, path)
        self.update_previews = lambda: ui_utils.update_previews(self)
        self.on_source_font_changed = lambda: ui_utils.on_source_font_changed(self)
        self.on_mode_change = lambda idx: ui_utils.on_mode_change(self, idx)
        self.create_label = lambda t: ui_utils.create_label(self, t)
        self.create_file_row = lambda inp, btn: ui_utils.create_file_row(self, inp, btn)
        self.switch_tab = lambda idx: ui_utils.switch_tab(self, idx)

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

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        header_layout = QHBoxLayout()
        self.title_label = QLabel("Galgame 字体工具箱")
        self.title_label.setFont(QFont("Microsoft YaHei", 13, QFont.Weight.Bold))
        self.header_hint = QLabel("原生布局，聚焦常用流程")
        self.header_hint.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.header_hint)
        main_layout.addLayout(header_layout)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)
        content_layout.addWidget(self._build_sidebar(), 38)
        content_layout.addWidget(self._build_workspace(), 62)
        main_layout.addLayout(content_layout)

    def _build_sidebar(self):
        self.left_card = IOSCard()
        layout = QVBoxLayout(self.left_card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addLayout(self._build_preset_actions())
        layout.addLayout(self._build_history_actions())

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(divider)

        self.lbl_src = self.create_label("字体资源")
        layout.addWidget(self.lbl_src)
        layout.addLayout(self._build_source_section())

        self.lbl_font_conf = self.create_label("输出设置")
        layout.addWidget(self.lbl_font_conf)
        layout.addLayout(self._build_output_section())

        self.btn_gen_font = IOSButton("生成 / 处理字体")
        self.btn_gen_font.clicked.connect(self.do_gen_font)
        layout.addWidget(self.btn_gen_font)

        ui_setup.setup_preview_ui(self, layout)

        layout.addStretch()
        self.lbl_status = QLabel("就绪")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_status)
        return self.left_card

    def _build_workspace(self):
        self.right_card = IOSCard()
        layout = QVBoxLayout(self.right_card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        layout.addWidget(self._build_tab_bar())

        self.stack = QStackedWidget()
        self._populate_pages()

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self.stack)

        self.log_area = IOSLog()
        QScroller.grabGesture(
            self.log_area.viewport(), QScroller.ScrollerGestureType.LeftMouseButtonGesture
        )
        splitter.addWidget(self.log_area)
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)
        layout.addWidget(splitter)

        self.progress = QProgressBar()
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)
        return self.right_card

    def _build_preset_actions(self):
        layout = QHBoxLayout()
        layout.setSpacing(8)
        layout.addStretch()

        self.btn_save_preset = QPushButton("保存预设")
        self.btn_save_preset.clicked.connect(self.save_preset)
        self.btn_load_preset = QPushButton("加载预设")
        self.btn_load_preset.clicked.connect(self.load_preset)
        self.btn_reset = QPushButton("重置")
        self.btn_reset.clicked.connect(self.reset_to_default)

        for button in (self.btn_save_preset, self.btn_load_preset, self.btn_reset):
            button.setMinimumHeight(30)
            layout.addWidget(button)
        return layout

    def _build_history_actions(self):
        layout = QHBoxLayout()
        layout.setSpacing(8)

        self.btn_undo = QPushButton("撤销")
        self.btn_undo.clicked.connect(self.do_undo)
        self.btn_undo.setEnabled(False)
        self.btn_redo = QPushButton("重做")
        self.btn_redo.clicked.connect(self.do_redo)
        self.btn_redo.setEnabled(False)
        self.btn_history = QPushButton("历史记录")
        self.btn_history.clicked.connect(self.show_history_dialog)

        for button in (self.btn_undo, self.btn_redo, self.btn_history):
            button.setMinimumHeight(28)
            layout.addWidget(button)
        return layout

    def _build_source_section(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)

        self.in_src = IOSInput("选择主字体文件 (.ttf/.otf)", "Font.ttf")
        self.in_src.editingFinished.connect(self.on_source_font_changed)
        self.btn_src = self._create_browse_button()
        self.btn_src_recent = self._create_browse_button("最近", 54)
        self.btn_src_recent.clicked.connect(
            lambda: self.show_recent_files_menu(self.btn_src_recent, self.in_src)
        )
        self.btn_src.clicked.connect(lambda: self.browse(self.in_src))
        layout.addLayout(
            self._compose_input_row(self.in_src, self.btn_src, self.btn_src_recent)
        )

        self.in_fallback = IOSInput("可选：补全字体", "")
        self.btn_fallback = self._create_browse_button()
        layout.addLayout(self.create_file_row(self.in_fallback, self.btn_fallback))

        self.in_json = IOSInput("选择 .json 映射文件", "custom_map.json")
        self.btn_json = self._create_browse_button()
        layout.addLayout(self.create_file_row(self.in_json, self.btn_json))
        return layout

    def _build_output_section(self):
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(10)

        self.in_file_name = IOSInput("game.ttf", "game.ttf")
        self.chk_lock_file_name = QCheckBox("锁定")
        form.addRow("输出文件名", self._wrap_row(self.in_file_name, self.chk_lock_file_name))

        self.in_font_name = IOSInput("My Game Font", "My Game Font")
        self.chk_lock_font_name = QCheckBox("锁定")
        form.addRow("内部字体名", self._wrap_row(self.in_font_name, self.chk_lock_font_name))

        self.in_output_dir = IOSInput("留空则输出到源文件同目录", "")
        self.btn_output_dir = self._create_browse_button()
        self.btn_output_dir.clicked.connect(lambda: self.browse_folder(self.in_output_dir))
        form.addRow("输出目录", self._wrap_row(self.in_output_dir, self.btn_output_dir))

        self.combo_mode = QComboBox()
        self.combo_mode.addItems(
            [
                "请选择处理模式...",
                "日繁映射: CN -> JP",
                "逆向映射: JP -> CN",
                "仅修改代码页标识",
                "字形转换: 繁体 -> 简体 (OpenCC)",
                "字形转换: 简体 -> 繁体 (OpenCC)",
            ]
        )
        self.combo_mode.setCurrentIndex(0)
        self.combo_mode.currentIndexChanged.connect(self.on_mode_change)
        self.combo_mode.setMinimumHeight(38)
        form.addRow("处理模式", self.combo_mode)

        self.combo_charset = QComboBox()
        self.combo_charset.addItems(
            [
                "128 - Shift-JIS",
                "134 - GB2312",
                "136 - Big5",
                "1 - Default",
                "129 - Hangeul",
            ]
        )
        self.combo_charset.setMinimumHeight(38)
        form.addRow("代码页", self.combo_charset)
        return form

    def _build_tab_bar(self):
        self.tab_container = QWidget()
        tab_layout = QGridLayout(self.tab_container)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(8)

        self.tabs = []
        for index, (attr_name, title, _) in enumerate(TAB_DEFINITIONS):
            button = QPushButton(title)
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setMinimumHeight(32)
            button.clicked.connect(lambda checked, idx=index: self.switch_tab(idx))
            setattr(self, attr_name, button)
            self.tabs.append(button)
            tab_layout.addWidget(button, index // 5, index % 5)

        for col in range(5):
            tab_layout.setColumnStretch(col, 1)
        return self.tab_container

    def _populate_pages(self):
        for _, _, setup_fn in TAB_DEFINITIONS:
            page = QWidget()
            setup_fn(self, page)
            self.stack.addWidget(page)
        self.switch_tab(0)

    def _create_browse_button(self, text="浏览", width=52):
        button = QPushButton(text)
        button.setFixedSize(width, 38)
        return button

    def _compose_input_row(self, *widgets):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        for widget in widgets:
            layout.addWidget(widget)
        return layout

    def _wrap_row(self, *widgets):
        container = QWidget()
        container.setLayout(self._compose_input_row(*widgets))
        return container

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
        for path in self.recent_files:
            action = menu.addAction(os.path.basename(path))
            action.setToolTip(path)
            action.triggered.connect(
                lambda checked, file_path=path: self.open_recent_file(file_path, target_input)
            )

        menu.addSeparator()
        menu.addAction("清空最近文件", self.clear_recent_files)
        menu.exec(button.mapToGlobal(button.rect().bottomLeft()))

    def open_recent_file(self, file_path, target_input):
        if not os.path.exists(file_path):
            self.log(f"文件不存在: {file_path}")
            if file_path in self.recent_files:
                self.recent_files.remove(file_path)
                self.save_recent_files()
            return

        target_input.setText(file_path)
        self.add_to_recent_files(file_path)
        if target_input == self.in_src:
            self.on_source_font_changed()
        self.log(f"已加载: {os.path.basename(file_path)}")

    def clear_recent_files(self):
        self.recent_files = []
        self.save_recent_files()
        self.log("最近文件列表已清空")

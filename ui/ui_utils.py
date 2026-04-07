import os
import json
from PySide6.QtWidgets import QFileDialog, QMessageBox, QLabel, QHBoxLayout, QPushButton, QComboBox, QTextEdit, QTableWidget
from PySide6.QtGui import QFont, QFontDatabase
from config import THEMES
from core.worker import Worker

def log(main_window, m):
    main_window.log_area.append(m)
    main_window.log_area.verticalScrollBar().setValue(main_window.log_area.verticalScrollBar().maximum())

def browse(main_window, target):
    if target == main_window.map_src or target == main_window.sub_txt or target == main_window.sf_txt or target == main_window.sf_lib:
        d = QFileDialog.getExistingDirectory(main_window, "选择目录")
        if d: target.setText(d)
    else:
        f, _ = QFileDialog.getOpenFileName(main_window, "选择文件", "", "Font/JSON (*.ttf *.otf *.json);;All (*.*)")
        if f:
            target.setText(f)
            if hasattr(main_window, 'add_to_recent_files') and f.lower().endswith(('.ttf', '.otf')):
                main_window.add_to_recent_files(f)

def browse_folder(main_window, line_edit):
    d = QFileDialog.getExistingDirectory(main_window, "选择目录", "")
    if d:
        line_edit.setText(d)

def reset_to_default(main_window):
    reply = QMessageBox.question(main_window, '确认重置', '确定要清除所有设置并恢复默认值吗？', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    if reply == QMessageBox.StandardButton.Yes:
        main_window.settings.clear()
        main_window.in_src.setText("Font.ttf")
        main_window.in_fallback.setText("")
        main_window.in_json.setText("custom_map.json")
        main_window.in_file_name.setText("game.ttf")
        main_window.in_font_name.setText("My Game Font")
        main_window.combo_mode.setCurrentIndex(0)
        main_window.combo_charset.setCurrentIndex(0)
        main_window.apply_theme("简约蓝 (Clean)")
        main_window.log_area.clear()
        main_window.log_area.append("✅ 已恢复默认设置。")

def save_preset(main_window):
    preset = {
        'src': main_window.in_src.text(), 'fallback': main_window.in_fallback.text(), 'json': main_window.in_json.text(),
        'file_name': main_window.in_file_name.text(), 'font_name': main_window.in_font_name.text(),
        'mode': main_window.combo_mode.currentIndex(), 'charset': main_window.combo_charset.currentIndex(),
        'theme': main_window.current_theme_name,
        'map_src': main_window.map_src.text(), 'map_out': main_window.map_out.text(), 'map_json': main_window.map_json.text(),
        'map_ext': main_window.map_ext.text(), 'sub_font': main_window.sub_font.text(), 'sub_txt': main_window.sub_txt.text(),
        'sub_json': main_window.sub_json.text(), 'sub_out': main_window.sub_out.text(),
        'pic_font': main_window.pic_font.text(), 'pic_folder': main_window.pic_folder.text(),
        'tga_font': main_window.tga_font.text(), 'bmp_font': main_window.bmp_font.text(),
    }
    save_path, _ = QFileDialog.getSaveFileName(main_window, "保存预设", "my_preset.json", "JSON (*.json)")
    if save_path:
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(preset, f, ensure_ascii=False, indent=2)
            main_window.log(f"💾 预设已保存: {os.path.basename(save_path)}")
            QMessageBox.information(main_window, "保存成功", f"配置预设已保存到：\n{save_path}")
        except Exception as e:
            main_window.log(f"❌ 保存预设失败: {e}")

def load_preset(main_window):
    load_path, _ = QFileDialog.getOpenFileName(main_window, "加载预设", "", "JSON (*.json)")
    if not load_path: return
    try:
        with open(load_path, 'r', encoding='utf-8') as f:
            preset = json.load(f)

        if 'src' in preset: main_window.in_src.setText(preset['src'])
        if 'fallback' in preset: main_window.in_fallback.setText(preset['fallback'])
        if 'json' in preset: main_window.in_json.setText(preset['json'])
        if 'file_name' in preset: main_window.in_file_name.setText(preset['file_name'])
        if 'font_name' in preset: main_window.in_font_name.setText(preset['font_name'])
        if 'mode' in preset: main_window.combo_mode.setCurrentIndex(preset['mode'])
        if 'charset' in preset: main_window.combo_charset.setCurrentIndex(preset['charset'])
        if 'theme' in preset:
            idx = main_window.combo_theme.findText(preset['theme'])
            if idx >= 0: main_window.combo_theme.setCurrentIndex(idx)
        if 'map_src' in preset: main_window.map_src.setText(preset['map_src'])
        if 'map_out' in preset: main_window.map_out.setText(preset['map_out'])
        if 'map_json' in preset: main_window.map_json.setText(preset['map_json'])
        if 'map_ext' in preset: main_window.map_ext.setText(preset['map_ext'])
        if 'sub_font' in preset: main_window.sub_font.setText(preset['sub_font'])
        if 'sub_txt' in preset: main_window.sub_txt.setText(preset['sub_txt'])
        if 'sub_json' in preset: main_window.sub_json.setText(preset['sub_json'])
        if 'sub_out' in preset: main_window.sub_out.setText(preset['sub_out'])
        if 'pic_font' in preset: main_window.pic_font.setText(preset['pic_font'])
        if 'pic_folder' in preset: main_window.pic_folder.setText(preset['pic_folder'])
        if 'tga_font' in preset: main_window.tga_font.setText(preset['tga_font'])
        if 'bmp_font' in preset: main_window.bmp_font.setText(preset['bmp_font'])

        main_window.log(f"📂 预设已加载: {os.path.basename(load_path)}")
        QMessageBox.information(main_window, "加载成功", f"已从预设恢复配置：\n{os.path.basename(load_path)}")

    except Exception as e:
        main_window.log(f"❌ 加载预设失败: {e}")
        QMessageBox.warning(main_window, "加载失败", f"无法加载预设：\n{e}")

def run_worker(main_window, task, conf):
    main_window.set_ui_busy(True)
    main_window.worker = Worker(task, conf)
    main_window.worker.log.connect(main_window.log)
    main_window.worker.prog.connect(main_window.progress.setValue)
    main_window.worker.done.connect(main_window.on_worker_done)
    main_window.worker.finished.connect(lambda: main_window.set_ui_busy(False))
    main_window.worker.start()

def set_ui_busy(main_window, busy):
    main_window.left_card.setEnabled(not busy)
    main_window.right_card.setEnabled(not busy)
    main_window.progress.setValue(0 if busy else 100)
    main_window.statusBar().showMessage("正在处理..." if busy else "就绪")

def on_worker_done(main_window, result):
    if result and isinstance(result, str):
        if result.endswith('.ttf'):
            main_window.generated_font_path = result
            main_window.pic_font.setText(result)
            main_window.tga_font.setText(result)
            main_window.bmp_font.setText(result)
            main_window.statusBar().showMessage("字体已就绪")
            family = main_window.load_font_for_preview(result)
            if family:
                main_window.generated_font_family = family
                main_window.update_previews()
        elif result.endswith('.json'):
            main_window.in_json.setText(result)
            main_window.statusBar().showMessage("映射表就绪")
    
    if hasattr(main_window, 'update_history_buttons'):
        main_window.update_history_buttons()

def toggle_max(main_window):
    if main_window.is_max:
        main_window.showNormal()
        main_window.is_max = False
    else:
        main_window.showMaximized()
        main_window.is_max = True

def load_settings(main_window):
    main_window.in_src.setText(main_window.settings.value("in_src", "Font.ttf"))
    main_window.in_fallback.setText(main_window.settings.value("in_fallback", ""))
    main_window.in_json.setText(main_window.settings.value("in_json", "custom_map.json"))
    main_window.in_file_name.setText(main_window.settings.value("in_file_name", "game.ttf"))
    main_window.in_font_name.setText(main_window.settings.value("in_font_name", "My Game Font"))
    main_window.chk_lock_file_name.setChecked(main_window.settings.value("lock_file_name", False) == "true" or main_window.settings.value("lock_file_name", False) is True)
    main_window.chk_lock_font_name.setChecked(main_window.settings.value("lock_font_name", False) == "true" or main_window.settings.value("lock_font_name", False) is True)
    if hasattr(main_window, 'in_output_dir'):
        main_window.in_output_dir.setText(main_window.settings.value("output_dir", ""))
    main_window.combo_mode.setCurrentIndex(int(main_window.settings.value("mode", 0)))
    main_window.combo_charset.setCurrentIndex(int(main_window.settings.value("charset", 0)))
    main_window.current_theme_name = main_window.settings.value("theme", "简约蓝 (Clean)")
    idx = main_window.combo_theme.findText(main_window.current_theme_name)
    if idx >= 0: main_window.combo_theme.setCurrentIndex(idx)
    if hasattr(main_window, 'load_recent_files'):
        main_window.load_recent_files()
    main_window.on_source_font_changed()
    if hasattr(main_window, 'update_history_buttons'):
        main_window.update_history_buttons()

def load_font_for_preview(main_window, font_path):
    if not os.path.exists(font_path):
        return None
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id == -1:
        main_window.log(f"⚠️ 预览加载失败: {os.path.basename(font_path)}")
        return None
    family = QFontDatabase.applicationFontFamilies(font_id)[0]
    main_window.log(f"🔎 预览已加载: {family}")
    return family

def update_previews(main_window):
    preview_text = main_window.preview_input.text()
    if not preview_text:
        preview_text = main_window.preview_input.placeholderText()
    main_window.preview_area.setText(preview_text)
    family_to_use = main_window.generated_font_family if main_window.generated_font_family else main_window.original_font_family
    if family_to_use:
        font = QFont(family_to_use, 16)
        main_window.preview_area.setFont(font)
        main_window.preview_area.setToolTip(f"当前预览: {family_to_use}")
    else:
        main_window.preview_area.setToolTip("当前使用系统默认字体")

def on_source_font_changed(main_window):
    src_font_path = main_window.in_src.text()
    family = main_window.load_font_for_preview(src_font_path)
    if family:
        main_window.original_font_family = family
        if not main_window.generated_font_family:
            main_window.update_previews()
    
    if os.path.exists(src_font_path):
        base_name = os.path.splitext(os.path.basename(src_font_path))[0]
        
        lock_file = main_window.chk_lock_file_name.isChecked()
        lock_font = main_window.chk_lock_font_name.isChecked()
        
        if not lock_file:
            main_window.in_file_name.setText(f"{base_name}_out.ttf")
        if not lock_font:
            main_window.in_font_name.setText(f"{base_name} Custom")
        if hasattr(main_window, 'add_to_recent_files'):
            main_window.add_to_recent_files(src_font_path)

def on_mode_change(main_window, index):
    need_json = index in [1, 2]
    main_window.in_json.setEnabled(need_json)
    main_window.btn_json.setEnabled(need_json)

def create_label(main_window, t): return QLabel(t)

def create_file_row(main_window, inp, btn):
    l = QHBoxLayout()
    btn.clicked.connect(lambda: main_window.browse(inp))
    l.addWidget(inp)
    l.addWidget(btn)
    return l

def clear_widget_styles(main_window):
    if hasattr(main_window, 'centralWidget') and main_window.centralWidget():
        main_window.centralWidget().setStyleSheet("")


def get_scrollbar_style():
    return (
        "QScrollBar:vertical { background: transparent; width: 10px; margin: 2px 1px 2px 1px; }"
        "QScrollBar::handle:vertical { background: #AEBBC7; min-height: 26px; border-radius: 5px; }"
        "QScrollBar::handle:vertical:hover { background: #93A4B3; }"
        "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }"
        "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }"
        "QScrollBar:horizontal { background: transparent; height: 10px; margin: 1px 2px 1px 2px; }"
        "QScrollBar::handle:horizontal { background: #AEBBC7; min-width: 26px; border-radius: 5px; }"
        "QScrollBar::handle:horizontal:hover { background: #93A4B3; }"
        "QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }"
        "QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: transparent; }"
    )

def apply_theme(main_window, theme_name):
    if theme_name in THEMES:
        main_window.current_theme_name = theme_name
        main_window.theme = THEMES[theme_name]
    t = main_window.theme

    clear_widget_styles(main_window)

    if main_window.centralWidget():
        main_window.centralWidget().setStyleSheet(
            "QWidget { background-color: #E9EEF2; color: #2B3844; }"
        )

    sb_style = get_scrollbar_style()

    if hasattr(main_window, 'left_card'):
        main_window.left_card.update_theme(t['card_bg'], t['border'])
    if hasattr(main_window, 'right_card'):
        main_window.right_card.update_theme(t['card_bg'], t['border'])

    for i in main_window.findChildren(main_window.IOSInput):
        i.update_theme(t['input_bg'], t['input_focus'], t['accent'], t['text_main'])

    label_style = "color: #33424F; background: transparent; border: none;"
    for lbl in main_window.findChildren(QLabel):
        lbl.setStyleSheet(label_style)

    button_style = (
        "QPushButton {"
        "background-color: #F6F8FA;"
        "color: #2D3A46;"
        "border: 1px solid #C9D2DB;"
        "border-radius: 5px;"
        "padding: 5px 10px;"
        "}"
        "QPushButton:hover { background-color: #EEF2F5; }"
        "QPushButton:pressed { background-color: #E6ECF1; }"
        "QPushButton:disabled { color: #8B949E; background-color: #F2F5F7; border-color: #D9E0E6; }"
    )
    for btn in main_window.findChildren(QPushButton):
        if btn in getattr(main_window, 'tabs', []):
            continue
        if isinstance(btn, main_window.__class__.IOSInput):
            continue
        btn.setStyleSheet(button_style)

    combo_style = (
        "QComboBox {"
        "background-color: #FFFFFF;"
        "color: #2E3B47;"
        "border: 1px solid #C9D2DB;"
        "border-radius: 5px;"
        "padding: 3px 8px;"
        "}"
        "QComboBox:focus { border-color: #6C7F90; background-color: #F8FBFD; }"
        "QComboBox::drop-down { border: none; width: 24px; }"
        "QComboBox QAbstractItemView { border: 1px solid #C9D2DB; background: #FFFFFF; selection-background-color: #EAF1F6; selection-color: #23303C; }"
        f"{sb_style}"
    )
    for combo in main_window.findChildren(QComboBox):
        combo.setStyleSheet(combo_style)

    from PySide6.QtWidgets import QStyleFactory
    native_style = QStyleFactory.create("windowsvista") or QStyleFactory.create("windows")
    for chk_name in ('chk_lock_file_name', 'chk_lock_font_name'):
        chk = getattr(main_window, chk_name, None)
        if chk:
            if native_style:
                chk.setProperty("_native_style", native_style)
                chk.setStyle(native_style)
            chk.setStyleSheet("")

    text_style = (
        "QTextEdit {"
        "background-color: #FFFFFF;"
        "color: #2E3B47;"
        "border: 1px solid #D8E0E7;"
        "border-radius: 5px;"
        "}"
        f"{sb_style}"
    )
    for te in main_window.findChildren(QTextEdit):
        te.setStyleSheet(text_style)
    for table in main_window.findChildren(QTableWidget):
        table.setStyleSheet(
            "QTableWidget { background-color: #FFFFFF; border: 1px solid #D8E0E7; gridline-color: #E8EDF2; selection-background-color: #EAF1F6; selection-color: #23303C; }"
            "QHeaderView::section { background-color: #F7F9FB; color: #33424F; border: none; border-bottom: 1px solid #E0E6EC; padding: 5px; }"
            f"{sb_style}"
        )

    for b in [
        getattr(main_window, 'btn_gen_font', None),
        getattr(main_window, 'btn_run_map', None),
        getattr(main_window, 'btn_checkup_map', None),
        getattr(main_window, 'btn_preview_map', None),
        getattr(main_window, 'btn_restore_map', None),
        getattr(main_window, 'btn_run_subset', None),
        getattr(main_window, 'btn_checkup_subset', None),
        getattr(main_window, 'btn_run_merge', None),
        getattr(main_window, 'btn_run_compare', None),
        getattr(main_window, 'btn_export_diff', None),
        getattr(main_window, 'btn_run_coverage', None),
        getattr(main_window, 'btn_run_imgfont', None),
        getattr(main_window, 'btn_run_woff2', None),
        getattr(main_window, 'btn_run_clean', None),
        getattr(main_window, 'btn_do_fix', None),
        getattr(main_window, 'btn_read_info', None),
        getattr(main_window, 'btn_save_info', None),
        getattr(main_window, 'btn_run_smart', None),
    ]:
        if b:
            b.set_theme_color(t['accent'])

    main_window.progress.setStyleSheet(
        "QProgressBar { background-color: #E8EDF1; border: 1px solid #D0D8E0; border-radius: 3px; }"
        f"QProgressBar::chunk {{ background-color: {t['accent']}; border-radius: 2px; }}"
    )
    main_window.log_area.update_theme(t['text_main'], "#FCFDFE", sb_style)
    main_window.statusBar().setStyleSheet(
        "QStatusBar { background-color: #F5F8FA; color: #42505D; border-top: 1px solid #D7DFE6; }"
    )
    main_window.switch_tab(main_window.stack.currentIndex())

def switch_tab(main_window, idx):
    main_window.stack.setCurrentIndex(idx)
    for i, b in enumerate(main_window.tabs):
        b.setChecked(i == idx)
        if i == idx:
            b.setStyleSheet(
                "QPushButton { background-color: #DEE8F0; color: #1F2D3A; border: 1px solid #B7C5D3; border-radius: 5px; padding: 5px 8px; font-weight: bold; }"
            )
        else:
            b.setStyleSheet(
                "QPushButton { background-color: #F6F8FA; color: #3A4855; border: 1px solid #CAD3DC; border-radius: 5px; padding: 5px 8px; }"
                "QPushButton:hover { background-color: #EEF2F5; }"
            )
    if hasattr(main_window, 'quick_nav') and main_window.quick_nav.currentIndex() != idx:
        main_window.quick_nav.blockSignals(True)
        main_window.quick_nav.setCurrentIndex(idx)
        main_window.quick_nav.blockSignals(False)

def set_help_content(main_window):
    text = """Galgame 字体工具箱 使用指南

快速入门
1. 在映射表功能中扫描文本目录。
2. 生成字符映射表 JSON。
3. 在主界面选择处理模式并生成字体。

常用快捷键
- Ctrl+O: 打开主字体文件
- Ctrl+S: 保存预设
- Ctrl+E: 导出配置
- Ctrl+I: 导入配置
- Ctrl+Z / Ctrl+Y: 撤销与重做
- Ctrl+G: 一键生成字体
- F5: 刷新

提示
- 大多数路径输入框支持拖拽文件或文件夹。
- 建议先确认映射表再执行批量生成。
"""
    main_window.help_browser.setPlainText(text)
import os
import json
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QLabel, QHBoxLayout, QPushButton
from PyQt6.QtGui import QColor, QFont, QFontDatabase
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
        main_window.apply_theme("🌊 深海 (Ocean)")
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
    main_window.lbl_status.setText("正在处理..." if busy else "就绪")

def on_worker_done(main_window, result):
    if result and isinstance(result, str):
        if result.endswith('.ttf'):
            main_window.generated_font_path = result
            main_window.pic_font.setText(result)
            main_window.tga_font.setText(result)
            main_window.bmp_font.setText(result)
            main_window.lbl_status.setText("字体已就绪")
            family = main_window.load_font_for_preview(result)
            if family:
                main_window.generated_font_family = family
                main_window.update_previews()
        elif result.endswith('.json'):
            main_window.in_json.setText(result)
            main_window.lbl_status.setText("映射表就绪")
    
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
    main_window.current_theme_name = main_window.settings.value("theme", "🌊 深海 (Ocean)")
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

def get_scrollbar_style(main_window, accent):
    return f"""
        QScrollBar:vertical {{ border: none; background: rgba(0, 0, 0, 0.05); width: 8px; margin: 0px; border-radius: 4px; }}
        QScrollBar::handle:vertical {{ background: {accent}; min-height: 20px; border-radius: 4px; }}
        QScrollBar::handle:vertical:hover {{ background: {QColor(accent).darker(110).name()}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
        QScrollBar:horizontal {{ border: none; background: rgba(0, 0, 0, 0.05); height: 8px; margin: 0px; border-radius: 4px; }}
        QScrollBar::handle:horizontal {{ background: {accent}; min-width: 20px; border-radius: 4px; }}
        QScrollBar::handle:horizontal:hover {{ background: {QColor(accent).darker(110).name()}; }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; }}
    """

def apply_theme(main_window, theme_name):
    if theme_name not in THEMES: return
    main_window.current_theme_name = theme_name
    main_window.theme = THEMES[theme_name]
    t = main_window.theme
    main_window.update()

    labels_to_color = [
        main_window.title_label,
        main_window.lbl_map, main_window.lbl_ed, main_window.lbl_sub,
        main_window.lbl_cov, main_window.lbl_merge, main_window.lbl_info, main_window.lbl_cmp,
        getattr(main_window, 'lbl_sf', None), getattr(main_window, 'lbl_woff2', None),
        getattr(main_window, 'lbl_clean', None), getattr(main_window, 'lbl_imgfont', None),
        getattr(main_window, 'lbl_fix', None), getattr(main_window, 'lbl_conv', None)
    ]

    for l in labels_to_color:
        if l: 
            try:
                l.setStyleSheet(f"color: {t['text_main']}; padding-left: 5px;")
            except RuntimeError:
                pass

    for l in [main_window.lbl_theme, main_window.lbl_src, main_window.lbl_font_conf, main_window.lbl_status]: l.setStyleSheet(f"color: {t['text_dim']}; font-weight:bold; font-size:12px; font-family:'Microsoft YaHei';")

    if hasattr(main_window, 'preview_labels'):
        for label in main_window.preview_labels:
            label.setStyleSheet(f"color: {t['text_dim']}; font-family:'Microsoft YaHei'; font-weight:bold; font-size:12px;")

    for btn in [main_window.btn_min, main_window.btn_max, main_window.btn_close]: btn.update_icon_color(t['text_main'])

    main_window.left_card.update_theme(t['card_bg'], t['border'])
    main_window.right_card.update_theme(t['card_bg'], t['border'])

    all_inputs = main_window.findChildren(main_window.IOSInput)
    for i in all_inputs: i.update_theme(t['input_bg'], t['input_focus'], t['accent'], t['text_main'])

    folder_btn_style = f"""
        QPushButton {{
            background-color: {t['input_bg']};
            color: {t['text_main']};
            border-radius: 8px;
            border: 1px solid {t['border']};
            font-size: 14px;
            padding: 4px;
        }}
        QPushButton:hover {{
            background-color: {t['accent']};
            color: white;
            border: none;
        }}
        QPushButton:disabled {{
            background-color: rgba(0,0,0,0.1);
            color: rgba(0,0,0,0.3);
        }}
    """
    
    from PyQt6.QtWidgets import QPushButton
    for btn in main_window.findChildren(QPushButton):
        if btn.text() == "📁":
            btn.setStyleSheet(folder_btn_style)

    main_window.btn_reset.setStyleSheet(f"QPushButton {{background-color: transparent; color: {t['text_dim']}; border: 1px dashed {t['text_dim']}; border-radius: 5px;}} QPushButton:hover {{background-color: {t['accent']}; color: white; border:none;}}")

    history_btn_style = f"QPushButton {{background-color: rgba(255,255,255,0.6); color: {t['text_main']}; border-radius: 5px; border: 1px solid rgba(128,128,128,0.2); font-size: 12px; padding: 2px 8px;}} QPushButton:hover {{background-color: {t['accent']}; color: white;}} QPushButton:disabled {{background-color: rgba(0,0,0,0.05); color: rgba(0,0,0,0.3); border-color: transparent;}}"
    for btn in [main_window.btn_undo, main_window.btn_redo, main_window.btn_history]:
        if btn: btn.setStyleSheet(history_btn_style)

    for b in [main_window.btn_gen_font, main_window.btn_run_map, main_window.btn_run_subset, main_window.btn_checkup_map, main_window.btn_checkup_subset,
              main_window.btn_preview_map, main_window.btn_run_coverage, main_window.btn_run_merge,
              main_window.btn_read_info, main_window.btn_save_info, main_window.btn_run_compare, main_window.btn_export_diff,
              main_window.btn_run_smart, getattr(main_window, 'btn_run_convert', None), getattr(main_window, 'btn_run_imgfont', None)]:
        if b: b.set_theme_color(t['accent'])
    
    sb_style = get_scrollbar_style(main_window, t['accent'])
    combo_style = f"""
        QComboBox {{ 
            border: 1px solid rgba(128,128,128,0.2); 
            border-radius: 10px; 
            padding: 0 10px; 
            background: {t['input_bg']}; 
            color: {t['text_main']}; 
            height: 38px;
            font-size: 13px;
        }}
        QComboBox:focus {{
            border: 1px solid {t['accent']};
            background-color: {t['input_focus']};
        }}
        QComboBox::drop-down {{ 
            border: none; 
            width: 30px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {t['text_dim']};
            margin-right: 10px;
        }}
        QComboBox QAbstractItemView {{ 
            background: {t['card_bg']}; 
            selection-background-color: {t['accent']}; 
            color: {t['text_main']}; 
            border: 1px solid rgba(128,128,128,0.2);
            border-radius: 8px;
            outline: none;
        }}
        {sb_style}
    """
    main_window.combo_theme.setStyleSheet(combo_style)
    main_window.combo_mode.setStyleSheet(combo_style)
    main_window.combo_charset.setStyleSheet(combo_style)
    main_window.tab_container.setStyleSheet(f"background: {t['input_bg']}; border-radius: 15px;")
    main_window.tab_scroll_area.setStyleSheet(f"QScrollArea {{ background: transparent; border: none; }} {sb_style}")
    main_window.switch_tab(main_window.stack.currentIndex())
    bg_log = "rgba(255,255,255,0.1)" if "Night" in theme_name else "rgba(0,0,0,0.03)"
    main_window.log_area.update_theme(t['text_main'], bg_log, sb_style)
    main_window.progress.setStyleSheet(f"QProgressBar {{border:none; background:rgba(0,0,0,0.1); border-radius:3px;}} QProgressBar::chunk {{background: {t['accent']}; border-radius:3px;}}")
    main_window.help_browser.setStyleSheet(f"QTextEdit {{ background: transparent; border: none; font-size: 13px; line-height: 150%; color: {t['text_main']}; }} {sb_style}")
    if hasattr(main_window, 'preview_area'):
        main_window.preview_area.setStyleSheet(f"QTextEdit {{ background-color: {t['input_bg']}; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2); color: {t['text_main']}; padding: 2px; }} {sb_style}")
    common_te_style = f"QTextEdit {{ background: rgba(0,0,0,0.03); border-radius: 8px; padding: 10px; font-family: 'Consolas', monospace; color: {t['text_main']}; }} {sb_style}"
    if hasattr(main_window, 'cov_result'): main_window.cov_result.setStyleSheet(common_te_style)
    if hasattr(main_window, 'info_display'): main_window.info_display.setStyleSheet(common_te_style)
    if hasattr(main_window, 'cmp_result'): main_window.cmp_result.setStyleSheet(common_te_style)
    if hasattr(main_window, 'map_table'):
         main_window.map_table.setStyleSheet(f"QTableWidget {{ background-color: {t['input_bg']}; color: {t['text_main']}; border: none; }} {sb_style}")
    if hasattr(main_window, 'sf_table'):
         main_window.sf_table.setStyleSheet(f"QTableWidget {{ background-color: {t['input_bg']}; color: {t['text_main']}; border: none; }} {sb_style}")

def switch_tab(main_window, idx):
    main_window.stack.setCurrentIndex(idx)
    t = main_window.theme
    base = "border:none; border-radius: 12px; font-weight: bold; font-family: 'Microsoft YaHei';"
    active = f"{base} background-color: {t['accent']}; color: white;"
    inactive = f"{base} background-color: transparent; color: {t['text_dim']};"
    for i, b in enumerate(main_window.tabs): b.setChecked(i == idx); b.setStyleSheet(active if i == idx else inactive)

def set_help_content(main_window):
    html = """
    <style>
        h3 { color: #2196F3; margin-top: 12px; margin-bottom: 5px; font-family: 'Microsoft YaHei'; }
        h4 { color: #555; margin-bottom: 2px; font-weight: bold; }
        li { margin-bottom: 4px; color: #444; line-height: 140%; }
        p { color: #666; line-height: 140%; }
        code { background: rgba(0,0,0,0.08); padding: 2px 6px; border-radius: 4px; font-family: Consolas; }
        .tip { background: #E3F2FD; padding: 8px 12px; border-radius: 6px; border-left: 3px solid #2196F3; margin: 8px 0; }
        .warn { background: #FFF3E0; padding: 8px 12px; border-radius: 6px; border-left: 3px solid #FF9800; margin: 8px 0; }
    </style>
    <h3 style='text-align:center; border-bottom: 1px solid #ddd; padding-bottom:10px;'>Galgame 字体工具箱 使用指南</h3>

    <h3>快速入门</h3>
    <p>本工具专为游戏翻译设计。核心工作流程：</p>
    <ol>
        <li><b>扫描文本</b> - 在【映射表】功能中扫描翻译文本目录</li>
        <li><b>生成映射</b> - 自动生成字符映射表 (JSON)</li>
        <li><b>制作字体</b> - 选择模式1，生成伪装日文字体</li>
    </ol>
    <div class='tip'>拖拽功能：所有输入框都支持直接拖拽文件或文件夹</div>

    <h3>快捷键</h3>
    <ul>
        <li><code>Ctrl+O</code> 打开字体文件</li>
        <li><code>Ctrl+S</code> 保存当前预设</li>
        <li><code>Ctrl+E</code> 导出完整配置 (.gft)</li>
        <li><code>Ctrl+I</code> 导入配置文件</li>
        <li><code>Ctrl+Z / Y</code> 撤销/重做</li>
        <li><code>Ctrl+G</code> 生成字体</li>
        <li><code>F5</code> 刷新字体预览</li>
        <li><code>Ctrl+1~5</code> 快速切换标签页</li>
        <li><code>Ctrl+H</code> 打开帮助页面</li>
    </ul>

    <h3>处理模式说明</h3>
    <ul>
        <li><b>模式1 - 日繁映射 (推荐)</b>：将简体字映射到日文字形位置，生成伪装日文字体</li>
        <li><b>模式2 - 逆向映射</b>：反向操作，将日文字形映射回原位</li>
        <li><b>模式3 - 仅伪装</b>：不改变字形，只修改字体元数据伪装成日文</li>
        <li><b>模式4 - 繁转简</b>：使用 OpenCC 将繁体字形转换为简体</li>
        <li><b>模式5 - 简转繁</b>：使用 OpenCC 将简体字形转换为繁体</li>
    </ul>
    <div class='tip'>翻译项目通常选择模式1，配合映射表使用</div>

    <h3>左侧面板 - 核心设置</h3>
    <ul>
        <li><b>主字体</b>：游戏原版字体 (支持 .ttf/.otf)，点击下拉查看历史</li>
        <li><b>补全字体</b>：当主字体缺字时自动补充 (推荐思源黑体)</li>
        <li><b>码表 JSON</b>：映射表文件，由【映射表】功能自动生成</li>
        <li><b>输出目录</b>：自定义保存位置，留空则与源文件同目录</li>
        <li><b>输出文件名</b>：生成字体的文件名，必须以 .ttf 结尾</li>
        <li><b>内部字体名</b>：字体元数据中的名称，游戏引擎读取用</li>
    </ul>

    <h3>右侧功能区详解</h3>
    <h4>字体信息</h4>
    <p>查看和编辑字体元数据 (名称、版权、设计师等)，双击表格单元格可修改</p>
    
    <h4>映射表</h4>
    <p>扫描翻译文本目录，自动生成字符映射关系。支持预览替换效果、检查缺字</p>
    
    <h4>分析对比</h4>
    <p>对比两个字体的字符集差异，分析字体对各语言区块的覆盖率</p>
    
    <h4>精简瘦身</h4>
    <p>删除未使用的字符，大幅减小字体体积 (20MB到2~5MB)</p>
    
    <h4>合并补字</h4>
    <p>从其他字体复制缺失的字符。在"指定字符"框输入需要的字</p>
    
    <h4>图片字库</h4>
    <p>生成 PNG/WebP/TGA/BMP/BMFont 等格式的图片字库</p>
    
    <h4>Web转换</h4>
    <p>转换为 WOFF2 格式，压缩率可达 40-70%，适用于 H5 游戏</p>
    
    <h4>度量修复</h4>
    <p>调整字体的宽高比、间距、垂直度量，解决文字偏移/截断问题</p>
    
    <h4>兼容清理</h4>
    <p>移除高级 OpenType 特性，提高老引擎兼容性</p>
    
    <h4>智能补字</h4>
    <p>扫描字体库，自动查找包含缺失字符的字体来源</p>

    <h3>常见问题</h3>
    <div class='warn'><b>文字显示不全</b>：使用精简前确保扫描所有文本；或使用【合并补字】添加缺失字符</div>
    <div class='warn'><b>文字位置偏移</b>：使用【度量修复】，点击"自动计算"按钮对齐原版字体度量</div>
    <div class='warn'><b>游戏崩溃</b>：使用【兼容清理】移除高级特性 (GSUB/GPOS/hdmx等)</div>
    <div class='warn'><b>OTF 不支持</b>：工具会自动转换 OTF 到 TTF，无需手动处理</div>

    <h3>推荐工作流</h3>
    <ol>
        <li>准备翻译文本目录和原版日文字体</li>
        <li>【映射表】扫描文本、生成映射、检查缺字</li>
        <li>如有缺字，使用【合并补字】或【智能补字】补全</li>
        <li>【生成字体】选择模式1，点击生成</li>
        <li>【度量修复】加载参考字体，自动计算，执行修复</li>
        <li>测试游戏效果</li>
    </ol>

    <p style='text-align:center; font-size:11px; color:#999; margin-top:20px;'>
        所有输入框支持拖拽 | 自动保存设置 | 记录最近文件
    </p>
    """
    main_window.help_browser.setHtml(html)
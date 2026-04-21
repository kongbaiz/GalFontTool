import os
import json
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QLabel, QHBoxLayout
from PyQt6.QtGui import QFont, QFontDatabase
from core.worker import Worker


def log(main_window, m):
    main_window.log_area.append(m)
    main_window.log_area.verticalScrollBar().setValue(
        main_window.log_area.verticalScrollBar().maximum()
    )


def browse(main_window, target):
    if (
        target == main_window.map_src
        or target == main_window.sub_txt
        or target == main_window.sf_txt
        or target == main_window.sf_lib
    ):
        d = QFileDialog.getExistingDirectory(main_window, "选择目录")
        if d:
            target.setText(d)
    else:
        f, _ = QFileDialog.getOpenFileName(
            main_window, "选择文件", "", "Font/JSON (*.ttf *.otf *.json);;All (*.*)"
        )
        if f:
            target.setText(f)
            if hasattr(main_window, "add_to_recent_files") and f.lower().endswith(
                (".ttf", ".otf")
            ):
                main_window.add_to_recent_files(f)


def browse_folder(main_window, line_edit):
    d = QFileDialog.getExistingDirectory(main_window, "选择目录", "")
    if d:
        line_edit.setText(d)


def reset_to_default(main_window):
    reply = QMessageBox.question(
        main_window,
        "确认重置",
        "确定要清除所有设置并恢复默认值吗？",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    if reply == QMessageBox.StandardButton.Yes:
        main_window.settings.clear()
        main_window.in_src.setText("Font.ttf")
        main_window.in_fallback.setText("")
        main_window.in_json.setText("custom_map.json")
        main_window.in_file_name.setText("game.ttf")
        main_window.in_font_name.setText("My Game Font")
        main_window.in_output_dir.setText("")
        main_window.combo_mode.setCurrentIndex(0)
        main_window.combo_charset.setCurrentIndex(0)
        main_window.log_area.clear()
        main_window.log_area.append("已恢复默认设置。")


def save_preset(main_window):
    preset = {
        "src": main_window.in_src.text(),
        "fallback": main_window.in_fallback.text(),
        "json": main_window.in_json.text(),
        "file_name": main_window.in_file_name.text(),
        "font_name": main_window.in_font_name.text(),
        "mode": main_window.combo_mode.currentIndex(),
        "charset": main_window.combo_charset.currentIndex(),
        "map_src": main_window.map_src.text(),
        "map_out": main_window.map_out.text(),
        "map_json": main_window.map_json.text(),
        "map_ext": main_window.map_ext.text(),
        "sub_font": main_window.sub_font.text(),
        "sub_txt": main_window.sub_txt.text(),
        "sub_json": main_window.sub_json.text(),
        "sub_out": main_window.sub_out.text(),
        "pic_font": main_window.pic_font.text(),
        "pic_folder": main_window.pic_folder.text(),
        "tga_font": main_window.tga_font.text(),
        "bmp_font": main_window.bmp_font.text(),
    }
    save_path, _ = QFileDialog.getSaveFileName(
        main_window, "保存预设", "my_preset.json", "JSON (*.json)"
    )
    if save_path:
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(preset, f, ensure_ascii=False, indent=2)
            main_window.log(f"预设已保存: {os.path.basename(save_path)}")
            QMessageBox.information(
                main_window, "保存成功", f"配置预设已保存到：\n{save_path}"
            )
        except Exception as e:
            main_window.log(f"保存预设失败: {e}")


def load_preset(main_window):
    load_path, _ = QFileDialog.getOpenFileName(main_window, "加载预设", "", "JSON (*.json)")
    if not load_path:
        return
    try:
        with open(load_path, "r", encoding="utf-8") as f:
            preset = json.load(f)

        if "src" in preset:
            main_window.in_src.setText(preset["src"])
        if "fallback" in preset:
            main_window.in_fallback.setText(preset["fallback"])
        if "json" in preset:
            main_window.in_json.setText(preset["json"])
        if "file_name" in preset:
            main_window.in_file_name.setText(preset["file_name"])
        if "font_name" in preset:
            main_window.in_font_name.setText(preset["font_name"])
        if "mode" in preset:
            main_window.combo_mode.setCurrentIndex(preset["mode"])
        if "charset" in preset:
            main_window.combo_charset.setCurrentIndex(preset["charset"])
        if "map_src" in preset:
            main_window.map_src.setText(preset["map_src"])
        if "map_out" in preset:
            main_window.map_out.setText(preset["map_out"])
        if "map_json" in preset:
            main_window.map_json.setText(preset["map_json"])
        if "map_ext" in preset:
            main_window.map_ext.setText(preset["map_ext"])
        if "sub_font" in preset:
            main_window.sub_font.setText(preset["sub_font"])
        if "sub_txt" in preset:
            main_window.sub_txt.setText(preset["sub_txt"])
        if "sub_json" in preset:
            main_window.sub_json.setText(preset["sub_json"])
        if "sub_out" in preset:
            main_window.sub_out.setText(preset["sub_out"])
        if "pic_font" in preset:
            main_window.pic_font.setText(preset["pic_font"])
        if "pic_folder" in preset:
            main_window.pic_folder.setText(preset["pic_folder"])
        if "tga_font" in preset:
            main_window.tga_font.setText(preset["tga_font"])
        if "bmp_font" in preset:
            main_window.bmp_font.setText(preset["bmp_font"])

        main_window.log(f"预设已加载: {os.path.basename(load_path)}")
        QMessageBox.information(
            main_window, "加载成功", f"已从预设恢复配置：\n{os.path.basename(load_path)}"
        )
    except Exception as e:
        main_window.log(f"加载预设失败: {e}")
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
        if result.endswith(".ttf"):
            main_window.generated_font_path = result
            main_window.pic_font.setText(result)
            main_window.tga_font.setText(result)
            main_window.bmp_font.setText(result)
            main_window.lbl_status.setText("字体已就绪")
            family = main_window.load_font_for_preview(result)
            if family:
                main_window.generated_font_family = family
                main_window.update_previews()
        elif result.endswith(".json"):
            main_window.in_json.setText(result)
            main_window.lbl_status.setText("映射表已就绪")

    if hasattr(main_window, "update_history_buttons"):
        main_window.update_history_buttons()


def load_settings(main_window):
    main_window.in_src.setText(main_window.settings.value("in_src", "Font.ttf"))
    main_window.in_fallback.setText(main_window.settings.value("in_fallback", ""))
    main_window.in_json.setText(main_window.settings.value("in_json", "custom_map.json"))
    main_window.in_file_name.setText(main_window.settings.value("in_file_name", "game.ttf"))
    main_window.in_font_name.setText(
        main_window.settings.value("in_font_name", "My Game Font")
    )
    main_window.chk_lock_file_name.setChecked(
        main_window.settings.value("lock_file_name", False) == "true"
        or main_window.settings.value("lock_file_name", False) is True
    )
    main_window.chk_lock_font_name.setChecked(
        main_window.settings.value("lock_font_name", False) == "true"
        or main_window.settings.value("lock_font_name", False) is True
    )
    if hasattr(main_window, "in_output_dir"):
        main_window.in_output_dir.setText(main_window.settings.value("output_dir", ""))
    main_window.combo_mode.setCurrentIndex(int(main_window.settings.value("mode", 0)))
    main_window.combo_charset.setCurrentIndex(
        int(main_window.settings.value("charset", 0))
    )
    if hasattr(main_window, "load_recent_files"):
        main_window.load_recent_files()
    main_window.on_source_font_changed()
    if hasattr(main_window, "update_history_buttons"):
        main_window.update_history_buttons()


def load_font_for_preview(main_window, font_path):
    if not os.path.exists(font_path):
        return None
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id == -1:
        main_window.log(f"预览加载失败: {os.path.basename(font_path)}")
        return None
    family = QFontDatabase.applicationFontFamilies(font_id)[0]
    main_window.log(f"预览已加载: {family}")
    return family


def update_previews(main_window):
    preview_text = main_window.preview_input.text()
    if not preview_text:
        preview_text = main_window.preview_input.placeholderText()
    main_window.preview_area.setText(preview_text)
    family_to_use = (
        main_window.generated_font_family
        if main_window.generated_font_family
        else main_window.original_font_family
    )
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
        if hasattr(main_window, "add_to_recent_files"):
            main_window.add_to_recent_files(src_font_path)


def on_mode_change(main_window, index):
    need_json = index in [1, 2]
    main_window.in_json.setEnabled(need_json)
    main_window.btn_json.setEnabled(need_json)


def create_label(main_window, t):
    return QLabel(t)


def create_file_row(main_window, inp, btn):
    l = QHBoxLayout()
    btn.clicked.connect(lambda: main_window.browse(inp))
    l.addWidget(inp)
    l.addWidget(btn)
    return l


def switch_tab(main_window, idx):
    main_window.stack.setCurrentIndex(idx)
    for i, b in enumerate(main_window.tabs):
        b.setChecked(i == idx)


def set_help_content(main_window):
    html = """
    <h3>Galgame 字体工具箱</h3>
    <p>主界面保留原生控件风格，功能不变。</p>
    <p>常用快捷键：</p>
    <ul>
        <li>Ctrl+O 打开主字体文件</li>
        <li>Ctrl+S 保存当前预设</li>
        <li>Ctrl+E 导出完整配置</li>
        <li>Ctrl+I 导入配置</li>
        <li>Ctrl+G 开始生成字体</li>
        <li>F5 刷新字体预览</li>
    </ul>
    """
    main_window.help_browser.setHtml(html)

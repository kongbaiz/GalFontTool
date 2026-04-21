import os


def closeEvent(main_window, event):
    main_window.settings.setValue("in_src", main_window.in_src.text())
    main_window.settings.setValue("in_fallback", main_window.in_fallback.text())
    main_window.settings.setValue("in_json", main_window.in_json.text())
    main_window.settings.setValue("in_file_name", main_window.in_file_name.text())
    main_window.settings.setValue("in_font_name", main_window.in_font_name.text())
    main_window.settings.setValue("mode", main_window.combo_mode.currentIndex())
    main_window.settings.setValue("charset", main_window.combo_charset.currentIndex())
    main_window.settings.setValue("lock_file_name", main_window.chk_lock_file_name.isChecked())
    main_window.settings.setValue("lock_font_name", main_window.chk_lock_font_name.isChecked())
    if hasattr(main_window, "in_output_dir"):
        main_window.settings.setValue("output_dir", main_window.in_output_dir.text())
    if hasattr(main_window, "recent_files"):
        main_window.settings.setValue("recent_files", main_window.recent_files)
    event.accept()


def dragEnterEvent(main_window, event):
    if event.mimeData().hasUrls():
        event.acceptProposedAction()


def dropEvent(main_window, event):
    urls = event.mimeData().urls()
    current_idx = main_window.stack.currentIndex()

    if current_idx == 3:
        for url in urls:
            path = url.toLocalFile()
            if os.path.isdir(path):
                main_window.sub_txt.setText(path)
                main_window.log_area.append(f"[精简] 文本目录: {path}")
            elif path.lower().endswith((".ttf", ".otf")):
                main_window.sub_font.setText(path)
                main_window.log_area.append(f"[精简] 源字体: {os.path.basename(path)}")
                if hasattr(main_window, "add_to_recent_files"):
                    main_window.add_to_recent_files(path)
            elif path.lower().endswith(".json"):
                main_window.sub_json.setText(path)
                main_window.log_area.append(f"[精简] 映射表: {os.path.basename(path)}")
        return

    if current_idx == 4:
        for url in urls:
            path = url.toLocalFile()
            if path.lower().endswith((".ttf", ".otf")):
                if not main_window.merge_base.text() or main_window.merge_base.text() == "base.ttf":
                    main_window.merge_base.setText(path)
                    main_window.log_area.append(f"[合并] 基础字体: {os.path.basename(path)}")
                elif not main_window.merge_add.text() or main_window.merge_add.text() == "supplement.ttf":
                    main_window.merge_add.setText(path)
                    main_window.log_area.append(f"[合并] 补充字体: {os.path.basename(path)}")
                else:
                    main_window.merge_add.setText(path)
                    main_window.log_area.append(f"[合并] 更新补充字体: {os.path.basename(path)}")
                if hasattr(main_window, "add_to_recent_files"):
                    main_window.add_to_recent_files(path)
        return

    if current_idx == 2:
        for url in urls:
            path = url.toLocalFile()
            if path.lower().endswith((".ttf", ".otf")):
                if not main_window.cmp_font1.text() or main_window.cmp_font1.text() == "fontA.ttf":
                    main_window.cmp_font1.setText(path)
                    main_window.log_area.append(f"[分析] 字体 A: {os.path.basename(path)}")
                elif not main_window.cmp_font2.text() or main_window.cmp_font2.text() == "fontB.ttf":
                    main_window.cmp_font2.setText(path)
                    main_window.log_area.append(f"[分析] 字体 B: {os.path.basename(path)}")
                else:
                    main_window.cov_font.setText(path)
                    main_window.log_area.append(f"[分析] 覆盖率字体: {os.path.basename(path)}")
                if hasattr(main_window, "add_to_recent_files"):
                    main_window.add_to_recent_files(path)
        return

    if current_idx == 0:
        for url in urls:
            path = url.toLocalFile()
            if path.lower().endswith((".ttf", ".otf")):
                main_window.info_font.setText(path)
                main_window.log_area.append(f"[信息] 已载入字体: {os.path.basename(path)}")
                main_window.do_read_font_info()
                if hasattr(main_window, "add_to_recent_files"):
                    main_window.add_to_recent_files(path)
        return

    if current_idx == 9:
        for url in urls:
            path = url.toLocalFile()
            if os.path.isdir(path):
                if not main_window.sf_txt.text() or main_window.sf_txt.text() == "cn_text":
                    main_window.sf_txt.setText(path)
                    main_window.log_area.append(f"[智能补字] 文本目录: {path}")
                else:
                    main_window.sf_lib.setText(path)
                    main_window.log_area.append(f"[智能补字] 字库目录: {path}")
            elif path.lower().endswith((".ttf", ".otf")):
                main_window.sf_primary.setText(path)
                main_window.log_area.append(f"[智能补字] 主字体: {os.path.basename(path)}")
                if hasattr(main_window, "add_to_recent_files"):
                    main_window.add_to_recent_files(path)
        return

    for url in urls:
        path = url.toLocalFile()
        if os.path.isdir(path):
            main_window.map_src.setText(path)
            main_window.log_area.append(f"已设置文本目录: {path}")
            main_window.switch_tab(1)
        elif path.lower().endswith((".ttf", ".otf")):
            if not main_window.in_src.text() or main_window.in_src.text() == "Font.ttf":
                main_window.in_src.setText(path)
                main_window.log_area.append(f"已载入主字体: {os.path.basename(path)}")
                main_window.on_source_font_changed()
            else:
                main_window.in_fallback.setText(path)
                main_window.log_area.append(f"已载入补全字体: {os.path.basename(path)}")
            if hasattr(main_window, "add_to_recent_files"):
                main_window.add_to_recent_files(path)
        elif path.lower().endswith(".json"):
            main_window.in_json.setText(path)
            main_window.log_area.append(f"已载入映射表: {os.path.basename(path)}")

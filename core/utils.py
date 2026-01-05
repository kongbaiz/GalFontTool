from fontTools.ttLib import newTable
from fontTools.pens.ttGlyphPen import TTGlyphPen


def ensure_ttf(font, logger_func=print, name_desc="字体"):
    # 同时检查 CFF 和 CFF2
    if 'CFF ' not in font and 'CFF2' not in font:
        return font

    if logger_func:
        logger_func(f"⚙️ 检测到 {name_desc} 为 OTF 格式，正在转换为 TTF 格式以确保合并兼容性...")
    
    glyphOrder = font.getGlyphOrder()
    
    # 彻底重新初始化 maxp 表
    if 'maxp' not in font:
        font['maxp'] = newTable('maxp')
    font['maxp'].tableVersion = 0x00010000
    font['maxp'].numGlyphs = len(glyphOrder)
    font['maxp'].maxZones = 1
    font['maxp'].maxTwilightPoints = 0
    font['maxp'].maxStorage = 0
    font['maxp'].maxFunctionDefs = 0
    font['maxp'].maxInstructionDefs = 0
    font['maxp'].maxStackElements = 0
    font['maxp'].maxSizeOfInstructions = 0
    font['maxp'].maxComponentElements = 0

    # 创建新的 loca 和 glyf 表
    font['loca'] = newTable('loca')
    font['glyf'] = newTable('glyf')
    font['glyf'].glyphs = {}
    font['glyf'].glyphOrder = glyphOrder

    glyphSet = font.getGlyphSet()
    for glyphName in glyphOrder:
        # 使用 TTGlyphPen 进行转换，这会处理复合字形的分解和 CFF 到 TTF 的轮廓转换
        pen = TTGlyphPen(glyphSet)
        try:
            glyphSet[glyphName].draw(pen)
            font['glyf'][glyphName] = pen.glyph()
        except Exception:
            # 容错处理：如果转换失败，生成一个空的字形
            font['glyf'][glyphName] = TTGlyphPen(None).glyph()

    # 移除所有 OTF 特有的表
    for tag in ['CFF ', 'CFF2', 'VORG', 'fvar', 'gvar', 'STAT', 'MVAR', 'HVAR', 'VVAR']:
        if tag in font:
            del font[tag]
            
    # 修改文件头标识为 TTF (0x00010000)
    font.sfntVersion = "\x00\x01\x00\x00"
    
    # 强制更新字体对象的字形顺序
    font.setGlyphOrder(glyphOrder)
    
    if logger_func:
        logger_func(f"✅ {name_desc} 格式转换成功。")
    return font

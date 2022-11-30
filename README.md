# gfont

一个字体处理方法合集，含有以下方法

- to_xml：将字体文件转换为 xml
- to_img：将单个或所有字体转为 Image 对象
- to_ocr：将单个或所有字体识别转为 str、dict 对象
- get_glyph_order：获取字段信息列表
- get_best_cmap：获取十六进制与字段信息字典

# 安装

```
pip install gfont
```

# 使用环境

```
pip install font2img==2.2
pip install fonttools==4.29.1
pip install Pillow==9.3.0
pip install paddlepaddle==2.3.2 -i https://mirror.baidu.com/pypi/simple
pip install "paddleocr==2.6.0.1"
```

# 示例

```
from gfont import FontHelper

f = FontHelper(path=r'font.ttf')
print(f.to_ocr())
```
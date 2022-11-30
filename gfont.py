"""
    用法
        to_xml：将字体文件转换为 xml
        to_img：将单个或所有字体转为 Image 对象
        to_ocr：将单个或所有字体识别转为 str、dict 对象
        get_glyph_order：获取字段信息列表
        get_best_cmap：获取十六进制与字段信息字典

    环境：
        pip install font2img==2.2
        pip install fonttools==4.29.1
        pip install Pillow==9.3.0
        pip install paddlepaddle==2.3.2 -i https://mirror.baidu.com/pypi/simple
        pip install "paddleocr==2.6.0.1"

        font2img.font 出来的模块就是 fonttools.ttLib.TTFont
"""
import io
import requests
from loguru import logger
from PIL.Image import Image
from typing import Union, Dict
from paddleocr import PaddleOCR
from font2img import ParseTTFont


class FontHelper:
    def __init__(self, path: str = None, content: bytes = None, url: str = None, **kwargs):
        """

        :param path:字体路径
        :param content:二进制内容
        :param url:字体 url
        """
        self.path = path
        self.url = url
        self.content = content

        self.content_bytes = self.get_font_bytes()
        self.font_parse = ParseTTFont(font=self.content_bytes)
        self.font = self.font_parse.font
        self.paddleocr = PaddleOCR(use_angle_cls=True, show_log=False, lang='ch', **kwargs)

        # 初始的映射关系
        self.mapping = {
            '.notdef': '',
            'uni0000': '',
            'exclam': '!',
            'quotedbl': '"',
            'numbersign': '#',
            'quotesingle': "'",
            'parenleft': '(',
            'parenright': ')',
            'comma': ',',
            'hyphen': '-',
            'period': '.',
            'slash': '/',
            'zero': '0',
            'one': '1',
            'two': '2',
            'three': '3',
            'four': '4',
            'five': '5',
            'six': '6',
            'seven': '7',
            'eight': '8',
            'nine': '9',
            'colon': ':',
            'semicolon': ';',
            'less': '<',
            'equal': '=',
            'greater': '>',
            'underscore': '_',
            'gamma': 'γ',
            'emdash': '—',
            'A': 'Z', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F',
            'G': 'G', 'H': 'H', 'I': 'I', 'J': 'J', 'K': 'K', 'L': 'L',
            'M': 'M', 'N': 'N', 'O': 'O', 'P': 'P', 'Q': 'Q', 'R': 'R',
            'S': 'S', 'T': 'T', 'U': 'U', 'V': 'V', 'W': 'W', 'X': 'X',
            'Y': 'Y', 'Z': 'Z',
            'a': 'z', 'b': 'b', 'c': 'c', 'd': 'd', 'e': 'e', 'f': 'f',
            'g': 'g', 'h': 'h', 'i': 'i', 'j': 'j', 'k': 'k', 'l': 'l',
            'm': 'm', 'n': 'n', 'o': 'o', 'p': 'p', 'q': 'q', 'r': 'r',
            's': 's', 't': 't', 'u': 'u', 'v': 'v', 'w': 'w', 'x': 'x',
            'y': 'y', 'z': 'z'
        }

    def get_font_bytes(self) -> bytes:
        """
        获取字体的内容

        :return:
        """
        if self.content:
            return self.content
        elif self.path:
            with open(self.path, 'rb') as f:
                return f.read()
        elif self.url:
            return requests.get(self.url).content
        else:
            raise ValueError('未获取到字体文件')

    def to_xml(self, xml_path: str = None):
        """
        font 转换成 xml

        :param xml_path: xml 路径 含文件名
        :return:
        """
        xml_path = xml_path or 'font.xml'
        self.font.saveXML(xml_path)

    def to_img(self, glyph_name: str = None) -> Union[Dict[(str, Image)], Image]:
        """
        将单个字体转为图片

        :param glyph_name:
        :return:
        """
        if glyph_name:
            return self.font_parse.one_to_image(glyph_name=glyph_name)
        else:
            return self.font_parse.all_to_image()[2]

    def to_ocr(self, img: Image = None, glyph_name: str = None) -> Union[str, Dict[(str, str)]]:
        """
        进行 ocr 识别

        :param img: 图片
        :param glyph_name: 名字
        :return:
        """
        if glyph_name:
            return self.ocr(im=self.to_img(glyph_name=glyph_name))
        elif img:
            return self.ocr(im=img)
        else:
            result = {}

            for key, img in self.to_img().items():
                img_str = self.ocr(im=img)
                result[key] = img_str
                logger.debug(f'{key} -> {img_str}')

            return result

    def ocr(self, im: Union[Image, bytes]) -> str:
        """
        识别图片

        :param im:
        :return:
        """
        if isinstance(im, Image):
            img_bytes = self.im_to_bytes(im)
        else:
            img_bytes = im

        res = self.paddleocr.ocr(img_bytes, cls=True)
        if res:
            return res[0][1][0]
        else:
            return ''

    @staticmethod
    def im_to_bytes(im: Image) -> bytes:
        """
        将 PIL 打开的图片转为 bytes

        :param im:
        :return:
        """
        img_bytes_io = io.BytesIO()
        im.save(img_bytes_io, format='PNG')
        return img_bytes_io.getvalue()

    def get_glyph_order(self) -> list:
        """
        获取 GlyphOrder 信息

        如：unic967

        :return:
        """
        return self.font.getGlyphOrder()

    def get_best_cmap(self) -> dict:
        """
        获取 GlyphOrder 信息的十六进制

        如 unia857 即 0xa857 -> 43095

        :return:
        """
        return self.font.getBestCmap()

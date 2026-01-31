import re
import shutil
from typing import List, Union, Optional, Any, Dict

def printf(*args: Any, style: Optional[str] = None, **kwargs: Any) -> None:
    """
    Улучшенная версия print с поддержкой CSS-подобного форматирования через теги.
    
    Args:
        *args: Аргументы для печати (как в стандартной функции print)
        style: CSS-подобные стили в формате:
            '''
            tag {
                color: rgb(255, 0, 255);    # RGB цвет
                color: #ff00ff;             # HEX цвет  
                color: red;                 # именованный цвет
                background: blue;           # фон
                effect: bold;               # эффект текста
                transform: upper;           # текстовая трансформация
                width: 50;                  # ширина для центрирования
                align: center;              # выравнивание (left/center/right)
            }
            '''
        **kwargs: Дополнительные аргументы как в print (sep, end, file, flush, etc.)
    
    Supported Color Formats:
        - Named colors: black, red, green, yellow, blue, magenta, cyan, white, default
        - RGB: rgb(255, 0, 255) or rgb(255,0,255)
        - HEX: #ff00ff or #f0f (короткая запись)
    
    Supported Backgrounds:
        - Named backgrounds: black, red, green, yellow, blue, magenta, cyan, white, default
        - RGB: background: rgb(255, 0, 255)
        - HEX: background: #ff00ff
    
    Supported Effects:
        - bold, dim, italic, underline, blink, reverse, hidden
    
    Supported Transforms:
        - upper: преобразует в ВЕРХНИЙ РЕГИСТР
        - lower: преобразует в нижний регистр
        - title: Каждое Слово С Заглавной Буквы
        - capitalize: Первая буква заглавная
        - swapcase: иНВЕРТИРУЕТ рЕГИСТР
        - strip: удаляет пробелы по краям
        - lstrip: удаляет пробелы слева
        - rstrip: удаляет пробелы справа
    
    Supported Alignments:
        - left: выравнивание по левому краю (по умолчанию)
        - center: центрирование текста
        - right: выравнивание по правому краю
    
    Usage Examples:
        >>> prinf("<p>Привет!</p> <name>Я Дубровский</name>", style=STYLES)
        >>> prinf("<error>тут ошибка</error>", style=STYLES)
        >>> prinf("<header>Заголовок</header>", style=STYLES)
        >>> prinf("<center>Центрированный текст</center>", style=STYLES)
    
    Note:
        - Форматирование сбрасывается закрывающим тегом </tag> или пустым </>
        - Трансформации применяются до применения цветов и эффектов
        - Для центрирования используйте width и align: center
        - По умолчанию доступны стандартные стили через константу STYLES
    """
    
    # Базовые ANSI коды
    ANSI_CODES: Dict[str, str] = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m',
        'italic': '\033[3m',
        'underline': '\033[4m',
        'blink': '\033[5m',
        'reverse': '\033[7m',
        'hidden': '\033[8m'
    }
    
    # Цвета
    COLORS: Dict[str, str] = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'default': '\033[39m'
    }
    
    # Фоны
    BACKGROUNDS: Dict[str, str] = {
        'black': '\033[40m',
        'red': '\033[41m',
        'green': '\033[42m',
        'yellow': '\033[43m',
        'blue': '\033[44m',
        'magenta': '\033[45m',
        'cyan': '\033[46m',
        'white': '\033[47m',
        'default': '\033[49m'
    }
    
    # Текстовые трансформации
    TRANSFORMS: Dict[str, Any] = {
        'upper': str.upper,
        'lower': str.lower,
        'title': str.title,
        'capitalize': str.capitalize,
        'swapcase': str.swapcase,
        'strip': str.strip,
        'lstrip': str.lstrip,
        'rstrip': str.rstrip,
    }

    def parse_styles(style_text: Optional[str]) -> Dict[str, Dict[str, str]]:
        """Парсит CSS-подобные стили"""
        styles: Dict[str, Dict[str, str]] = {}
        if not style_text:
            return styles
            
        # Находим все блоки стилей
        pattern = r'(\w+)\s*\{([^}]+)\}'
        matches = re.findall(pattern, style_text)
        
        for tag, style_block in matches:
            tag_styles: Dict[str, str] = {}
            
            # Парсим свойства
            for line in style_block.split(';'):
                line = line.strip()
                if ':' in line:
                    prop, value = line.split(':', 1)
                    prop = prop.strip()
                    value = value.strip()
                    tag_styles[prop] = value
            
            styles[tag] = tag_styles
            
        return styles
    
    def hex_to_rgb(hex_color: str) -> Optional[tuple[int, int, int]]:
        """Конвертирует HEX цвет в RGB tuple"""
        hex_color = hex_color.lstrip('#')
        
        # Короткая запись #rgb -> #rrggbb
        if len(hex_color) == 3:
            hex_color = ''.join(c * 2 for c in hex_color)
        
        if len(hex_color) == 6:
            try:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return r, g, b
            except ValueError:
                return None
        return None
    
    def color_to_ansi(color_str: str, is_background: bool = False) -> str:
        """Конвертирует цвет в ANSI код из различных форматов"""
        # Именованные цвета
        if color_str in COLORS and not is_background:
            return COLORS[color_str]
        if color_str in BACKGROUNDS and is_background:
            return BACKGROUNDS[color_str]
        
        # HEX цвета
        if color_str.startswith('#'):
            rgb = hex_to_rgb(color_str)
            if rgb:
                r, g, b = rgb
                code = 48 if is_background else 38
                return f'\033[{code};2;{r};{g};{b}m'
        
        # RGB цвета
        rgb_match = re.match(r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color_str)
        if rgb_match:
            r, g, b = map(int, rgb_match.groups())
            code = 48 if is_background else 38
            return f'\033[{code};2;{r};{g};{b}m'
        
        return ''
    
    def apply_transform(text: str, transform_name: str) -> str:
        """Применяет текстовую трансформацию"""
        if transform_name in TRANSFORMS:
            return TRANSFORMS[transform_name](text)
        return text
    
    def apply_alignment(text: str, width_str: str, align_str: str) -> str:
        """Применяет выравнивание к тексту"""
        try:
            width = int(width_str)
            align = align_str.lower()
            
            # Удаляем ANSI коды для правильного расчета длины
            clean_text = re.sub(r'\033\[[0-9;]*m', '', text)
            
            if align == 'center' and len(clean_text) < width:
                padding = width - len(clean_text)
                left_padding = padding // 2
                right_padding = padding - left_padding
                return ' ' * left_padding + text + ' ' * right_padding
            elif align == 'right' and len(clean_text) < width:
                return ' ' * (width - len(clean_text)) + text
            # left alignment is default
            
        except (ValueError, TypeError):
            pass
        
        return text
    
    def apply_styles(text: str, styles: Dict[str, Dict[str, str]]) -> str:
        """Применяет стили к тексту с тегами"""
        if not styles:
            return text
            
        # Регулярка для поиска тегов и их содержимого
        pattern = r'<(\w+)>([^<]*)</\1>|</?(\w*)>'
        
        def process_tag_content(match: re.Match) -> str:
            """Обрабатывает содержимое тега с применением стилей и трансформаций"""
            if match.group(1):  # Тег с содержимым: <tag>content</tag>
                tag_name = match.group(1)
                content = match.group(2)
                
                if tag_name in styles:
                    style_data = styles[tag_name]
                    ansi_codes: List[str] = []
                    
                    # Текстовая трансформация (применяется первой)
                    if 'transform' in style_data:
                        transform = style_data['transform']
                        content = apply_transform(content, transform)
                    
                    # Выравнивание (применяется перед цветами)
                    if 'width' in style_data and 'align' in style_data:
                        content = apply_alignment(content, style_data['width'], style_data['align'])
                    
                    # Цвет
                    if 'color' in style_data:
                        color = style_data['color']
                        ansi_code = color_to_ansi(color, False)
                        if ansi_code:
                            ansi_codes.append(ansi_code)
                    
                    # Фон
                    if 'background' in style_data:
                        bg = style_data['background']
                        ansi_code = color_to_ansi(bg, True)
                        if ansi_code:
                            ansi_codes.append(ansi_code)
                    
                    # Эффекты
                    if 'effect' in style_data:
                        effect = style_data['effect']
                        if effect in ANSI_CODES:
                            ansi_codes.append(ANSI_CODES[effect])
                    
                    return ''.join(ansi_codes) + content + ANSI_CODES['reset']
                else:
                    return match.group(0)  # Возвращаем как есть, если стиль не найден
                    
            else:  # Одиночный тег: </tag> или </>
                tag_name = match.group(3)
                if tag_name == '':  # Пустой тег </>
                    return ANSI_CODES['reset']
                return ANSI_CODES['reset']
            
            return match.group(0)
        
        # Обрабатываем все теги
        result = re.sub(pattern, process_tag_content, text)
        
        return result
    
    # Парсим стили
    parsed_styles = parse_styles(style)
    
    # Обрабатываем аргументы
    processed_args: List[str] = []
    for arg in args:
        if isinstance(arg, str):
            processed_args.append(apply_styles(arg, parsed_styles))
        else:
            processed_args.append(str(arg))
    
    # Используем стандартный print с обработанными аргументами
    print(*processed_args, **kwargs)


# СТАНДАРТНЫЕ СТИЛИ
STYLES: str = """
/* Основные стили для текста */
p {
    color: #cccccc;
}

strong {
    effect: bold;
    color: #ffffff;
}

em {
    effect: italic;
    color: #ffff00;
}

underline {
    effect: underline;
}

/* Стили для статусов и уведомлений */
success {
    color: #00ff00;
    effect: bold;
}

error {
    color: #ff0000;
    effect: bold;
}

warning {
    color: #ffa500;
    effect: bold;
}

info {
    color: #00ffff;
    effect: bold;
}

/* Стили для заголовков */
h1 {
    color: #ffffff;
    effect: bold;
    transform: upper;
}

h2 {
    color: #ffffff;
    effect: bold;
    transform: capitalize;
}

h3 {
    color: #ffff00;
    effect: bold;
}

/* Стили для кода и данных */
code {
    color: #00ff00;
    background: #000000;
}

data {
    color: #ff00ff;
    effect: bold;
}

quote {
    color: #888888;
    effect: italic;
}

/* Стили для выравнивания */
center {
    width: 80;
    align: center;
    effect: bold;
}

right {
    width: 80;
    align: right;
}

left {
    width: 80;
    align: left;
}

/* Стили для специальных элементов */
header {
    color: #ffffff;
    background: #0000ff;
    effect: bold;
    transform: upper;
    width: 80;
    align: center;
}

footer {
    color: #888888;
    effect: dim;
    width: 80;
    align: center;
}

menu {
    color: #ffff00;
    effect: bold;
}

button {
    color: #000000;
    background: #ffff00;
    effect: bold;
}

label {
    color: #00ffff;
    effect: bold;
}

value {
    color: #ffffff;
    effect: bold;
}

/* Стили для прогресс-бара */
progress_low {
    color: #ff0000;
    effect: bold;
}

progress_medium {
    color: #ffa500;
    effect: bold;
}

progress_high {
    color: #ffff00;
    effect: bold;
}

progress_complete {
    color: #00ff00;
    effect: bold;
}
"""


# ДОПОЛНИТЕЛЬНЫЕ УЛУЧШЕНИЯ

def prinf_table(data: List[List[Any]], 
                headers: Optional[List[str]] = None, 
                style: Optional[str] = None) -> None:
    """
    Печатает таблицу с форматированием.
    
    Args:
        data: Двумерный список данных для таблицы. 
              Каждый внутренний список - строка таблицы.
              Пример: [["Яблоки", "15 кг"], ["Бананы", "8 кг"]]
        headers: Список заголовков колонок. Если None, заголовки не печатаются.
        style: Стили для форматирования. Если None, используются STYLES.
    
    Example:
        >>> data = [["Яблоки", "15 кг"], ["Бананы", "8 кг"]]
        >>> headers = ["Товар", "Количество"]
        >>> prinf_table(data, headers, STYLES)
    """
    if not data:
        return
    
    def clean_ansi_codes(text: str) -> str:
        """Удаляет ANSI коды из текста для правильного расчета ширины"""
        return re.sub(r'\033\[[0-9;]*m', '', text)
    
    # Определяем ширину колонок (используем очищенный от ANSI кодов текст)
    if headers:
        clean_headers = [clean_ansi_codes(str(header)) for header in headers]
        all_data_for_width = [clean_headers] + [[clean_ansi_codes(str(cell)) for cell in row] for row in data]
    else:
        all_data_for_width = [[clean_ansi_codes(str(cell)) for cell in row] for row in data]
    
    col_widths: List[int] = []
    for i in range(len(all_data_for_width[0])):
        col_width = max(len(row[i]) for row in all_data_for_width)
        col_widths.append(col_width + 2)  # Добавляем отступы
    
    # Верхняя граница
    top_border = "┌" + "┬".join("─" * w for w in col_widths) + "┐"
    prinf(f"{top_border}", style=style or STYLES)
    
    # Печатаем заголовки
    if headers:
        header_cells = []
        for i, header in enumerate(headers):
            header_cells.append(f" {str(header).ljust(col_widths[i]-2)} ")
        header_row = "│".join(header_cells)
        prinf(f"│{header_row}│", style=style or STYLES)
        
        # Разделитель заголовков и данных
        middle_border = "├" + "┼".join("─" * w for w in col_widths) + "┤"
        prinf(f"{middle_border}", style=style or STYLES)
    
    # Печатаем данные
    for row in data:
        row_cells = []
        for i, cell in enumerate(row):
            row_cells.append(f" {str(cell).ljust(col_widths[i]-2)} ")
        row_str = "│".join(row_cells)
        prinf(f"│{row_str}│", style=style or STYLES)
    
    # Нижняя граница
    bottom_border = "└" + "┴".join("─" * w for w in col_widths) + "┘"
    prinf(f"{bottom_border}", style=style or STYLES)

def prinf_progress(iteration: int, 
                   total: int, 
                   prefix: str = '', 
                   suffix: str = '', 
                   length: int = 50, 
                   style: Optional[str] = None,
                   color_scale: bool = True) -> None:
    """
    Печатает прогресс-бар с автоматической сменой цвета.
    
    Args:
        iteration: Текущая итерация (от 0 до total)
        total: Общее количество итераций
        prefix: Текст перед прогресс-баром
        suffix: Текст после прогресс-бара
        length: Длина прогресс-бара в символах
        style: Стили для форматирования. Если None, используются STYLES.
        color_scale: Если True, цвет меняется в зависимости от прогресса
    
    Example:
        >>> for i in range(101):
        ...     prinf_progress(i, 100, prefix='Progress:')
    """
    percent = 100 * (iteration / float(total))
    filled_length = int(length * iteration // total)
    
    # Выбираем цвет в зависимости от прогресса
    progress_tag = "progress_complete"
    if color_scale:
        if percent < 25:
            progress_tag = "progress_low"
        elif percent < 50:
            progress_tag = "progress_medium" 
        elif percent < 75:
            progress_tag = "progress_high"
        elif percent < 100:
            progress_tag = "progress_high"
        else:
            progress_tag = "progress_complete"
    
    bar = '█' * filled_length + '░' * (length - filled_length)
    
    prinf(f'\r<info>{prefix}</info> |<{progress_tag}>{bar}</{progress_tag}>| <value>{percent:.1f}%</value> <info>{suffix}</info>', 
          end='', style=style or STYLES)
    
    if iteration == total:
        print()


# Пример использования
if __name__ == "__main__":
    print("=== ДЕМОНСТРАЦИЯ СТАНДАРТНЫХ СТИЛЕЙ И ВЫРАВНИВАНИЯ ===")
    
    # Используем стандартные стили
    prinf("<h1>главный заголовок</h1>", style=STYLES)
    prinf("<h2>второстепенный заголовок</h2>", style=STYLES)
    
    prinf("<success>Успешная операция!</success>", style=STYLES)
    prinf("<error>Критическая ошибка!</error>", style=STYLES)
    prinf("<warning>Внимание: проверьте настройки</warning>", style=STYLES)
    prinf("<info>Информационное сообщение</info>", style=STYLES)
    
    # Выравнивание
    prinf("<center>Центрированный текст</center>", style=STYLES)
    prinf("<right>Текст по правому краю</right>", style=STYLES)
    prinf("<left>Текст по левому краю</left>", style=STYLES)
    
    # Специальные элементы
    prinf("<header>ЗАГОЛОВОК СЕКЦИИ</header>", style=STYLES)
    prinf("<footer>нижний колонтитул</footer>", style=STYLES)
    prinf("<menu>Главное меню</menu>", style=STYLES)
    prinf("<button>Кнопка действия</button>", style=STYLES)
    
    # Комбинирование
    prinf("<label>Имя пользователя:</label> <value>Дубровский</value>", style=STYLES)
    prinf("<code>print('Hello, World!')</code>", style=STYLES)
    prinf("<quote>Цитата великого человека</quote>", style=STYLES)
    
    print("\n" + "="*50)
    
    # Демонстрация таблицы
    print("ДЕМОНСТРАЦИЯ ТАБЛИЦЫ:")
    data: List[List[Any]] = [
        ["Яблоки", "15 кг", "150 руб"],
        ["Бананы", "8 кг", "320 руб"],
        ["Апельсины", "12 кг", "240 руб"]
    ]
    headers: List[str] = ["Товар", "Количество", "Стоимость"]
    prinf_table(data, headers, STYLES)
    
    print("\nДЕМОНСТРАЦИЯ ПРОГРЕСС-БАРА С ЦВЕТАМИ:")
    # Демонстрация прогресс-бара с цветами
    import time
    
    print("Прогресс с цветовой шкалой:")
    for i in range(101):
        prinf_progress(i, 100, prefix='Загрузка:', suffix='Выполнено', length=40, style=STYLES, color_scale=True)
        time.sleep(0.03)
    
    print("\nПрогресс без цветовой шкалы:")
    for i in range(101):
        prinf_progress(i, 100, prefix='Обработка:', suffix='Готово', length=30, style=STYLES, color_scale=False)
        time.sleep(0.02)
    
    print("\n" + "="*50)
    
    # Демонстрация разных этапов прогресса
    print("ДЕМОНСТРАЦИЯ РАЗНЫХ ЭТАПОВ ПРОГРЕССА:")
    
    test_stages = [10, 25, 49, 50, 74, 75, 99, 100]
    for stage in test_stages:
        prinf_progress(stage, 100, prefix=f'Этап {stage}%:', length=25, style=STYLES, color_scale=True)
        print()  # Новая строка после каждого этапа
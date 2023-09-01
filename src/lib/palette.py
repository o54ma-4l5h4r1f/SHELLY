# ANSI escape codes for text colors
COLORS = {
	'black': '30',
	'red': '31',
	'green': '32',
	'yellow': '33',
	'blue': '34',
	'magenta': '35',
	'cyan': '36',
	'white': '37',
	'reset': '0'
}

BACKGROUND = {
	'reset': 49,
    'black': 40,
    'red': 41,
    'green': 42,
    'yellow': 43,
    'blue': 44,
    'magenta': 45,
    'cyan': 46,
    'white': 47
}

STYLES = {
    'reset': 0,
    'bold': 1,
    'underline': 4,
    'invert': 7
}
	
def colorize(text, color='reset', style='reset', bg='reset'):
	color = color.lower()
	
	if color in COLORS:
		# {style_code};{color_code};{bg_color_code}
		return f"\033[{STYLES[style]};{COLORS[color]};{BACKGROUND[bg]}m{text}\033[{COLORS['reset']}m"
	else:
		return text
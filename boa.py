"""

CODE CLUSTERFUCK BELOW.
TAKE CARE!
LMAO, WARNED U

"""

import os
import re
import io
import sys
import contextlib
from bs4 import BeautifulSoup as BSoup
import html as pyhtml

# Source: https://stackoverflow.com/a/3906390/8041523
@contextlib.contextmanager
def get_stdout(stdout = None):
	old = sys.stdout
	if stdout is None:
		stdout = io.StringIO()
	sys.stdout = stdout
	yield stdout
	sys.stdout = old

class Boa(object):
	def __init__(self, caller = './', template_dir = 'templates'):
		caller = '/'.join(caller.split('/')[:-1])
		self.parent_directory = os.path.abspath(caller)
		self.template_directory = os.path.join(self.parent_directory, template_dir)
		
		self.bs4_parser = 'html.parser'

		self.open_tag = '{!'
		self.quick_print_prefix = '='
		self.close_tag = '!}'
		self.ignore_html_tag = 'boa-ignore'
		self.extends_html_tag = 'extends'
		self.block_html_tag = 'block'

		self.open_ignore_html_tag = '<{}>'.format(self.ignore_html_tag)
		self.close_ignore_html_tag = '</{}>'.format(self.ignore_html_tag)

	def escape(self, s):
		to_rep = {
			'\\': '\\\\',
			'\'': '\\\'',
			'"': '\\"'
		}
		r = s
		for k, v in to_rep.items():
			r = r.replace(k, v)
		return r

	def process_template(self, html):
		soup = BSoup(html, self.bs4_parser)
		extends = soup.find('extends')
		if not extends:
			return str(soup)
		parent_file = None
		if extends.has_attr('from'):
			parent_file = os.path.join(self.template_directory, extends['from'])
		else:
			raise Exception('Cannot extend from unspecified file.')
		if not os.path.exists(parent_file):
			raise FileNotFoundError('Template \'{}\' does not exist.'.format(parent_file))

		parent_html = ''
		with open(parent_file, 'r') as f:
			parent_html = f.read()

		parent_soup = BSoup(parent_html, self.bs4_parser)
		parent_html = self.process_template(str(parent_soup))
		parent_soup = BSoup(parent_html, self.bs4_parser)

		for block in soup.find_all('block'):
			if block.has_attr('id'):
				parent_block = parent_soup.find('block', {'id': block['id']})
				if parent_block:
					# Hack to get rid of <block></block>, only keep
					# inner HTML. Fuck you, BeautifulSoup!
					block_innerhtml = block.encode_contents().decode('utf-8')
					parent_block.replace_with(BSoup(str(block_innerhtml), self.bs4_parser))
		return str(parent_soup)

	def parse(self, html):
		output = ''
		code = ''
		text = ''
		is_ignoring = False
		indent = 0
		is_code = False
		ptr = 0

		def matches_tag(tag, offset = 0, custom_ptr = None):
			ptr_ = ptr
			if custom_ptr is not None:
				ptr_ = custom_ptr
			return html[ptr_ + offset:ptr_ + offset + len(tag)] == tag

		while ptr < len(html):
			if matches_tag(self.open_ignore_html_tag):
				is_ignoring = True
				ptr += len(self.open_ignore_html_tag)
			if matches_tag(self.close_ignore_html_tag):
				is_ignoring = False
				ptr += len(self.close_ignore_html_tag)
			if matches_tag(self.open_tag) and not is_ignoring:
				# Strip text if it breaks.
				if len(text) > 0:
					output += ('\t' * indent) + 'print(\'{}\', end = \'\')\n'.format(self.escape(text))
					text = ''
				is_code = True
				qk_prt = False
				code_fragment = ''
				j = ptr + len(self.open_tag)
				if html[j:j + len(self.quick_print_prefix)] == self.quick_print_prefix:
					j += len(self.quick_print_prefix) + 1
					qk_prt = True
				while True:
					if j >= len(html):
						raise Exception('Unclosed code block.')
					if matches_tag(self.close_tag, 1, j):
						is_code = False
						j += len(self.close_tag) + 1
						break
					code_fragment += html[j]
					j += 1
				code_result = ''
				for ln in code_fragment.split('\n'):
					ln = ln.strip().strip('\t').strip('\n')
					ln = pyhtml.unescape(ln)
					if len(ln) == 0: continue
					if ln.endswith(':') and (ln != 'else:' and not ln.startswith('elif')):
						code_result += ('\t' * indent) + ln + '\n'
						indent += 1
					elif (ln == 'else:' or ln.startswith('elif')):
						code_result += ('\t' * (indent - 1)) + ln + '\n'
					else:
						if ln == 'end':
							indent -= 1
							continue
						else:
							if qk_prt:
								ln = 'print(str({}), end = \'\')'.format(ln)#self.escape(ln))
							code_result += ('\t' * indent) + ln + '\n'
				if len(code_result.strip()) != 0:
					output += code_result.rstrip() + '\n'
				ptr = j
			if not is_code:
				c = html[ptr]
				if c != '\n':
					text += html[ptr]
				else:
					if len(text.rstrip()) != 0:
						output += ('\t' * indent) + 'print(\'{}\')\n'.format(self.escape(text))
						text = ''
			ptr += 1
		return output.strip()

	def render(self, template, request, **context):
		template = os.path.join(self.template_directory, template)
		if not os.path.exists(template):
			raise FileNotFoundError('Template \'{}\' does not exist.'.format(template))
		with open(template, 'r') as f:
			template_html = f.read()

			templated = self.process_template(template_html)

			pre_html = self.open_tag + '\n'
			pre_html += 'GET = {}\nPOST = {}\n'
			if request is not None:
				for k, v in request.args.items():
					pre_html += 'GET[\'{}\'] = \'{}\'\n'.format(k, v)
				for k, v in request.form.items():
					pre_html += 'POST[\'{}\'] = \'{}\'\n'.format(k, v)
				for k, v in context.items():
					pre_html += '{} = {}\n'.format(k, v)
				pre_html += '!}\n'
			templated = pre_html + templated

			parsed = self.parse(templated)
			with open('output.txt', 'w') as f:
				f.write(parsed)

			output = ''
			with get_stdout() as s:
			#	try:
				exec(parsed, globals())
				output = s.getvalue()
			#	except Exception as e:
			#		output = '500 Server Error\nException: {}'.format(e)
			return output
		raise Exception('Something went very wrong. :(')

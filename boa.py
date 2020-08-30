"""

WAIT!!!
YOU ARE ABOUT TO SEE SOME UGLY CODE WRITTEN IN ABOUT 3 HOURS.
DO NOT USE THIS IN PRODUCTION FOR THE LOVE OF GOD.
USE SOMETHING DECENT LIKE JINJA, FOR FUCKS SAKE!

Feel free to use, but give credit to the author
(@lucasrdrgs on GitHub) if redistributed and/or modified.

"""

import os
import io
import re
import sys
import string
import contextlib
from bs4 import BeautifulSoup as BSoup

"""
I got this from some stackoverflow answer, I should credit the author...
Edit: found it, it's https://stackoverflow.com/a/3906390
"""
@contextlib.contextmanager
def stdoutIO(stdout = None):
	old = sys.stdout
	if stdout is None:
		stdout = io.StringIO()
	sys.stdout = stdout
	yield stdout
	sys.stdout = old

"""
The main inspiration was Karrigell. Since it's a bit
limited, I made this :]
"""
class BoaRenderer(object):
	"""
	Parameter module is usually __file__. It is supposed to
	tell Boa where the directory of your templates
	is located at.
	"""
	def __init__(self, module = './'):
		self.parent_dir = '/'.join(module.split('/')[:-1])
		self.template_dir = 'templates'
		self.open_tag = '{!'
		self.close_tag = '!}'
		self.quick_print_prefix = '=' # quick print is done like so: open_tag+quick_print_prefix expression_to_print close_tag
		self.boa_ignore_tag = 'boa-ignore' # <boa-ignore>{! this is not run !}</boa-ignore>
		self.boa_ignore_open_tag = '<' + self.boa_ignore_tag + '>'
		self.boa_ignore_close_tag = '</' + self.boa_ignore_tag + '>'
		self.bs4_html_parser = 'lxml'
		self.templating = True

	def set_tags(self, open_tag = None, close_tag = None, boa_ignore_tag = None, quick_print_prefix = None):
		if open_tag:
			self.open_tag = open_tag
		if close_tag:
			self.close_tag = close_tag
		if boa_ignore_tag:
			self.boa_ignore_tag = 'boa-ignore'
			self.boa_ignore_open_tag = '<' + self.boa_ignore_tag + '>'
			self.boa_ignore_close_tag = '</' + self.boa_ignore_tag + '>'
		if quick_print_prefix:
			self.quick_print_prefix = quick_print_prefix

	def templating_toggle(enabled = True):
		self.templating = enabled

	def set_template_dir(self, new_dir):
		self.template_dir = new_dir

	def set_html_parser(parser = 'lxml'):
		self.bs4_html_parser = parser

	def render(self, template, request = None, **context):
		get_args = {}
		post_args = {}
		json_arg = {}
		if request:
			for arg in request.args:
				get_args[arg] = request.args[arg]
			for arg in request.form:
				post_args[arg] = request.form[arg]
			json_arg = request.get_json()
		self.get_args = get_args
		self.post_args = post_args
		self.json_arg = json_arg
		file = os.path.join(self.parent_dir, self.template_dir, template)
		if not os.path.exists(file):
			raise FileNotFoundError('Template \'{}\' does not exist.'.format(file))
		html = ''
		with open(file, 'r') as f:
			html = f.read()
		parsed = None
		if self.templating:
			parsed = self.parse_template_extensions(html)
		else:
			parsed = html
		final = self._render(parsed, context)
		return final

	def escape(self, c):
		if c == '\'':
			return '\\\''
		if c == '"':
			return '\\"'
		if c == '\\':
			return '\\\\'
		if c == '\n':
			return '\\n'
		return c

	def parse_template_extensions(self, html):
		soup = BSoup(html, self.bs4_html_parser)
		extends = soup.find('extends')
		if not extends:
			return str(soup)
		parent_file = None
		if extends.has_attr('from'):
			parent_file = os.path.join(self.parent_dir, self.template_dir, extends['from'])
		else:
			raise Exception('Cannot extend from unspecified file.')
		if not os.path.exists(parent_file):
			raise FileNotFoundError('Cannot extend from nonexisting file.')

		parent_html = open(parent_file, 'r').read()
		parent_soup = BSoup(parent_html, self.bs4_html_parser)
		parent_html = self.parse_template_extensions(str(parent_soup))
		parent_soup = BSoup(parent_html, self.bs4_html_parser)

		blocks = soup.find_all('block')
		if len(blocks) != 0:
			for block in blocks:
				if block.has_attr('id'):
					parent_block = parent_soup.find('block', {'id': block['id']})
					if parent_block:
						parent_block.replace_with(block.text)
		return str(parent_soup)

	def parse(self):
		pointer = 0
		indent = 0
		tmp_output = ''
		is_ignoring = False
		is_first_time = True # Make sure you add the first <<< print(' >>> only when it's not inside code.
		is_in_code = False
		is_double_code = False # {! code_a !}{! code_b !} is an example of double code
		while pointer < len(self.html):
			if self.html[pointer:pointer + len(self.boa_ignore_open_tag)] == self.boa_ignore_open_tag: # boa-ignore open, also handles close
				is_ignoring = True
				j = len(self.boa_ignore_open_tag)
				while True:
					k = pointer + j + 1
					if k >= len(self.html):
						raise Exception('Unclosed Boa ignore tag.')
					if self.html[k:k + len(self.boa_ignore_close_tag)] == self.boa_ignore_close_tag:
						pointer = k + len(self.boa_ignore_close_tag)
						if len(tmp_output.strip()) > 0:
							self.output += 'print(\'' + tmp_output + '\')\n'
						tmp_output = ''
						is_ignoring = False
						break
					tmp_output += self.escape(self.html[pointer + j])
					j += 1
			elif self.html[pointer:pointer + len(self.open_tag)] == self.open_tag and not is_in_code and not is_ignoring: # open tag, this also handles close tag and quick print
				is_quick_print = False
				if self.html[pointer + len(self.open_tag):pointer + len(self.open_tag) + len(self.quick_print_prefix)] == self.quick_print_prefix:
					is_quick_print = True
					pointer += 1
				if not is_double_code:
					is_double_code = True
				is_in_code = True
				pointer += len(self.open_tag)
				code_before = ''
				j = 0
				while True:
					k = pointer + j
					if k >= len(self.html):
						raise Exception('Unclosed open/quickprint tag somewhere!')
					if self.html[k + 1:k + len(self.close_tag) + 1] == self.close_tag:
						pointer += j + len(self.close_tag) + 1
						is_in_code = False
						code_before += self.html[k]
						if not is_quick_print:
							pointer += 1
						break
					code_before += self.html[k]
					j += 1
				lines = code_before.split('\n')
				code_after = ''
				for line in lines:
					line = line.strip().strip('\t')
					if len(line) == 0: continue
					if line == 'end':
						indent -= 1
						if indent < 0:
							raise Exception('Cannot have negative indentation.')
					else:
						code_after += ('\t' * indent) 
						if not is_quick_print:
							code_after += line
						else:
							code_after += 'print(str(' + line + '))'
						code_after += '\n'
						if line.endswith(':') or ':'.join(line.split(':')[-1:]).rstrip().endswith(self.close_tag):
							indent += 1
				if len(tmp_output.strip()) > 0:
					self.output += 'print(\'' + tmp_output + '\')\n'
					tmp_output = ''
				self.output += code_after
				continue
			else:
				if self.html[pointer] == '\n' and not is_in_code and not is_double_code:
					if len(tmp_output.strip()) > 0:
						self.output += 'print(\'' + tmp_output + '\')\n'
						tmp_output = ''
						pointer += 1
						continue
				tmp_output += self.escape(self.html[pointer])
				is_double_code = False
			pointer += 1

	def _render(self, html, context):
		self.output = ''
		self.html = html + '\n'

		# Add context and request parameters
		new_html = self.open_tag + '\n'
		new_html += '__GET__ = {}\n'
		new_html += '__POST__ = {}\n'
		for k in context:
			fmt = context[k]
			if isinstance(fmt, str):
				fmt = '\'' + fmt + '\''
			new_html += k + ' = ' + str(fmt) + '\n'
		for arg in self.get_args:
			fmt = self.get_args[arg]
			if isinstance(fmt, str):
				fmt = '\'' + fmt + '\''
			new_html += '__GET__[\'' + arg + '\'] = ' + str(fmt) + '\n'
		for arg in self.post_args:
			fmt = self.post_args[arg]
			if isinstance(fmt, str):
				fmt = '\'' + fmt + '\''
			new_html += '__POST__[\'' + arg + '\'] = ' + str(fmt) + '\n'
		# TODO: add JSON... support?
		new_html  += self.close_tag + '\n'
		self.html = new_html + self.html
		self.html = self.html.replace('\n\r', '\n')

		self.parse()

		with stdoutIO() as s:
			exec(self.output, globals())
			return s.getvalue()

		raise Exception('Something went wrong :(')

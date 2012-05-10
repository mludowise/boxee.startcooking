##
# The functions below were copied from http://effbot.org/zone/re-sub.htm
# in accordance with the copyright information on that site
# http://effbot.org/zone/copyright.htm
##

import re, htmlentitydefs, sre, sys

##
# Removes HTML markup from a text string.
#
# @param text The HTML source.
# @return The plain text.  If the HTML source contains non-ASCII
#	 entities or character references, this is a Unicode string.

def strip_html(text):
	def fixup(m):
		text = m.group(0)
		if text[:1] == "<":
			return "" # ignore tags
		if text[:2] == "&#":
			try:
				if text[:3] == "&#x":
					return unichr(int(text[3:-1], 16))
				else:
					return unichr(int(text[2:-1]))
			except ValueError:
				pass
		elif text[:1] == "&":
			import htmlentitydefs
			entity = htmlentitydefs.entitydefs.get(text[1:-1])
			if entity:
				if entity[:2] == "&#":
					try:
						return unichr(int(entity[2:-1]))
					except ValueError:
						pass
				else:
					return unicode(entity, "iso-8859-1")
		return text # leave as is
	return re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text)

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
	def fixup(m):
		text = m.group(0)
		if text[:2] == "&#":
			# character reference
			try:
				if text[:3] == "&#x":
					return unichr(int(text[3:-1], 16))
				else:
					return unichr(int(text[2:-1]))
			except ValueError:
				pass
		else:
			# named entity
			try:
				text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
			except KeyError:
				pass
		return text # leave as is
	return re.sub("&#?\w+;", fixup, text)

# match $var and ${var} and $$
_dosub = sre.compile(r'\$(?:\$|(\w+)|\{([^}]*)\})').sub

def expandvars(string, vars):
	# expand $var and ${var}; leave unknowns as is
	def repl(m, vars=vars):
		if not m.lastindex:
			return "$"
		try:
			return vars[m.group(m.lastindex)]
		except (KeyError, NameError):
			return m.group(0)
	return _dosub(repl, string)

def replacevars(string, vars):
	# same as expandvars, but raises an exception if variable not known
	def repl(m, vars=vars):
		if not m.lastindex:
			return "$"
		return vars[m.group(m.lastindex)]
	return _dosub(repl, string)

def replacevars_from_scope(string):
	# same as replacevars, but gets the variables from caller's local scope
	frame = sys._getframe(1)
	mapping = frame.f_globals.copy()
	mapping.update(frame.f_locals)
	return replacevars(string, mapping)

def re_quote(string, sub=re.compile(r"[\\\"]").sub):
	def fixup(m):
		return "\\" + m.group(0)
	return sub(fixup, string)

def re_unquote(string, sub=re.compile(r"(?s)\\(.)|\\").sub):
	def fixup(m):
		ch = m.group(1)
		if ch is None:
			raise ValueError("backslash at end of string")
		if ch not in r"\\\"":
			raise ValueError("unsupported character after backslash")
		return ch
	return sub(fixup, string)

# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
	_ST3 = False
else:
	_ST3 = True

from pdfBuilder import PdfBuilder
import sublime_plugin
import os, os.path
import codecs

DEBUG = False

DEFAULT_COMMAND_UNICES = ["latexmk", "-cd",
				"-e", "$pdflatex = '%E -interaction=nonstopmode -synctex=1 %S %O'",
				"-f", "-pdf"]

DEFAULT_COMMAND_WINDOWS = ["texify", 
					"-b", "-p",
					"--tex-option=\"--synctex=1\""]


#----------------------------------------------------------------
# TraditionalBuilder class
#
# Implement existing functionality, more or less
# NOTE: move this to a different file, too
#
class TraditionalBuilder(PdfBuilder):

	def __init__(self, tex_root, output, prefs):
		# Sets the file name parts, plus internal stuff
		super(TraditionalBuilder, self).__init__(tex_root, output, prefs) 
		# Now do our own initialization: set our name
		self.name = "Traditional Builder"
		# Display output?
		self.display_log = prefs.get("display_log", False)
		# Build command, with reasonable defaults
		if sublime.platform() == 'windows':
			default_command = DEFAULT_COMMAND_WINDOWS
		else: # osx, linux
			default_command = DEFAULT_COMMAND_UNICES
		self.cmd = prefs.get("command", default_command)
		# Default tex engine (pdflatex if none specified)
		self.engine = prefs.get("program", "pdflatex")
		# Sanity check: if "strange" engine, default to pdflatex but give message
		if not(self.engine in ['pdflatex', 'xelatex', 'lualatex']):
			self.engine = 'pdflatex'
			sublime.error_message("Unknown engine specified in preferences;\n" \
								  "defaulting to pdflatex.")
		# See if the root file specifies a custom engine
		for line in codecs.open(self.tex_root, "r", "UTF-8", "ignore").readlines():
			if not line.startswith('%'):
				break
			else:
				# We have a comment match; check for a TS-program match
				mroot = re.match(r"%\s*!TEX\s+(?:TS-)?program *= *(xelatex|lualatex|pdflatex)\s*$",line)
				if mroot:
					# Sanity checks
					if "texify" == self.cmd[0]:
						sublime.error_message("Sorry, cannot select engine using a %!TEX program directive on MikTeX.\n"\
											  "Running with default engine.")
						break 
					if not ("$pdflatex\s?=\s?'%E" in self.cmd[3]): # fixup blanks (linux)
						sublime.error_message("You are using a custom LaTeX.sublime-build file (in User maybe?). Cannot select engine using a %!TEX program directive.")
						break
					self.engine = mroot.group(1)
					break
		if self.engine != 'pdflatex': # Since pdflatex is standard, we do not output a msg. for it.
			self.output("Using engine " + self.engine + "\n")
		self.cmd[3] = self.cmd[3].replace("%E", self.engine)

	#
	# Very simple here: we yield a single command
	#
	def commands(self):
		# Print greeting
		self.display("\n\nTraditionalBuilder: ")

		yield (self.cmd + [self.base_name], "invoking " + self.cmd[0] + "... ")

		self.display("done.\n")
		
		# This is for debugging purposes 
		if self.display_log:
			self.display("\nCommand results:\n")
			self.display(self.out)
			self.display("\n\n")	
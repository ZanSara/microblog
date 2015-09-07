# Wrapper for moment.js that we can invoke from the templates.
# Note that the render method does not directly return a string but instead wraps the string inside a Markup object provided by Jinja2.
# The reason is that Jinja2 escapes all strings by default, so for example, our <script> tag will arrive as &lt;script&gt; .
# Wrapping the string in a Markup object tells Jinja2 that this string should not be escaped.

from jinja2 import Markup

class momentjs(object):
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def render(self, format):
        return Markup("<script>\ndocument.write(moment(\"%s\").%s);\n</script>" % (self.timestamp.strftime("%Y-%m-%dT%H:%M:%S Z"), format))

    def format(self, fmt):
        return self.render("format(\"%s\")" % fmt)

    def calendar(self):
        return self.render("calendar()")

    def fromNow(self):
        return self.render("fromNow()")

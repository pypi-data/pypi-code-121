# -*- coding: utf-8 -*-

import collections

from django.utils.safestring import mark_safe

import markdown



class TransformParagraph(object):

    def __init__(self, story):
        self.story = story
        self.content_defaults = collections.OrderedDict()

    def run_content_processors(self, tags, text):
        ntags = collections.OrderedDict()
        unused = []
        for name, comp, value in tags:
            if comp in ("<<", ">>"):
                ntags[name] = (name, comp, value)
            else:
                unused.append((name, comp, value))

        for name, value in self.content_defaults.items():
            ntags.setdefault(name, value)

        images = {}
        for image in self.story.image_set.all():
            images["images/" + image.name] = "<img src='{}' alt=''>".format(
                image.full_url,
                image.name
            )

        text = text.format(**images)

        for name, comp, value in ntags.values():
            try:
                func = getattr(self, "content_" + name, None)
                if func:
                    text = func(text, name, comp, value)
                else:
                    unused.append((name, comp, value))
            except Exception as ex:
                import traceback
                traceback.print_exc()
                print("EXCEPTION:", ex)

        return (
            unused,
            mark_safe(markdown.markdown(text.strip()).strip())
        )

    def get_image_url(self, name):
        try:
            return Image.objects.get(story=self.story, name=name).full_url
        except Image.DoesNotExist:
            return ""

    def startswith_any(self, s, chars):
        return any([s.startswith(c) for c in chars])

    def endswith_any(self, s, chars):
        return any([s.endswith(c) for c in chars])

    ## content processores ###################################################

    def content_char(self, text, name, comp, value):

        if self.startswith_any(text, ['"', u"“"]) and \
                self.endswith_any(text, ['"', u"”"]):
            text = self.content_quote(text[1:-1], name, comp, value)
        elif self.startswith_any(text, ['<']) and \
                self.endswith_any(text, ['>']):
            text = self.content_thought(text[1:-1], name, comp, value)
        else:
            text = self.content_narration(text, name, comp, value)

        text = u"""<p class="plain"><image src="{image}" class="{direction}"></p>
{text}""".format(
            text=text,
            image=self.get_image_url(value),
            direction=comp == ">>" and "right" or "left"
        )

        self.content_defaults[name] = (name, comp, value)

        return text

    def content_quote(self, text, name, comp, value):
        return u"""<blockquote class="{direction}">{text}</blockquote>""".format(
            text=text,
            direction=comp == ">>" and "right" or "left"
        )

    def content_thought(self, text, name, comp, value):
        return u"""<blockquote class="thought {direction}">{text}</blockquote>""".format(
            text=text,
            direction=comp == ">>" and "right" or "left"
        )

    def content_narration(self, text, name, comp, value):
        return u"""<p class="{direction}">{text}</p>""".format(
            text=text,
            direction={
                ">>": "right",
                "<<": "left",
            }.get(comp, "")
        )

    def content_image(self, text, name, comp, value):
        return u"""<p class="plain"><image src="{image}"></p>\n
{text}""".format(
            text=text,
            image=self.get_image_url(value),
        )

from .models import Image

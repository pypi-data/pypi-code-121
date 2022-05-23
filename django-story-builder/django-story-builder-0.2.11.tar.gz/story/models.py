import base64
import json

from django.conf import settings
from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.db import models
from django.utils.safestring import mark_safe

import markdown


class Image(models.Model):
    story = models.ForeignKey("Story", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    image = models.ImageField(
        upload_to="content/%Y/%m/", blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def full_url(self):
        site = Site.objects.get_current()
        if self.image.url.startswith("http"):
            return self.image.url
        else:
            return "http://{}{}".format(site.domain, self.image.url)


class Story(models.Model):
    ordering = models.SmallIntegerField(default=1)
    name = models.CharField(max_length=255)
    short_description = models.CharField(blank=True, null=True, max_length=80)
    splash = models.ImageField(upload_to="content/%Y/%m/", blank=True, null=True)

    starting_scene = models.ForeignKey(
        "Scene", null=True, blank=True, related_name="starting",
        on_delete=models.SET_NULL)

    class Meta:
        verbose_name_plural = "Stories"
        ordering = ("ordering", "name")

    def __str__(self):
        return self.name

    @property
    def cache_key(self):
        return "story-2-{}".format(self.id)

    def to_dict(self):
        site = Site.objects.get_current()
        splash = None
        try:
            splash = "http://{}{}".format(site.domain, self.splash.url)
        except ValueError:
            pass
        dataset = dict(
            id=self.pk,
            meta=dict(
                name=self.name,
                short_description=self.short_description,
                splash=splash,
                start=self.starting_scene_id,
            ),
            media=[i.full_url for i in self.image_set.all()]
        )
        scenes = []
        for scene in self.scene_set.order_by("id"):
            scenes.append(scene.to_dict())
        dataset['scenes'] = scenes
        return dataset

    def to_json(self):
        # dataset = cache.get(self.cache_key)
        # if settings.DEBUG or not dataset:
        dataset = self.to_dict()
        # cache.set(self.cache_key, dataset, 60 * 60 * 4)
        return json.dumps(dataset)


class Scene(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    image = models.ForeignKey(
        Image, verbose_name="Background Image", null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return u"{name}".format(
            story=self.story,
            name=self.name or u"#{}".format(self.id))

    def to_dict(self):
        from .content_processors import TransformParagraph
        tp = TransformParagraph(self.story)
        return dict(
            meta=dict(
                id=self.id,
                name=self.name
            ),
            image=self.image and self.image.full_url or None,
            content=[c.to_dict(tp) for c in self.content_set.all()],
            choices=[c.to_dict() for c in self.links_from.all()],
        )


class RequiredTag(models.Model):
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey()

    tag = models.CharField(max_length=50)
    comparison = models.CharField(max_length=10, choices=(
        (">", ">"),
        ("<", "<"),
        ("=", "=")
    ), default=">=")
    value = models.CharField(max_length=50)

    def __str__(self):
        return self.tag


class Content(models.Model):
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    ordering = models.SmallIntegerField(default=0)

    # grouping content will make only one show, whichever has the highest
    # ordering and matches the character tags
    group = models.CharField(max_length=50, default="default")
    tags = GenericRelation(RequiredTag)
    text = models.TextField()
    audio = models.FileField(upload_to="content/%Y/%m/", null=True, blank=True)

    class Meta:
        verbose_name_plural = "Content"
        ordering = ("ordering", "id")

    def __str__(self):
        return u"{}: {}".format(self.scene, self.text[:25] + u"...")

    @property
    def formatted_text(self):

        return mark_safe(markdown.markdown(self.text))

    @property
    def image_data_url(self):
        if self.image:
            return "data:image/png;base64,{}".format(
                base64.b64encode(self.image.image.read())
            )
        return None

    def to_dict(self, tp):
        if not tp:
            tp = TransformParagraph(self.scene.story)

        tags, text = tp.run_content_processors(
            list(self.tags.values_list("tag", "comparison", "value")),
            self.text
        )

        audio = None
        if self.audio:
            site = Site.objects.get_current()
            if self.audio.url.startswith("http"):
                audio = self.audio.url
            else:
                audio = "http://{}{}".format(site.domain, self.audio.url)

        return dict(
            text=text,
            audio=audio,
            tags=[dict(tag=n, comparison=c, value=v) for n, c, v in tags]
        )


class Choice(models.Model):
    scene = models.ForeignKey(Scene, related_name="links_from", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    next_scene = models.ForeignKey(
        Scene, related_name="links_to", blank=True, null=True, on_delete=models.CASCADE)
    tags = GenericRelation(RequiredTag)

    def __str__(self):
        return u"{}: {}".format(self.scene, self.text[:25] + u"...")

    @property
    def formatted_text(self):
        tp = TransformParagraph(self.scene.story)

        tags, text = tp.run_content_processors(
            list(self.tags.values_list("tag", "comparison", "value")),
            self.text
        )

        # strip off the paragraph tags
        return text[3:-4]

    def to_dict(self):
        return dict(
            text=self.formatted_text,
            next_scene=self.next_scene_id,
            tags=list(self.tags.values("tag", "comparison", "value")),
            consequences=list(self.consequenceattribute_set.values(
                "tag", "value"
            ))
        )

    # def link(self):
    #     if self.next_scene:
    #         return resolve_url


class Consequence(models.Model):
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    module = models.CharField(max_length=255)


class ConsequenceAttribute(models.Model):
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    tag = models.CharField(max_length=50)
    value = models.SmallIntegerField(default=1)


# this requires Image
from .content_processors import TransformParagraph  # isort:skip

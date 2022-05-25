# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Gallery.random'
        db.add_column('galleryserve_gallery', 'random',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Gallery.random'
        db.delete_column('galleryserve_gallery', 'random')


    models = {
        'galleryserve.gallery': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Gallery'},
            'height': ('django.db.models.fields.IntegerField', [], {'default': '600', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quality': ('django.db.models.fields.IntegerField', [], {'default': '85'}),
            'random': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'resize': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'width': ('django.db.models.fields.IntegerField', [], {'default': '800', 'blank': 'True'})
        },
        'galleryserve.item': {
            'Meta': {'ordering': "('sort',)", 'object_name': 'Item'},
            'alt': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'credit': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'gallery': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['galleryserve.Gallery']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'video_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['galleryserve']
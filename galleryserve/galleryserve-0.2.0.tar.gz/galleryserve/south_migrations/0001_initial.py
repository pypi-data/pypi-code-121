# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Gallery'
        db.create_table('galleryserve_gallery', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('height', self.gf('django.db.models.fields.IntegerField')(default=600, blank=True)),
            ('width', self.gf('django.db.models.fields.IntegerField')(default=800, blank=True)),
            ('resize', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('quality', self.gf('django.db.models.fields.IntegerField')(default=85)),
        ))
        db.send_create_signal('galleryserve', ['Gallery'])

        # Adding model 'Item'
        db.create_table('galleryserve_item', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('gallery', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['galleryserve.Gallery'])),
            ('alt', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('credit', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('video_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('sort', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('galleryserve', ['Item'])


    def backwards(self, orm):
        # Deleting model 'Gallery'
        db.delete_table('galleryserve_gallery')

        # Deleting model 'Item'
        db.delete_table('galleryserve_item')


    models = {
        'galleryserve.gallery': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Gallery'},
            'height': ('django.db.models.fields.IntegerField', [], {'default': '600', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quality': ('django.db.models.fields.IntegerField', [], {'default': '85'}),
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
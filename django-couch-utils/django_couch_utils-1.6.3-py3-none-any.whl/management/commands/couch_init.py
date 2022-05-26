# -*- coding: utf-8 -*-

import sys
from django.core.management.base import BaseCommand
from django.conf import settings

import django_couch
from couchdbcurl.client import ResourceConflict

class Command(BaseCommand):

    help = u'Creates basic views: types and auth'
    
    def execute(self, db_key, *args, **options):
        
        db = django_couch.db(db_key)
        
        if not args or 'types' in args:
            print "Creating types/list view"
            try:
                db['_design/types'] = {
                    'language': 'javascript',
                    'views': {
                        'list': {
                            'map': "function(doc) {\n  emit(doc.type, 1\t);\n}",
                            'reduce': "function(keys, values) {\n  return sum(values);\n}"
                        }
                    }
                }
                print "  Done"
            except ResourceConflict:
                print "  Can't create: conflict"

        if not args or 'auth' in args:
            print "Creating auth/admins view"
            try:
                db['_design/auth'] = {
                    'language': 'javascript',
                    'views': {
                        'admins': {
                            'map': "function(doc) {\n  if ((doc.type == 'user') && (doc.admin)) {\t\n    emit(doc.username, doc.password);\n  }\t\n}",
                            },
                        "list": {
                            'map': "function(doc) {\n  if ((doc.type == 'user')) {\n    emit(doc.username, doc.password);\n  }\n}"}}
                }
                print "  Done"
            except ResourceConflict:
                print "  Can't create: conflict"

        
        
            



        

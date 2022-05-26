# -*- coding: utf-8 -*-

from datetime import datetime
import urlparse

import django_couch
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib import messages

from forms import *

CONFIG_ID = 'cluster_config'
    

@user_passes_test(lambda u: u.get("is_superuser"))
def nodes(request):

    nodes = request.db_cluster.view('nodes/list', include_docs=True).rows
    
    return render(request, 'cluster/nodes.html', {
        'nodes': nodes,
    })


@user_passes_test(lambda u: u.get("is_superuser"))
def node_edit(request, node_id=None):

    if node_id:
        node = request.db_cluster[node_id]
        assert node.type == 'node'
    else:
        node = django_couch.Document(_db=request.db_cluster,
                                     type='node',
                                     date_created=datetime.today().strftime(settings.DATETIME_FMT),
                                     enabled=True,
                                     )

    if request.method == "POST":
        form = NodeEditForm(request.POST, initial=node)
        if form.is_valid():
            node.update(form.cleaned_data)

            if node.id:
                node.save()
            else:
                node.create('n_%s' % node.hostname)

            return redirect('cluster:nodes')
    else:
        form = NodeEditForm(initial=node)
    
    
    return render(request, 'cluster/node_edit.html', {
        'node': node,
        'form': form,
    })



@user_passes_test(lambda u: u.get("is_superuser"))
def node(request, node_id):

    config = request.db_cluster[CONFIG_ID]

    def security_check(security, config):
        
        s = dict(security)
        
        return s == config.security
    
    node = request.db_cluster[node_id]
    assert node.type == 'node'
    
    db_info = {
    }
    
    db_nodes = [row.key for row in request.db_cluster.view('nodes/db').rows if row.key != node.hostname]
    
    if node.is_db:
        server = django_couch.Server('http://%s:%s@%s:5984' % (str(node.admin_username), str(node.admin_password), str(node.hostname)))
        
        db_info['databases'] = []
        
        
        
        for db in config.databases:
            try:
                info = server[db].info()
            except django_couch.ResourceNotFound:
                info = None
                
            if info:
                security = server[db]['_security']
                security_correct = security_check(security, config)
            else:
                security = None
                security_correct = None
            
            
            db_info['databases'].append((db, info, security, security_correct))

        db_info['tasks'] = server.tasks()
        
        try:
            db_info['replications'] = server['_replicator'].view('status/list', reduce=False, include_docs=True).rows
        except django_couch.ResourceNotFound:
            db_info['replications_error'] = 'not_found'
            db_info['replications'] = []
        
        
        db_info['permutations'] = []
        for hostname in db_nodes:
            for db in config.databases:
                db_info['permutations'].append({
                    'hostname': hostname,
                    'db': db,
                })

        for perm in db_info['permutations']:
            for replication in db_info['replications']:
                u = urlparse.urlparse(replication.doc.source)
                if u.hostname == perm['hostname'] and u.path.lstrip('/') == perm['db'] and replication.doc.target == perm['db']:
                    perm['status'] = replication.key
        
        

        
    return render(request, 'cluster/node.html', {
        'node': node,
        'db_info': db_info,
    })


@require_POST
@user_passes_test(lambda u: u.get("is_superuser"))
def node_actions(request, node_id):

    node = request.db_cluster[node_id]
    assert node.type == 'node' and node.is_db, "Invalid node id supplied"

    config = request.db_cluster[CONFIG_ID]

    cmd = request.POST['cmd']
    server = django_couch.Server('http://%s:%s@%s:5984' % (str(node.admin_username), str(node.admin_password), str(node.hostname)))
    
    if cmd == 'replication_create':
        
        hostname = request.POST['hostname']
        
        db_nodes = [row.key for row in request.db_cluster.view('nodes/db').rows if row.key != node.hostname]
        assert hostname in db_nodes, "Invalid source hostname supplied"
        
        db = request.POST['db']
        assert db in config.databases, "Invalid DB supplied"
        
        
        
        try:
            source_node = request.db_cluster.view('nodes/db', key=hostname, include_docs=True).rows[0].doc
        except django_couch.ResourceNotFound:
            raise Http404("Source not found")

        source = 'http://%s:%s@%s:5984/%s' % (source_node.replica_username, source_node.replica_password, source_node.hostname, db)

        doc = {
            'source': source,
            'target': db,
            'continuous': True,
            'user_ctx': {"roles": ["_admin"]},
        }
        
        msg = u'Replication started from %s/%s to %s' % (hostname, db, node.hostname)
        messages.info(request, msg)
        
        doc_id = '%s_%s' % (hostname, db)
        
        if doc_id in server['_replicator']:
            del(server['_replicator'][doc_id])
            
        server['_replicator'][doc_id] = doc
        
        
    elif cmd == 'security_fix':
        db = request.POST['db']
        assert db in config.databases, "Invalid DB supplied"

        msg = u'Security doc updated for %s at %s' % (db, node.hostname)
        messages.info(request, msg)
            
        # we need to copy, because it may be modified by couchdbcurl library
        server[db]['_security'] = config.security.copy()

    elif cmd == 'replication_view_create':

        doc = {
            "language": "javascript",
            "views": {
                "list": {
                    "map": "function(doc) {\t\n  emit(doc._replication_state, null);\n}",
                    "reduce": "_count"
                }
            }
        }
        
        doc_id = '_design/status'
        
        server['_replicator'][doc_id] = doc
        
        msg = u'Replications status view created at %s' % (node.hostname)
        messages.info(request, msg)

    elif cmd == 'db_create':
        db = request.POST['db']
        assert db in config.databases, "Invalid DB supplied"

        assert not db in server, "Database already exists"
        
        server.create(db)
        
        msg = u'Database %s created at %s' % (db, node.hostname)
        messages.info(request, msg)
        
        
        
    return redirect('cluster:node', node.id)



@user_passes_test(lambda u: u.get("is_superuser"))
def config(request):
    
    if not CONFIG_ID in request.db_cluster:
        request.db_cluster[CONFIG_ID] = {
            'databases': [],
            'security': {
                'admins': {
                    'names': [],
                    'roles': [],
                },
                'members': {
                    'names': [],
                    'roles': [],
                },
            },
        }
    
    nodes_config = request.db_cluster[CONFIG_ID]
    

    if request.method == "POST":
        form = ConfigForm(request.POST, initial=nodes_config.copy())

        if form.is_valid():
            nodes_config.update(form.cleaned_data)

            pprint(nodes_config)
            nodes_config.save()

            return redirect(request.path)
    else:
        form = ConfigForm(initial=nodes_config.copy())
        
    
    return render(request, 'cluster/config.html', {
        'nodes_config': nodes_config,
        'form': form,
    })


def setup_settings(settings, **kwargs):

    settings['CSS_COMPONENTS'] = {
        'admin': [
            'cap/components/bootstrap/bootstrap.min.css',
            'cap/components/jquery-ui/jquery-ui.min.css',
            'cap/components/font-awesome/font-awesome.min.css',
            'cap/components/qtip2/jquery.qtip.min.css',
            'cap/components/fancybox/jquery.fancybox.min.css',
            'cap/components/bootstrap-treeview/bootstrap-treeview.min.css',
            'cap/components/bootstrap-tagsinput/bootstrap-tagsinput.css',
            'cap/css/common.css',
            'cap/css/sidebar.css'
        ],
        **settings.get('CSS_COMPONENTS', {})
    }

    settings['JS_COMPONENTS'] = {
        'admin': [
            'cap/components/jquery.min.js',
            'cap/components/jquery.form.min.js',
            'cap/components/jquery.cookie.js',
            'cap/components/bootstrap/bootstrap.min.js',
            'cap/components/bootstrap-treeview/bootstrap-treeview.min.js',
            'cap/components/fancybox/jquery.fancybox.min.js',
            'cap/components/qtip2/jquery.qtip.min.js',
            'cap/components/bootstrap-tagsinput/bootstrap-tagsinput.js',
            'jquery/jquery.ba-bbq.js',
            'jquery/ajax-csrf.js',
            'cap/components/jquery-ui/jquery-ui.min.js',
            'cap/js/sidebar.js'
        ],
        **settings.get('JS_COMPONENTS', {})
    }

    settings['INSTALLED_APPS'] += [
        app for app in [
            'cap.configs.SuitConfig',
            'django.contrib.admin.apps.SimpleAdminConfig',
            'notify',
            'djforms',
            'adminplus',
            'adminsortable2',
            'rangefilter'
        ] if app not in settings['INSTALLED_APPS']
    ]

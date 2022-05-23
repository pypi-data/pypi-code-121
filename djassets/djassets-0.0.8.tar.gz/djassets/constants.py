
BC = 'bower_components/'

STATIC_APPS_MAP = {
    'jquery': {
        'bower': [
            'jquery#3.5.1',
            'jquery-form#4.3.0'
        ],
        'js': [
            BC + 'jquery/dist/jquery.js',
            BC + 'jquery-form/dist/jquery.form.min.js',
            'jquery/jquery.ba-bbq.js',
            'jquery/ajax-csrf.js',
            'modal.js'
        ]
    },
    'bootstrap': {
        'bower': 'bootstrap#3.3.7',
        'css': BC + 'bootstrap/dist/css/bootstrap.css',
        'js': BC + 'bootstrap/dist/js/bootstrap.js'
    },
    'bootstrap5': {
        'bower': 'bootstrap',
        'css': BC + 'bootstrap/dist/css/bootstrap.css',
        'js': BC + 'bootstrap/dist/js/bootstrap.js'
    },
    'jasny': {
        'bower': 'jasny-bootstrap#3.1.3',
        'css': BC + 'jasny-bootstrap/dist/css/jasny-bootstrap.css',
        'js': BC + 'jasny-bootstrap/dist/js/jasny-bootstrap.js'
    },
    'fa': {
        'bower': 'components-font-awesome#5.15.1',
        'css': BC + 'components-font-awesome/css/all.css'
    },
    'chosen': {
        'bower': 'chosen#1.8.7',
        'css': BC + 'chosen/chosen.css',
        'js': BC + 'chosen/chosen.jquery.js'
    },
    'fancybox': {
        'bower': 'fancybox#3.5.7',
        'css': BC + 'fancybox/dist/jquery.fancybox.css',
        'js': BC + 'fancybox/dist/jquery.fancybox.js'
    },
    'fancybox2': {
        'bower': 'fancybox#2.1.6',
        'css': BC + 'fancybox/source/jquery.fancybox.css',
        'js': BC + 'fancybox/source/jquery.fancybox.js'
    },
    'bootstrap-theme': {
        'css': BC + 'bootstrap/dist/css/bootstrap-theme.css'
    },
    'pgwslideshow': {
        'bower': 'pgwslideshow#2.0.2',
        'css': [
            BC + 'pgwslideshow/pgwslideshow.css',
            BC + 'pgwslideshow/pgwslideshow_light.css'
        ],
        'js': BC + 'pgwslideshow/pgwslideshow.js'
    },
    'owl': {
        'bower': 'owl.carousel#2.3.4',
        'css': BC + 'owl.carousel/dist/assets/owl.carousel.css',
        'js': BC + 'owl.carousel/dist/owl.carousel.js'
    },
    'autocomplete': {
        'bower': 'devbridge-autocomplete#1.4.11',
        'js': (
            BC + 'devbridge-autocomplete/'
            'dist/jquery.autocomplete.js'
        )
    },
    'tagsinput': {
        'bower': 'bootstrap-tagsinput#0.8.0',
        'css': (
            BC + 'bootstrap-tagsinput/dist/bootstrap-tagsinput.css'
        ),
        'js': (
            BC + 'bootstrap-tagsinput/dist/bootstrap-tagsinput.js')
    },
    'qtip2': {
        'bower': 'qtip2#2.2.1',
        'css': BC + 'qtip2/basic/jquery.qtip.css',
        'js': BC + 'qtip2/basic/jquery.qtip.js'
    },
    'cookie': {
        'bower': 'jquery.cookie#1.4.1',
        'js': BC + 'jquery.cookie/jquery.cookie.js'
    },
    'jquery-ui': {
        'bower': 'jquery-ui#1.12.1',
        'css': BC + 'jquery-ui/themes/ui-lightness/jquery-ui.css',
        'js': [
            BC + 'jquery-ui/jquery-ui.js',
            BC + 'jquery-ui/ui/i18n/datepicker-uk.js',
        ]
    },
    'treeview': {
        'bower': 'bootstrap-treeview#1.2.0',
        'css': (
            BC + 'bootstrap-treeview/'
            'dist/bootstrap-treeview.min.css'
        ),
        'js': (
            BC + 'bootstrap-treeview/'
            'dist/bootstrap-treeview.min.js'
        )
    },
    'slick': {
        'bower': 'slick-carousel#1.8.1',
        'css': [
            BC + 'slick-carousel/slick/slick.css',
            BC + 'slick-carousel/slick/slick-theme.css'
        ],
        'js': BC + 'slick-carousel/slick/slick.js'
    },
    'range-slider': {
        'bower': 'seiyria-bootstrap-slider#11.0.2',
        'css': [
            BC + 'seiyria-bootstrap-slider/dist/css/bootstrap-slider.css'
        ],
        'js': [
            BC + 'seiyria-bootstrap-slider/dist/bootstrap-slider.js',
            'range-slider.js'
        ]
    },
    'zoom': {
        'bower': 'jquery-zoom#1.7.21',
        'js': BC + 'jquery-zoom/jquery.zoom.js'
    },
    'basement': {
        'css': 'css/indents.css'
    }
}

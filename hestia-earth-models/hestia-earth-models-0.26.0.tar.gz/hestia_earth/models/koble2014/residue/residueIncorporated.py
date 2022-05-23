REQUIREMENTS = {
    "Cycle": {
        "dataCompleteness.cropResidue": "False",
        "products": {
            "@type": "Product",
            "primary": "True",
            "term.termType": "crop",
            "value": "> 0"
        },
        "site": {
            "@type": "Site",
            "country": ""
        }
    }
}
RETURNS = {}
TERM_ID = 'residueIncorporated'


def run(*args): return None

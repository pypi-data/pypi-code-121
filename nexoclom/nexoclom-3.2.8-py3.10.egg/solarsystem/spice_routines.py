import os
import spiceypy as spice
from bs4 import BeautifulSoup
import requests
from nexoclom import __datapath__


def load_kernels():
    """Load generic spice kernels. Retrieves if necessary."""
    # leap second kernel
    url = 'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/'
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    
    for node in soup.find_all('a'):
        text = node.get('href')
        if (text is not None) and (text.endswith('.tls')):
        
    lsk_url = [url + '/' + node.get('href')
               for node in soup.find_all('a')
               if (node.get('href') is not None) and
                  node.get('href').endswith('.tls')]
    lsk_path = os.path.join(__datapath__, 'spice_kernels', 'lsk')
    lsk_filename = os.path.join(lsk_path, os.path.basename(lsk_url[-1]))
    if not os.path.exists(lsk_filename):
        print(f'Retreiving leapsecond kernel {os.path.basename(lsk_filename)}')
        file = requests.get(lsk_url[-1]).text
        with open(lsk_filename, 'w') as f:
            f.write(file)
    else:
        pass
    
    spice.furnsh(lsk_filename)
    

    
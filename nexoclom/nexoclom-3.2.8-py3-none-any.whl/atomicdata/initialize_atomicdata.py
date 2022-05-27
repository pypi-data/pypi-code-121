"""Read atomicdata from the text files and save as pandas dataframes
"""
import os
import glob
from nexoclom import __file__ as basefile
import pandas as pd
from nexoclom.atomicdata import gValue, PhotoRate

basepath = os.path.dirname(basefile)

def make_gvalue_table():
    ref = 'Killen et al. (2009)'
    datafiles = glob.glob(os.path.join(basepath, 'data', 'g-values', '*.dat'))
    
    gvalues = pd.DataFrame(columns=['species', 'wavelength', 
                                    'velocity', 'gvalue', 'refpoint', 
                                    'filename', 'reference'])
    
    for datafile in datafiles:
        # Determine the species
        species = os.path.basename(datafile).split('.')[0]

        with open(datafile) as f:
            # Determine the reference point
            refpt_str = f.readline().strip()
        refpt = float(refpt_str.split('=')[1])

        gvalue_species = pd.read_csv(datafile, sep=':', skiprows=1)
        wavelengths = [float(wave) for wave in gvalue_species.columns[1:]]
        gvalue_species.columns = ['vel'] + wavelengths

        for wave in wavelengths:
            print(species, wave)
            for _, row in gvalue_species.iterrows():
                newrow = {'species': species,
                          'wavelength': wave,
                          'velocity': row['vel'],
                          'gvalue': row[wave],
                          'refpoint': refpt,
                          'filename': datafile,
                          'reference': ref}
                gvalues.loc[len(gvalues)] = newrow

    fakerow = {'species': 'Fk',
                'wavelength': 9999,
                'velocity': 0., 
                'gvalue': 0.,
                'refpoint': 1.,
                'filename': 'NO_SUCH_FILE.dat',
                'reference': 'Fake (2021)'}
    gvalues.loc[len(gvalues)] = fakerow

    fakerow = {'species': 'Fk',
                'wavelength': 9999,
                'velocity': 0., 
                'gvalue': 1., 
                'refpoint': 1.,
                'filename': 'NO_SUCH_FILE2.dat',
                'reference': 'Liar (2021)'}
    gvalues.loc[len(gvalues)] = fakerow
    
    gvalue_file = gValue.gvalue_filename()
    print(gvalue_file)
    gvalues.to_pickle(gvalue_file)

def make_photorates_table():
    photodatafiles = glob.glob(os.path.join(basepath, 'data', 'Loss', 
                                            'Photo', '*.dat'))
    species, reaction, kappa, reference, best = [], [], [], [], []
    for photofile in photodatafiles:
        print(f'  {photofile}')
        ref = ''
        for line in open(photofile):
            if 'reference' in line.lower():
                ref = line.split('//')[0].strip()
            elif len(line.split(':')) == 4:
                parts = line.split(':')
                species.append(parts[0].strip())
                reaction.append(parts[1].strip())
                kappa.append(float(parts[2].strip()))
                reference.append(ref)
                best.append(True)
            else:
                pass
    photorates = pd.DataFrame({'species': species,
                               'reaction': reaction,
                               'kappa': kappa,
                               'reference': reference,
                               'best_version': best}) 
    
    # Find duplicates
    counts = photorates['reaction'].value_counts()
    duplicates = counts[counts > 1].index.values
    for duplicate in duplicates:
        subset = photorates[photorates.reaction == duplicate]
        print(f'Reaction = {duplicate}')
        for ind, row in subset.iterrows():
            print(f'{ind}: {row.reference}')
        which = input('Which is the best source? ')
        notwhich = [i for i in subset.index if i != which]
        photorates.loc[notwhich, 'best_version'] = False

    photorates.to_pickle(PhotoRate.photorates_filename())
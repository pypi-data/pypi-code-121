import setuptools



setuptools.setup(
    name="ivao",
    version="2.1",
    author="Chawalwit Akarajirathanachot",
    author_email="meck22772@gmail.com",
    description="IVAO WhazzupAPI for Python",
    long_description="""
### What is IVAO?
International Virtual Aviation Organisation (IVAO) 
is a non-profit association which operates a free-of-charge online flight-simulation network. Following free registration users can connect to the IVAO Network (IVAN) either as a virtual air traffic controller or as a virtual pilot and engage and interact with each other in a massively multiplayer environment utilising real-world aviation procedures, phraseology and techniques.

## Library Syntax structre
```
ivao
├──raw
|
├──to_json
|
├──servers
|
├──voiceServers
|
├──clients
|  ├──pilot
|  |  ├──raw
|  |  └──callsign
|  ├──atc
|  |   ├──raw
|  |   ├──callsign
|  |   └──atis
|  ├──observer
|  |   ├──raw
|  |   └──callsign
|  └──followMe
|
└──connections
   ├──total
   ├──supervisor
   ├──atc
   ├──observer
   ├──pilot
   └──worldTour


```


## Usage/Examples

#### ATC Callsign Example
Return all callsign of ATC in IVAO
```atc callsign
from ivao import ivao

print(ivao.clients.atc.callsign())
```
#### ATC ATIS
Return ATIS of ATC in IVAO
```atc atis
from ivao import ivao
print(ivao.clients.atc.atis(callsign="VTBD_TWR"))
```
#### Pilot Callsign Example
Return all callsign of Pilot in IVAO
```Pilot callsign
from ivao import ivao

print(ivao.clients.pilot.callsign())
```





""",
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    install_requires  = ['requests'],
    license = 'MIT'
)

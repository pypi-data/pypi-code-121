import json, requests, os
url = "https://api.ivao.aero/v2/tracker/whazzup"

pcs = [] #pilot callsign list
acs = [] #atc callsign list
ocs = [] #other callsign list

class ivao():
    def raw():
        r = requests.get(url)
        data = r.json()
        return data
    
    def to_json(filename, data):
        with open(filename, 'w') as outfile:
            json.dump(data, outfile)
   
    def servers():
        data = ivao.raw()
        servers = data['servers']
        return servers
    
    def voiceServers():
        data = ivao.raw()
        voiceServers = data['voiceServers']
        return voiceServers
    
    #Connections Class
    class connections():     
        def total():
            data = ivao.raw()
            total = data['connections']['total']
            return total
        
        def supervisor():
            data = ivao.raw()
            supervisor = data['connections']['supervisor']
            return supervisor
        
        def atc():
            data = ivao.raw()
            atc = data['connections']['atc']
            return atc
        
        def observer():
            data = ivao.raw()
            observer = data['connections']['observer']
            return observer
        
        def pilot():
            data = ivao.raw()
            pilot = data['connections']['pilot']
            return pilot
        
        def worldTour():
            data = ivao.raw()
            worldTour = data['connections']['worldTour']
            return worldTour

    #Client Class
    class clients():
        def raw():
            data = ivao.raw()
            clients = data['clients']
            return clients
        
        class pilot():
            def raw():
                data = ivao.raw()
                pilot = data['clients']['pilots']
                return pilot

            def callsign():
                data = ivao.raw()
                pilot = data['clients']['pilots']

                for i in pilot:
                    callsign = i['callsign']
                    pcs.append(callsign)
                return pcs
        
        class atc():
            def raw():
                data = ivao.raw()
                atc = data['clients']['atcs']
                return atc
            
            def callsign():
                data = ivao.raw()
                atc = data['clients']['atcs']

                for i in atc:
                    callsign = i['callsign']
                    acs.append(callsign)
                return acs
            
            def atis(callsign):
                data = ivao.raw()
                atc = data['clients']['atcs']
                for i in atc:
                    if i['callsign'] == callsign:
                        atis = i['atis']['lines']
                        return atis
                return None
        
        class observer():
            def raw():
                data = ivao.raw()
                observer = data['clients']['observers']
                return observer
            
            def callsign():
                data = ivao.raw()
                observer = data['clients']['observers']

                for i in observer:
                    callsign = i['callsign']
                    ocs.append(callsign)
                return ocs
    def followMe():
        data = ivao.raw()
        followMe = data['clients']['followMe']
        return followMe

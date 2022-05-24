from pysolardb.SolarDB import SolarDB
import logging
import numpy as np

if __name__=="__main__":
    solar = SolarDB()
    solar.setloggerLevel(logging.INFO)
    df = solar.getSiteDataframe("amitie", start="-1w")
    print(df)
    df.to_csv("booyashaka.csv")
    # print(solar.getSensors(sites=["vacoas"], types=["DHI"])[0])
    # print(solar.getAllSites())
    # print(solar.getAllTypes()[1])

    # solar_measure = solar.getMeasures(names=["DHI_pq01_Avg"], nested=True)[0]["model"]["name"]
    # model = solar.getModels(name=solar_measure)[0]
    # print(model)
    # print(solar.getMeasures(names=["RH_ng01_Avg"], nested=True))

    # smeta = solarfunc.SensorMeta(solar)
    # for sensor in solar.getSensors(sites=["amitie"]):
    #     print(smeta.getSensorMeta(sensor))
    # print(solarfunc.getSiteLifespan(solar, "vacoas"))
    # print(solarfunc.getAvailableSensors(solar,"amitie", "2022-05-16T00:00:00Z", "2022-05-17T07:00:00Z"))

    # for sensor in solar.getSensors(["amitie"]):
    #     meta = sensormeta.getSensorMeta(sensor)["instrument"]
    #     instrulist[meta["model"]+"_"+meta["serial"]] = meta

    # for i in instrulist:
    #     print(instrulist[i]["model"] + "_" + instrulist[i]["serial"])

# alias = ["amitie"]
# campaign = solar.getCampaigns(alias=alias[0])[0]
# for meta in siteMetaTypes:
#     print(meta + " : ")
#     print(campaign[meta])

    # sdata = solar.getData(sensors=solar.getSensors(sites=["amitie","vacoas"]))
    # print(sdata)
# dtype = ["GHI"]
# data = solar.getData(sites=alias, types=dtype, start="-2y", aggrFn="mean", aggrEvery="1d")

# # extract the dates and values for Vacoas from the 'data' dictionary
# sensors = solar.getSensors(sites=["plaineparcnational"], types=["GHI"])

# plt.figure()
# for sensor in sensors:
#     dates = data["plaineparcnational"][sensor]["dates"]
#     values = data["plaineparcnational"][sensor]["values"]

#     # put the dates to a datetime format
#     dates = [dt.strptime(date, "%Y-%m-%dT%H:%M:%SZ") for date in dates]

#     # plot the average global irradiance per week for the last 2 y

#     plt.plot(dates, values)
# plt.legend(labels=sensors)
# plt.show()


# alias= ['saintlouisjeanjoly']
# dtype = ['GHI']
# sensors = solar.getSensors(types=dtype, sites=alias)
# bounds = []
# for sensor in sensors:
#     bound = solar.getBounds(sites=alias, types=dtype, sensors=[sensor])
#     bounds.append(sensor + "= start: " + bound.get(alias[0]).get(sensor).get("start") \
#                          + " | stop: " + bound.get(alias[0]).get(sensor).get("stop"))
# print("\n".join(bounds))
# print(solar.getCampaigns(territory="Mauritius"))

# print(solar.getInstruments())

# print(solar.getMeasures())

# print(solar.getModels())
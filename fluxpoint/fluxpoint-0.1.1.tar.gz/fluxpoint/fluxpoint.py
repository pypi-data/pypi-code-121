import json, requests;

from collections import namedtuple;

class FluxpointClient:
    def __init__(self, token: str) -> None:
        if token == "":
            raise AttributeError("Error, Fluxpoint Authorization Token must not be an empty string!") from None;
        self.token = token;

        self.nsfw = self.__NSFW(self.token);
        self.sfw = self.__SFW(self.token);
        self.imageGen = self.__ImageGen(self.token);
    def __repr__(self) -> None:
        return "FluxpointClient";
        
    class __NSFW:
        def __init__(self, token: str):
            self.token = token;
            self.successResponse = namedtuple("goodResponse", "id file success code message");
            self.badResponse = namedtuple("badResponse", "success code message");

         # Function to reduce the work load of sending the requests, reduces code amount quite a bit and packages up response nicely.
        async def __req(self, endpoint: str):
            try:
                res = requests.get(endpoint, headers = { "Authorization": self.token });
                res = res.json();

                if res["success"]:
                    return self.successResponse(id = res["id"], file = res["file"], success = res["success"], code = res["code"], message = res["message"]);
                else:
                    return self.badResponse(success = res["success"], code = res["code"], message = res["message"]);
            except Exception as e:
                raise e;
        # START IMAGE METHODS #
                
        async def getAzurlanImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/azurlane");

        async def getFeetImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/feet");

        async def getCumImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/cum");

        async def getBlowjobImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/blowjob");

        async def getSoloImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/solo");

        async def getNekoImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/neko");

        async def getBoobsImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/boobs");

        async def getAnalImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/anal");

        async def getPussyImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/pussy");

        async def getYuriImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/yuri");

        async def getBDSMImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/bdsm");

        async def getFutaImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/futa");

        async def getHentaiImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/hentai");

        async def getAssImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/ass");

        async def getKitsuneImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/kitsune");

        async def getFemdomImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/femdom");

        async def getNekoparaImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/nekopara");

        async def getLewdImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/lewd");

        async def getPantyhoseImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/pantyhose");

        async def getCosplayImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/cosplay");

        async def getPetplayImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/petplay");

        async def getGasmImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/gasm");

        async def getTrapImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/trap");

        async def getAnusImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/anus");

        async def getHoloImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/holo");

        async def getYaoiImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/img/yaoi");
        # START GIF METHODS #

        async def getFeetGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/gif/feet");

        async def getCumGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/gif/cum");

        async def getBlowjobGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/gif/blowjob");

        async def getSoloGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/gif/solo");

        async def getNekoGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/gif/neko");

        async def getBoobsGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/gif/boobs");

        async def getAnalGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/gif/anal");

        async def getPussyGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/gif/pussy");

        async def getYuriGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/gif/yuri");

        async def getBDSMGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/gif/bdsm");

        async def getFutaGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/gif/futa");

        async def getSpankGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/gif/spank");

        async def getAssGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/gif/ass");

        async def getKistuneGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/gif/kitsune");

        async def getFemdomGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/gif/femdom");

        async def getHentaiGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/nsfw/gif/hentai");

    class __SFW:
        def __init__(self, token: str):
            self.token = token;
            self.successResponse = namedtuple("goodResponse", "id file success code message");
            self.badResponse = namedtuple("badResponse", "success code message");

        # Function to reduce the work load of sending the requests, reduces code amount quite a bit and packages up response nicely.
        async def __req(self, endpoint: str):
            try:
                res = requests.get(endpoint, headers = { "Authorization": self.token });
                res = res.json();

                if res["success"]:
                    return self.successResponse(id = res["id"], file = res["file"], success = res["success"], code = res["code"], message = res["message"]);
                else:
                    return self.badResponse(success = res["success"], code = res["code"], message = res["message"]);
            except Exception as e:
                raise e;
        # START OF IMAGE METHODS #
                
        async def getNekoImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/img/neko")
      
        async def getKitsuneImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/img/kitsune");

        async def getHoloImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/img/holo");

        async def getChristmasImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/img/christmas");

        async def getMaidImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/img/maid");

        async def getNekoparaImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/img/nekopara");

        async def getAzurlanImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/img/azurlane");

        async def getSenkoImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/img/senko");

        async def getDDLCImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/img/ddlc");

        async def getWallpaperImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/img/wallpaper");

        async def getAnimeImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/img/anime");

        async def getMemeImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/img/meme");

        async def getNoUImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/img/nou");

        async def getPogImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/img/pog");

        async def getCatImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/img/cat");

        async def getDogImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/img/dog");

        async def getLizardImage(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/img/lizard");

        # START OF GIF METHODS #

        async def getBakaGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/baka");

        async def getBiteGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/bite");

        async def getBlushGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/blush");

        async def getCryGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/cry")

        async def getDanceGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/dance");

        async def getFeedGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/feed");

        async def getFluffGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/fluff");

        async def getGrabGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/grab");

        async def getHandholdGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/handhold");

        async def getHighfiveGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/highfive");

        async def getHugGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/hug");

        async def getKissGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/kiss");

        async def getLickGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/lick");

        async def getNekoGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/neko");

        async def getPatGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/pat");

        async def getPokeGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/poke");

        async def getPunchGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/punch");

        async def getShrugGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/shrug");

        async def getSlapGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/slap");

        async def getSmugGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/smug");

        async def getStareGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/stare");

        async def getTickleGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/tickle");

        async def getWagGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/wag");

        async def getWastedGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/wasted");

        async def getWaveGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/wave");

        async def getWinkGif(self):
            return await self.__req("https://gallery.fluxpoint.dev/api/sfw/gif/wink");
           
    class __ImageGen:
        def __init__(self, token: str):
            self.token = token;   
            self.successResponse = namedtuple("goodResponse", "id file success code message");
            self.bytesResponse = namedtuple("bytesResponse", "bytes success code");
            self.badResponse = namedtuple("badResponse", "success code message");

        # Function to reduce the work load of sending the requests, reduces code amount quite a bit and packages up response nicely.
        async def __req(self, endpoint: str, **kwargs):
            try:
                if not kwargs.get("body", False):
                    res = requests.get(endpoint, headers = { "Authorization": self.token });
                else:
                    res = requests.get(endpoint, headers = { "Authorization": self.token }, json = kwargs["body"]);

                if not type(res) is dict:
                    return self.bytesResponse(bytes = res.text, success = True, code = 200);
                if res["success"]:
                    res = res.json();
                    return self.successResponse(id = res["id"], file = res["file"], success = res["success"], code = res["code"], message = res["message"]);
                    
                else:
                    res = res.json();
                    return self.badResponse(success = res["success"], code = res["code"], message = res["message"]);
            except Exception as e:
                print(e);
        # CLASS METHODS #
                
        async def welcomeImage(self, username: str, avatar: str, background: str, **kwargs) -> str:
            """
                --Returns--
                String of Bytes returned from the API.
            
                --Parameters--
                username - Username of user you are welcoming.
                avatar - Avatar to set.
                background - background color. (accepts RGB string ex: 0,0,0 or hex strings ex: #FFFFFF)

                Optional arguments:
                members - Member text (ex: "Member #1)
                icon - Icon to set. (icon options can be gotten using client.imageGen.getIcons())
                banner - Banner to set. (banner options can be gotten using client.imageGen.getBanners())
                color_welcome - Color of welcome text. (accepts RGB string ex: 0,0,0 or hex strings ex: #FFFFFF)
                color_username - Color of username text. (accepts RGB string ex: 0,0,0 or hex strings ex: #FFFFFF)
                color_members - Color of member text. (accepts RGB string ex: 0,0,0 or hex strings ex: #FFFFFF)
            """
            
            bodyData = {
                "username": username,
                "avatar": avatar,
                "background": background
            };

            if kwargs.get("members"):
                bodyData["members"] = kwargs["members"];
            if kwargs.get("icon"):
                bodyData["icon"] = kwargs["icon"];
            if kwargs.get("banner"):
                bodyData["banner"] = kwargs["banner"];
            if kwargs.get("color_welcome"):
                bodyData["color_welcome"] = kwargs["color_welcome"];
            if kwargs.get("color_username"):
                bodyData["color_username"] = kwargs["color_username"];
            if kwargs.get("color_members"):
                bodyData["color_members"] = kwargs["color_members"];
            
            return await self.__req("https://api.fluxpoint.dev/gen/welcome", body = bodyData);
        
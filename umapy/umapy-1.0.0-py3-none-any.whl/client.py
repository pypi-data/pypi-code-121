import difflib
from typing import Optional

import requests

from umapy._helpers import (
    Roster,
    RosterDict,
    ChampsInfo,
    NodeInfo,
    Location,
    champ_checker,
)

from .Exceptions.api_errors import APIError, ChampError, NodeError, RosterError


class BaseClient:
    """
    Base class for both sync and async classes.

    This is a internal class and is not meant to be used.
    """

    def __init__(self) -> None:
        self.session = requests.Session()
        self.url = "https://api.rexians.tk"


class Client(BaseClient):
    """
    Represents a Synchronounus client

    Functions
    ---------
    1. get_champs_info(champname, tier)
    2. find_champ(champname)
    ---------

    """

    def __init__(self) -> None:
        super().__init__()

    def get_champ_info(
        self, champname: str, tier: Optional[int] = 6, rank: int = 1
    ) -> ChampsInfo:
        """
        Get champ info for a specific champ.

        Parameters
        ----------
        champname : str (Required)
        The champ name for the character. Look here for names-

        tier : int (Optional)
        The tier/star of the character from 1 to 6.

        rank: int (Required)
        The rank of the champ. The rank various with the tier.

        Tier 6 = 1,2,3,4\n
        Tier 5 = 1,2,3,4,5\n
        Tier 4 = 1,2,3,4,5\n
        Tier 3 = 1,2,3,4\n
        Tier 2 = 1,2,3\n
        Tier 1 = 1,2\n
        ----------

        - Returns ChampsInfo object
        - Raises ChampError on wrong champname
        - Raises ChampError on incorrect tier and rank combination
        - Raises ChampError if tier is bigger than 6
        - Raises APIError on Internal Server Error
        """

        if tier is not None and tier not in range(1, 7):
            raise ChampError("Tier should not be bigger than 7 or lower than 1.")

        url = self.url + "/champs/"
        champname = champname.upper()
        champname = champ_checker(champname)
        params = {"champ": champname, "tier": tier, "rank": rank}

        request = self.session.get(url=url, params=params)

        response = request.json()
        status = request.status_code
        if status == 500:
            raise APIError(f"Internal Server Error in the API. Status:{status}")
        elif status == 422:
            raise APIError(response["detail"])
        elif status in [400, 404]:
            raise ChampError(response["detail"])

        else:
            location = Location(story_quests=response["find"]["story_quests"])
            return ChampsInfo(
                json=response,
                name=response["name"],
                mcoc_class=response["class"],
                tags=response["tags"],
                contact_type=response["contact"],
                tier=int(response["tier"]),
                rank=int(response["rank"]),
                challenger_rating=int(response("challenger_rating")),
                prestige=int(response["prestige"]),
                health=int(response["hp"]),
                attack=int(response["attack"]),
                abilities=response["abilities"],
                crit_rate=int(response["crit_rate"]),
                crit_damage=int(response["crit_dmge"]),
                armor=int(response["armor"]),
                block_proficiency=int(response["block_prof"]),
                energy_resistence=int(response["energy_resist"]),
                physical_resistence=int(response["physical_resist"]),
                crit_resistence=int(response["crit_resist"]),
                signature_info=response["sig_info"],
                url_page=response["url_page"],
                img_link=response["img_portrait"],
                location=location,
                status=request.status_code,
            )

    def get_node(self, node_id: int) -> NodeInfo:
        """
        Get champ info for a specific champ.

        Parameters
        ----------
        node_id : int (Required)
        The ID for the node! All ID's are listed in
        ----------

        - Returns NodeInfo object
        - Raises NodeError on wrong node_id
        - Raises APIError on Internal Server Error
        """

        url = self.url + f"/nodes/{node_id}"
        r = self.session.get(url)
        response = r.json()
        status = r.status_code
        if status == 400:
            raise NodeError(response["detail"])
        elif status == 500:
            raise APIError(f"Internal Server Error in the API. Status:{status}")
        else:
            return NodeInfo(
                json=response,
                id=int(response["node_id"]),
                name=response["node_name"],
                info=response["node_info"],
                status=status,
            )

    def get_node_ids(self, node_name: str) -> list[int]:
        """
        Returns the most similiar nodes IDs in a list with the name specified.

        Parameters
        ----------
        node_name : str (Required)
        The Name/Partial Name for the node!
        ----------

        - Returns list object
        - Raises APIError on Internal Server Error
        """
        url = self.url + "/nodes/"
        r = self.session.get(url)
        response = r.json()
        status = r.status_code
        if status == 500:
            raise APIError(f"Internal Server Error in the API. Status:{status}")
        else:
            nodes = response["data"]
            nodes_list = []
            for node in nodes:
                nodes_list.append(nodes[node]["node_name"].lower())
            node_names = difflib.get_close_matches(node_name.lower(), nodes_list)
            node_ids = []
            for names in node_names:
                node_id = nodes_list.index(names) + 1
                node_ids.append(node_id)
            return node_ids

    def get_roster(self, gamename: str) -> Roster:
        """
        Get Roster of any user who is registered on [Rexians Web](https://mcoc.rexians.tk/login/)
        The user must be registered and should have *champs added too* to get the Roster

        Parameters
        ----------
        gamename : str (Required)
        The gamename specified by the user at the time of registering for the first time.
        ----------

        - Returns Roster object
        - Raises RosterError on wrong gamename
        - Raises APIError on Internal Server Error
        """
        url = self.url + "/roster/get/"
        params = {"gamename": gamename}
        r = self.session.get(url, params=params)
        response = r.json()
        status = r.status_code
        if status == 400:
            raise RosterError(response["detail"])
        elif status == 500:
            raise APIError(f"Internal Server Error in the API. Status:{status}")
        else:
            roster = []
            if len(response["roster"]) > 0:
                for champs in response["roster"]:
                    roster_dict = RosterDict(
                        champ_name=champs["champ_name"],
                        tier=int(champs["tier"]),
                        rank=int(champs["rank"]),
                        prestige=int(champs["prestige"]),
                        sig_number=int(champs["sig_number"]),
                        img_link=champs["img_link"],
                        url_page=champs["url_page"],
                    )
                    roster.append(roster_dict)
            return Roster(
                json=response,
                discord_id=int(response["discord_id"]),
                gamename=response["game_name"],
                avatar_url=response["avatar_url"],
                prestige=int(response["prestige"]),
                about_me=response["about_me"],
                roster=roster,
            )

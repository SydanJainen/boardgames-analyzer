import logging
import time
import requests
from typing import List, Dict, Any, Optional
import xml.etree.ElementTree as ET


class BGGDataClient:
    def __init__(self, max_retries=3, retry_delay=2):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.api_base_url = "https://boardgamegeek.com/xmlapi2"

    def _safe_api_call(self, url: str, params: Dict[str, Any]) -> str:
        """
        Make a safe HTTP GET request with retries.
        """
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()  # Raise HTTP errors
                return response.text
            except requests.RequestException as e:
                self.logger.warning(f"API call failed (Attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise

    def _parse_xml(self, xml_string: str) -> ET.Element:
        """
        Parse XML string and return the root element.
        """
        try:
            return ET.fromstring(xml_string)
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse XML: {e}")
            raise

    def get_game_id(self, game_name: str) -> Optional[int]:
        """
        Retrieve the game ID based on the game name.
        """
        search_url = f"{self.api_base_url}/search"
        params = {"query": game_name, "type": "boardgame"}
        try:
            xml_data = self._safe_api_call(search_url, params)
            root = self._parse_xml(xml_data)
            game = root.find("item")
            if game is not None:
                return int(game.get("id"))
            else:
                self.logger.warning(f"No game found for name: {game_name}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to retrieve game ID for {game_name}: {e}")
            return None

    def get_game_info(self, game_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve the main information of a game using its ID.
        """
        thing_url = f"{self.api_base_url}/thing"
        params = {"id": game_id}
        try:
            xml_data = self._safe_api_call(thing_url, params)
            root = self._parse_xml(xml_data)
            item = root.find("item")
            if item is not None:
                return {
                    "id": game_id,
                    "name": item.find("name").get("value") if item.find("name") is not None else None,
                    "year": item.find("yearpublished").get("value") if item.find("yearpublished") is not None else None,
                    "description": item.find("description").text if item.find("description") is not None else None,
                }
            else:
                self.logger.warning(f"No information found for game ID: {game_id}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to retrieve game info for ID {game_id}: {e}")
            return None

    def get_game_comments(self, game_id: int, max_comments: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve comments for a specific game using its ID.
        """
        thing_url = f"{self.api_base_url}/thing"
        params = {"id": game_id, "comments": 1, "ratingcomments":1, "pagesize": max_comments}
        try:
            xml_data = self._safe_api_call(thing_url, params)
            root = self._parse_xml(xml_data)
            comments = []
            for comment in root.findall(".//comment"):
                comments.append({
                    "username": comment.get("username"),
                    "rating": comment.get("rating"),
                    "value": comment.get("value"),
                })
            return comments
        except Exception as e:
            self.logger.error(f"Failed to retrieve comments for game ID {game_id}: {e}")
            return []

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    client = BGGDataClient()

    game_name = "Catan"
    game_id = client.get_game_id(game_name)
    if game_id:
        info = client.get_game_info(game_id)
        comments = client.get_game_comments(game_id, max_comments=5)
        #print("Game Info:", info)
        print("Comments:", comments)

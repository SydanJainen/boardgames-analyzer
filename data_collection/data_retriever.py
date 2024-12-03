import os
import json
from typing import List, Dict, Any, Optional
import logging
from .bgg_api_client import BGGDataClient


class DataRetriever:
    def __init__(self, 
                 output_dir: str = "data/raw_comments", 
                 download_path: Optional[str] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.output_dir = output_dir
        self.download_path = download_path
        self.bgg_client = BGGDataClient()
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

    def retrieve_comments(self, 
                          games: List[str], 
                          max_comments: int = 500) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieve comments for multiple games by name.
        """
        all_comments = {}
        for game_name in games:
            try:
                # Retrieve game ID
                game_id = self.bgg_client.get_game_id(game_name)
                if game_id is None:
                    self.logger.warning(f"Game '{game_name}' not found.")
                    continue

                # Retrieve comments
                comments = self.bgg_client.get_game_comments(game_id, max_comments)
                all_comments[game_name] = comments
                self.logger.info(f"Retrieved {len(comments)} comments for '{game_name}'.")

                # Save individual game comments
                self._save_game_comments(game_name, comments)

            except Exception as e:
                self.logger.error(f"Error retrieving comments for '{game_name}': {e}")
        
        # Save full dataset
        self._save_full_dataset(all_comments)
        return all_comments

    def _save_game_comments(self, game_name: str, comments: List[Dict[str, Any]]):
        """
        Save comments for a specific game as a JSON file.
        """
        sanitized_name = self._sanitize_filename(game_name)
        game_filename = os.path.join(self.output_dir, f"{sanitized_name}_comments.json")
        try:
            with open(game_filename, "w", encoding="utf-8") as f:
                json.dump(comments, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Saved comments for '{game_name}' to {game_filename}.")
        except IOError as e:
            self.logger.error(f"Failed to save comments for '{game_name}': {e}")

    def _save_full_dataset(self, dataset: Dict[str, List[Dict[str, Any]]]):
        """
        Save the full dataset of all game comments.
        """
        full_dataset_path = os.path.join(self.output_dir, "full_comments_dataset.json")
        try:
            with open(full_dataset_path, "w", encoding="utf-8") as f:
                json.dump(dataset, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Saved full dataset to {full_dataset_path}.")
        except IOError as e:
            self.logger.error(f"Failed to save full dataset: {e}")

    def load_local_dataset(self, source: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load a dataset from a local file or a specified path.
        """
        load_path = source or self.download_path or os.path.join(self.output_dir, "full_comments_dataset.json")
        try:
            with open(load_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.logger.info(f"Loaded dataset from {load_path}.")
            return data
        except FileNotFoundError:
            self.logger.error(f"Dataset not found at {load_path}.")
            return {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON at {load_path}: {e}")
            return {}

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """
        Sanitize a string to create a valid filename.
        """
        return "".join(c if c.isalnum() or c in "._-" else "_" for c in name)

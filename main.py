import logging
from data_collection.data_retriever import DataRetriever
from data_collection.data_preprocessor import DataPreprocessor

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Games to analyze
    games = ['Gloomhaven', 'On Mars', 'CATAN']
    
    # Retrieve comments
    retriever = DataRetriever(output_dir='data/raw_comments')
    comments_dataset = retriever.retrieve_comments(games)
    
    # Preprocess dataset
    preprocessor = DataPreprocessor()
    preprocessed_dataset = preprocessor.preprocess_dataset(comments_dataset)
    
    # Further processing or analysis can be done here

if __name__ == '__main__':
    main()
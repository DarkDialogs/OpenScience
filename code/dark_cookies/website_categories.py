import logging

def detect_homepage2vec_category(domain):
    try:
        from homepage2vec.model import WebsiteClassifier
        model = WebsiteClassifier()
        website = model.fetch_website(domain)
        scores, embeddings = model.predict(website)
        category = max(scores, key=scores.get)
        logging.info(f"Website category: {category}")
        return category
    except Exception as e:
        logging.warning(f"Failed to find category for '{domain}'")
        return None
class BusinessEntity:
    """Base class for all business entities across domains (scaffold)"""
    def __init__(self, model_name: str, domain: str, discovered_metadata: dict):
        self.model_name = model_name
        self.domain = domain
        self.metadata = discovered_metadata 
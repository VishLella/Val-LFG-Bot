class Player:
    def __init__(self, user_id, name, region, rank, servers, tag=None):
        self.user_id = user_id
        self.name = name
        self.region = region
        self.rank = rank
        self.servers = servers
        self.tag = tag
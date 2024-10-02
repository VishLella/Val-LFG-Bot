def get_user_region(member):
    region_roles = ["North America", "Europe", "APAC", "LATAM", "Korea", "Brazil"]

    for role in member.roles:
        if role.name in region_roles:
            return role.name
        
    return None

def get_user_rank(member):
    rank_roles = ["Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ascendant", "Immortal 1", "Immortal 2", "Immortal 3", "Radiant"]

    for role in member.roles:
        for rank in rank_roles:
            if rank in role.name:
                return rank
    
    return None
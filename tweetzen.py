import time
import json
from twikit import Client

# Replace these values with your own login credentials
USERNAME = 'YOUR_X_USERNAME'
PASSWORD = 'YOUR_X_PASSWORD'
USE_CACHE = False

client = Client('ja-JP')

if USE_CACHE:
    client.load_cookies('cookies.json')
else:
    client.login(auth_info_1=USERNAME, password=PASSWORD)
    client.save_cookies('cookies.json')

def get_community_users(community_id: str, use_cache: bool = USE_CACHE) -> list[dict]:
    if use_cache:
        with open('members.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    community = client.get_community(community_id)
    members = []
    original_members = client.get_community_members(community_id, count=community.member_count)
    
    while original_members:
        members.extend(
            {'id': member.id, 'name': member.name} 
            for member in original_members
        )
        original_members = original_members.next()
    
    with open('members.json', 'w', encoding='utf-8') as f:
        json.dump(members, f, ensure_ascii=False)
    
    return members

def get_followers(client: Client, use_cache: bool = USE_CACHE) -> list[dict]:
    if use_cache:
        with open('followers.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    followers = []
    user = client.user()
    users = user.get_followers(count=user.followers_count)
    
    while users:
        followers.extend(
            {'id': follower.id, 'name': follower.name} 
            for follower in users
        )
        users = users.next()
    
    with open('followers.json', 'w', encoding='utf-8') as f:
        json.dump(followers, f, ensure_ascii=False)
    
    return followers

def is_a_follower(followers: set[str], user_id: str) -> bool:
    return user_id in followers

def main():
    community_users = get_community_users('The community id') # The community users to ban
    followers = get_followers(client)
    follower_ids = {f['id'] for f in followers}

    community_users_count = len(community_users)
    start = 1  # Starting point for processing users
    count = 0
    
    # Notice that you would be kicked off if you are banning too many users(~400?)
    for user in community_users:
        count += 1
        if count < start:
            print(f"[INFO] {count}/{community_users_count} : Skipping...")
            continue
        
        if not is_a_follower(follower_ids, user['id']):
            try:
                client.block_user(user_id=user['id'])
                print(f"[INFO] {count}/{community_users_count} : Blocked user: {user['name']} ({user['id']})")
            except Exception as e:
                print(f"[ERROR] {count}/{community_users_count} : Error blocking user {user['name']} ({user['id']}) - {e}")
        else:
            print(f"[WARN] {count}/{community_users_count} : User {user['name']} ({user['id']}) is a follower, not blocked.")
        
        time.sleep(0.5)

if __name__ == "__main__":
    main()
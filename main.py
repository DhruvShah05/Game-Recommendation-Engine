from auth import authenticate_user
from db import get_or_create_user, get_user_purchases, update_user_purchases
from recommender import get_content_based_recommendations

def prompt_for_game_ids():
    print("\nEnter at least 3 game IDs separated by commas (e.g., 730,570,440):")
    ids = input("Game IDs: ")
    return [int(id.strip()) for id in ids.split(',') if id.strip().isdigit()]

def main():
    print("🔐 Signing in via Google...")
    email = authenticate_user()
    print(f"✅ Signed in as {email}")

    user = get_or_create_user(email)
    purchases = get_user_purchases(email)

    if len(purchases) < 3:
        print("⚠️ Not enough purchases found.")
        more_ids = prompt_for_game_ids()
        update_user_purchases(email, more_ids)
        purchases = get_user_purchases(email)

    print("🧠 Generating recommendations...")
    recs = get_content_based_recommendations(purchases)

    if not recs.empty:
        print("\n🎮 Top Recommendations:")
        for idx, row in recs.iterrows():
            print(f"  - {row['name']} (score: {row['score']:.4f})")
    else:
        print("😕 No recommendations available.")

if __name__ == "__main__":
    main()

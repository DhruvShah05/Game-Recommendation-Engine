from auth import authenticate_user
from db import get_or_create_user, get_user_purchases, update_user_purchases
from recommender import get_content_based_recommendations
import pandas as pd
import numpy as np

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
        print("⚠️ Not enough purchases found. Using popularity algorithm instead.")
        df = pd.read_csv('df_processed.csv')
        df['total_reviews'] = df['positive_ratings'] + df['negative_ratings']
        filtered_df = df[df['total_reviews'] >= 50]
        filtered_df['review_score'] = filtered_df['positive_ratings'] / filtered_df['total_reviews']
        filtered_df['popularity_score'] = filtered_df['review_score'] * np.log(filtered_df['total_reviews'])
        popular_games = filtered_df.sort_values(by='popularity_score', ascending=False)
        top_10 = popular_games[['name', 'review_score', 'total_reviews', 'popularity_score']].head(10)
        print("\n🎮 Top Popular Games:")
        for idx, row in top_10.iterrows():
            print(f"  - {row['name']} (popularity score: {row['popularity_score']:.4f})")
        return

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

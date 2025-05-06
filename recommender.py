import pandas as pd

similarity_df = pd.read_pickle("steam_similarity_matrix.pkl")
df_steam = pd.read_csv('steam.csv')

def get_content_based_recommendations(purchases, top_n=10):
    if len(purchases) == 0:
        return []

    user_id = 1
    interaction_df = pd.DataFrame(0, index=[user_id], columns=similarity_df.columns)
    valid_purchases = [appid for appid in purchases if appid in similarity_df.columns]
    interaction_df.loc[user_id, valid_purchases] = 1

    from model_code import get_content_based_recommendations as recommend_core
    scores = recommend_core(user_id, interaction_df, similarity_df, top_n)

    if scores.empty:
        return []

    return df_steam[df_steam['appid'].isin(scores.index)][['appid', 'name']].assign(score=scores.values)

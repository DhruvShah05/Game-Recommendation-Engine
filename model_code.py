import pandas as pd
def get_content_based_recommendations(user_id, user_item_matrix, product_similarity_content_df, top_n=10):
    """
    Generates top N product recommendations for a given user using Content-Based Filtering.
    """

    if user_id not in user_item_matrix.index:
        print(f"User ID {user_id} not found in user-item matrix. Cannot generate recommendations.")
        return pd.Series()

    user_history = user_item_matrix.loc[user_id, :]
    products_interacted = user_history[user_history > 0].index.tolist()
    products_interacted = [product for product in products_interacted if product in product_similarity_content_df.index]

    products_to_predict = user_item_matrix.columns.difference(products_interacted)
    products_to_predict = [product for product in products_to_predict if product in product_similarity_content_df.index]

    if not products_to_predict:
        print(f"User {user_id} has interacted with all products. No new recommendations possible.")
        return pd.Series()

    predicted_scores = []
    for product_candidate_id in products_to_predict:
        predicted_score = 0
        for product_history_id in products_interacted:
            similarity_score = product_similarity_content_df.loc[product_candidate_id, product_history_id]
            if similarity_score > 0:
                predicted_score += similarity_score

        predicted_scores.append((product_candidate_id, predicted_score))

    ranked_predictions = sorted(predicted_scores, key=lambda x: x[1], reverse=True)
    top_recommendations = ranked_predictions[:top_n]

    if not top_recommendations:
        return pd.Series()

    recommended_product_ids = [item[0] for item in top_recommendations]
    recommendation_scores = [item[1] for item in top_recommendations]

    return pd.Series(data=recommendation_scores, index=recommended_product_ids, name='predicted_score')
# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

import polars as pl

def calculate_combined_df(score_lf, content, k_avg):
    # Calculate average of top k scores
    avg_scores_df = (
        score_lf.group_by("content_id").agg(pl.col("score").top_k(k_avg).mean().alias("score"))
    )

    # Combine dataframes
    combined_df = (
        pl.LazyFrame(content, schema_overrides={"parent_id": pl.UInt32})
        .join(avg_scores_df, on="content_id", how="left")
    ).collect()

    return combined_df

def build_hierarchy(df):
    """
    Builds the hierarchical structure and calculates scores efficiently.
    """

    # Create a dictionary for fast parent-child lookup
    parent_child_map = {}
    for row in df.iter_rows():
        # TODO: find more elegant solution that doesnt require to unpack the row "manually"
        content_id, file_id, content_type, title, text, parent_id, date_created, date_updated, interaction_id, user_created, user_updated, score = row
        parent_child_map.setdefault(parent_id, []).append({"content_id": content_id, "file_id": file_id, "content_type": content_type, "title": title, "text": text, "parent_id": parent_id, "date_created": date_created, "date_updated": date_updated, "interaction_id": interaction_id, "user_created": user_created, "user_updated": user_updated, "score": score})
 
    def calculate_scores_and_build_subtree(node):
        """
        Recursively calculates scores and builds the subtree for a node.
        """
        total_score = node.get("score", 0)
        total_leafs = 1 if "score" in node else 0
        child_ids = []

        # Process children (if any) using the precomputed map
        for child in parent_child_map.get(node["content_id"], []):
            child_score, child_leafs, child_tree = calculate_scores_and_build_subtree(child)
            total_score += child_score
            total_leafs += child_leafs
            child_ids.append(child_tree)

        # Calculate average leaf score
        avg_leaf_score = total_score / total_leafs if total_leafs > 0 else None

        # Return results (including subtree)
        node["avg_leaf_score"] = avg_leaf_score
        node["child_id"] = child_ids
        return total_score, total_leafs, node

    # Find root nodes and build the hierarchy
    root_nodes = parent_child_map.get(None, [])
    hierarchy = []
    for root_node in root_nodes:
        _, _, root_tree = calculate_scores_and_build_subtree(root_node)
        hierarchy.append(root_tree)

    hierarchy.sort(key=lambda x: (x.get("score", 0) + (x.get("avg_leaf_score") or 0)), reverse=True)

    return hierarchy
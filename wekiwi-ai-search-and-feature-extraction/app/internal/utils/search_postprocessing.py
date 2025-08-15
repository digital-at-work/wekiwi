# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

import polars as pl
from loguru import logger
# Removed numpy import as explicit checks are removed
# import numpy as np

def calculate_combined_df(score_lf, content, k_avg):
    # logger.debug(f"calculate_combined_df: Input score_lf schema: {score_lf.schema}") # Removed debug log
    # Calculate average of top k scores
    avg_scores_df = (
        score_lf.group_by("content_id").agg(pl.col("score").top_k(k_avg).mean().alias("score"))
    )
    # logger.debug(f"calculate_combined_df: avg_scores_df schema: {avg_scores_df.schema}") # Removed debug log

    # Combine dataframes
    content_lf = pl.LazyFrame(content, schema_overrides={"parent_id": pl.UInt32})
    # logger.debug(f"calculate_combined_df: content_lf schema: {content_lf.schema}") # Removed debug log

    combined_lf = content_lf.join(avg_scores_df, on="content_id", how="left")
    # logger.debug(f"calculate_combined_df: combined_lf schema after join: {combined_lf.schema}") # Removed debug log

    combined_df = combined_lf.collect()
    # logger.debug(f"calculate_combined_df: Final combined_df schema: {combined_df.schema}") # Removed debug log
    # logger.debug(f"calculate_combined_df: Final combined_df head:\n{combined_df.head(5)}") # Removed debug log

    return combined_df

def build_hierarchy(df):
    # logger.debug(f"build_hierarchy: Input df schema: {df.schema}") # Removed debug log
    # logger.debug(f"build_hierarchy: Input df head:\n{df.head(5)}") # Removed debug log
    """
    Builds the hierarchical structure and calculates scores efficiently.
    """

    # Create a dictionary for fast parent-child lookup
    parent_child_map = {}
    # Use iter_rows() default tuple format for potentially better performance
    for row_tuple in df.iter_rows():
        # Unpack based on expected column order (adjust if schema changes)
        # Assuming schema: content_id, file_id, content_type, title, text, parent_id, ..., score
        # This is less robust than named=True but avoids potential dict overhead
        try:
             # Adjust indices based on actual combined_df schema
             content_id = row_tuple[0]
             parent_id = row_tuple[5]
             score = row_tuple[-1] # Assuming score is the last column
             # Create the dict needed for parent_child_map
             # Only include necessary fields if full row dict isn't needed downstream
             node_data = {
                 "content_id": content_id,
                 "score": score,
                 # Add other fields from row_tuple by index if needed by calculate_scores_and_build_subtree
                 "file_id": row_tuple[1],
                 "content_type": row_tuple[2],
                 "title": row_tuple[3],
                 "text": row_tuple[4],
                 "parent_id": parent_id,
                 "date_created": row_tuple[6],
                 "date_updated": row_tuple[7],
                 "interaction_id": row_tuple[8],
                 "user_created": row_tuple[9],
                 "user_updated": row_tuple[10],
             }
             parent_child_map.setdefault(parent_id, []).append(node_data)
        except IndexError:
             logger.warning(f"Could not unpack row tuple during parent_child_map creation: {row_tuple}")
             continue # Skip malformed rows

    def calculate_scores_and_build_subtree(node):
        """
        Recursively calculates scores and builds the subtree for a node.
        """
        # Initialize with safe defaults - parent nodes may have None scores
        node_score = node.get("score")
        # Removed debug logs and explicit numpy checks (float conversion happens earlier now)

        total_score = 0 if node_score is None else node_score
        total_leafs = 1 if node_score is not None else 0
        child_ids = []

        # Process children (if any) using the precomputed map
        for child in parent_child_map.get(node["content_id"], []):
            child_score, child_leafs, child_tree = calculate_scores_and_build_subtree(child)

            # Removed debug logs and explicit numpy checks

            # Safely add child scores - they might be None if the child is a container
            if child_score is not None:
                # Removed type check log
                total_score += child_score
            if child_leafs > 0:
                total_leafs += child_leafs
            child_ids.append(child_tree)

        # Calculate average leaf score - ensure we don't divide by zero
        avg_leaf_score = total_score / total_leafs if total_leafs > 0 else None
        # Removed debug log

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

    # Sort by combined score, handling None values safely
    def get_sort_key(x):
        direct_score = x.get("score")
        avg_score = x.get("avg_leaf_score")
        # Removed debug logs and explicit numpy checks

        direct_score_num = direct_score or 0
        avg_score_num = avg_score or 0

        # Removed type check log

        return direct_score_num + avg_score_num

    try:
        hierarchy.sort(key=get_sort_key, reverse=True)
    except Exception as sort_e:
        logger.error(f"Error during hierarchy sort: {sort_e}")
        raise # Re-raise the sorting error

    return hierarchy

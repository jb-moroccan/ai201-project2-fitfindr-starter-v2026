"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config
import json
import re

from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    Implementation:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    query_terms = set(re.findall(r"[a-z0-9]+", description.casefold()))
    if not query_terms:
        return []

    requested_size = re.findall(r"[a-z0-9]+", size.casefold()) if size else []

    def has_size(listing_size: str) -> bool:
        listing_tokens = re.findall(r"[a-z0-9]+", listing_size.casefold())
        token_count = len(requested_size)
        return any(
            listing_tokens[index:index + token_count] == requested_size
            for index in range(len(listing_tokens) - token_count + 1)
        )

    matches = []
    for listing in load_listings():
        if max_price is not None and listing["price"] > max_price:
            continue
        if requested_size and not has_size(listing["size"]):
            continue

        searchable_text = " ".join(
            [
                listing["title"],
                listing["description"],
                listing["category"],
                *listing["style_tags"],
            ]
        )
        listing_terms = set(re.findall(r"[a-z0-9]+", searchable_text.casefold()))
        score = len(query_terms & listing_terms)
        if score:
            matches.append((score, listing))

    matches.sort(key=lambda match: match[0], reverse=True)
    return [
        listing
        for _, listing in matches[:config.SEARCH_RESULT_LIMIT]
    ]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    Implementation:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    wardrobe_items = wardrobe.get("items", [])
    item_details = {
        "title": new_item.get("title"),
        "description": new_item.get("description"),
        "category": new_item.get("category"),
        "colors": new_item.get("colors", []),
        "style_tags": new_item.get("style_tags", []),
    }

    if wardrobe_items:
        prompt = (
            "Suggest one or two wearable outfits featuring this thrifted item. "
            "Use the wardrobe pieces listed below, name the pieces you use, "
            "and do not invent items the user does not own.\n\n"
            f"New item:\n{json.dumps(item_details, indent=2)}\n\n"
            f"Wardrobe items:\n{json.dumps(wardrobe_items, indent=2)}"
        )
    else:
        prompt = (
            "The user has no wardrobe items saved yet. Give one or two general, "
            "practical styling ideas for this thrifted item using complementary "
            "colors, silhouettes, or types of pieces they could look for. Do not "
            "claim the user already owns any other items.\n\n"
            f"New item:\n{json.dumps(item_details, indent=2)}"
        )

    response = generate(
        prompt,
        system=(
            "You are a practical personal stylist. Keep suggestions concise, "
            "specific to the item, and easy to wear. Return plain text."
        ),
    )
    return response or "Try pairing this piece with complementary colors and simple basics."


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    Implementation:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    title = new_item.get("title") or "this thrifted find"
    if not outfit.strip():
        return f"No outfit suggestion is available yet for {title}, so a fit card could not be created."

    item_details = {
        "title": title,
        "description": new_item.get("description", ""),
        "category": new_item.get("category", ""),
        "price": new_item.get("price"),
        "platform": new_item.get("platform", ""),
        "colors": new_item.get("colors", []),
        "style_tags": new_item.get("style_tags", []),
    }
    prompt = (
        "Write a 2-to-4 sentence social-media caption for this thrifted find. "
        "Make it sound natural and specific about the outfit's vibe, not like "
        "a product listing. Mention the item's title, price, and platform once "
        "each, and do not invent details.\n\n"
        f"Item details:\n{json.dumps(item_details, indent=2)}\n\n"
        f"Outfit suggestion:\n{outfit.strip()}"
    )
    response = generate(
        prompt,
        system=(
            "You write concise, authentic thrift-fashion captions. Follow the "
            "requested sentence count and include the supplied listing details."
        ),
    ).strip()
    if response:
        return response
    return f"A fit card for {title} could not be generated because the caption was empty."

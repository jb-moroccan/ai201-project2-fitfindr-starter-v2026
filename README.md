# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

FitFindr takes a clothing search query, such as an item description with a size and price limit, and looks for matching thrift listings. When it finds a match, it suggests outfit ideas using the user's wardrobe, or general styling ideas if the wardrobe is empty. It then creates a short caption for the selected item and outfit; if nothing matches, it explains what the user could change.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** This function searches the listings file and returns matches based on a description, size, and maximum price.
- **Inputs:** description (str), size (str | None, optional), max_price (float | None, optional, dollars)<!-- name and type each: `max_price` (float), not "a price" -->
- **Returns:** list[dict] - Matching listing dictionaries with fields including `title`, `price`, `size`, `category`, `style_tags`, and `platform`, ordered by keyword match.
- **When it has nothing:** Empty list

### `suggest_outfit`

- **What it does:** This function takes an item and a wardrobe, and returns outfit ideas.
- **Inputs:** new_item (dict listing), wardrobe (dict with an `items` list of wardrobe item dicts)
- **Returns:** str - Outfit suggestions as text, naming matching wardrobe pieces when available.
- **When it has nothing:** If the wardrobe is empty, general styling advice for the new item.

### `create_fit_card`

- **What it does:** This function writes a short caption someone would actually post about the item for a listing.
- **Inputs:** outfit (str), new_item (dict listing)
- **Returns:** str - A string that provides a description of how a new clothing item can be incorporated into an outfit from a person's existing wardrobe.
- **When it has nothing:** A descriptive message if the outfit suggestion is empty.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, store a message in `session["error"]` explaining that the user can change the description, size, or maximum price, then stop. Otherwise, store the first result in `session["selected_item"]` and call `suggest_outfit`. If that call returns a blank value, a non-string, `"Unable to suggest an outfit"`, or a string beginning with `"error:"`, store an error message and stop. Otherwise, pass the outfit suggestion string and selected item to `create_fit_card` and store its caption in the session.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** <!-- regex, string splitting, or asking the model — say which --> Regular expressions extract an optional size following `size` and an optional maximum price following terms such as `under`, `below`, `up to`, `at most`, or `max`, or a standalone dollar amount. The parser removes those matched parts and common filler words from the query to form the description; missing size or price values are stored as `None`.

**What moves through the session:** <!-- which fields, in what order --> Store the parsed description, size, and maximum price in `session["parsed"]`, then store the search results in `session["search_results"]`. If results exist, store the first listing in `session["selected_item"]`; `suggest_outfit` receives that item and `session["wardrobe"]`, and its text result is stored in `session["outfit_suggestion"]`. The agent reads the suggestion back from the session and passes it with `session["selected_item"]` to `create_fit_card`, storing the returned caption in `session["fit_card"]`. If search is empty or the outfit result signals an error, the agent stores a message in `session["error"]` and stops before the next tool.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Outfit 1: Casual Y2K Streetwear
- Y2K Baby Tee — Butterfly Print
- Baggy straight-leg jeans, dark wash
- Chunky white sneakers
- Black crossbody bag

Wear the cropped baby tee with the high-waisted baggy dark jeans to balance the fitted top. Finish the look with chunky white sneakers and the black crossbody bag for an easy everyday outfit.

Outfit 2: Edge Contrast
- Y2K Baby Tee — Butterfly Print
- Wide-leg khaki trousers
- Vintage black denim jacket
- Black combat boots

Pair the pink and white butterfly tee with the tan wide-leg trousers. Layer the slightly cropped black denim jacket on top and anchor the look with black combat boots to add some edge to the graphic tee.

  Fit card: Channel your inner 2000s pop star with this adorable white, pink, and purple Y2K Baby Tee — Butterfly Print. Pair it with baggy dark wash jeans and chunky sneakers for an effortless everyday streetwear look. Grab this fitted crop top for $18.00 over on depop before it's gone!
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

Outfit 1: Casual Streetwear
- Vintage Levi's 501 Jeans — Medium Wash
- White ribbed tank top
- Oversized grey crewneck sweatshirt
- Chunky white sneakers
- Black crossbody bag
Wear the tank tucked into the 501s with the grey crewneck layered on top. Finish with the white sneakers and black crossbody bag for an easy, everyday look.

Outfit 2: Edge & Denim
- Vintage Levi's 501 Jeans — Medium Wash
- White ribbed tank top
- Vintage black denim jacket
- Black combat boots
- Brown leather belt
Tuck the white tank into the 501s, secure them with the brown leather belt, and layer the black denim jacket on top. Complete the outfit with the black combat boots to lean into the vintage grunge aesthetic.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

Nothing beats a pair of broken-in blues with that effortless streetwear edge. Just style these with your favorite white sneakers for an easy, timeless look. Grab the Vintage Levi's 501 Jeans — Medium Wash for $38.00 over on depop before they're gone!
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I used Claude to help me build the search_listings function by giving it the spec to base it off what I wrote for the tool inventory in the README along with making sure to use the data loader to read in the file.
- *What came back:* It returned a function that had a return value of str.
- *What I changed:* I updated my README to reflect this str return value because I wanted the method signatures to match the initial stubs provided and my README did not while Claude properly followed the right return types.

**Moment 2**

- *What I asked for:* I asked Claude if it could help me understand how to temporarily change the cache to not be enabled so I could verify if my fit card function would return 3 different answers on 3 different runs.
- *What came back:* It suggested: In PowerShell, disable the cache for the current terminal session, then run all three calls with the same input:

```powershell
$env:AI201_CACHE = "0"
python -c "from tools import create_fit_card; from utils.data_loader import load_listings; item=load_listings()[0]; [print(f'Run {i}: {create_fit_card(\"jeans and white sneakers\", item)}') for i in range(1, 4)]"
```

This makes each call reach the model instead of reusing the cached answer. `TEMPERATURE` is already `0.9`, which encourages variation, but the model can still occasionally produce identical wording.

To restore the default cache setting in that terminal:

```powershell
Remove-Item Env:AI201_CACHE
```
- *What I changed:* I ended up simply changing the CACHE_ENABLED value to be 0 because I felt like this was a lot of extra work to test something that took less than a minute that I wanted to reset back to the previous value afterwards.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**

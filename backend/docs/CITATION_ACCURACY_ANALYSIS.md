# Citation Accuracy Analysis

## The Issue
User query: "What did Marcus Garvey say about unity?"

**Citation provided by system:**
> Founded the "Universal Negro Improvement Association and African Communities (Imperial) League... with the program of uniting the Negro peoples of the world into one great body to establish a country and government absolutely their own" **[Source: marcus_garvey_selected_writings, Locator: pdf:page:0010]**

**Problem:** The full quote about "African Communities (Imperial) League" is NOT on page 10.

## Investigation Results

### What's Actually in the Database

**The correct chunk:**
- **Chunk ID:** `70bbc8b9c8b4fa9e1426c7f6e58ef710916c78d84a490404e515c93af5cdd0eb`
- **Actual Locator:** `pdf:page:0021` (Page 21!)
- **Content:** Contains the full quote about "Universal Negro Improvement Association and African Communities (Imperial) League"

**What's on page 10:**
- **Chunk ID:** `e0088508183f385f265399af395138e2a232d8672546afcaf317c7e96b09c035`
- **Content:** Text about W.E.B. Du Bois calling Garvey "the most dangerous enemy of the Negro race" and criticism of Christianity
- **Does NOT contain:** Information about founding UNIA or African Communities League

## Root Causes (Most Likely to Least Likely)

### 1. **LLM Hallucinated the Citation** (Most Likely 70%)
**What happened:**
- The retrieval system retrieved MULTIPLE chunks (we found 15 chunks total)
- Chunk from page 21 contained the quote about UNIA/African Communities League
- Chunk from page 10 contained OTHER information about Garvey
- Gemini 2.5 Flash **combined information** from multiple chunks
- When generating the citation, it **picked the wrong locator**

**Why LLMs do this:**
- LLMs don't have perfect chunk-to-citation mapping
- They generate text auto-regressively and can "lose track" of which chunk a fact came from
- Even with strict prompting, citation assignment can drift

**Evidence:**
- The quote IS in the database (page 21)
- The retrieval found it
- But the model attributed it to page 10

### 2. **Multiple Chunks Merged in Context** (Possible 20%)
**What happened:**
- The `format_context()` function might have presented chunks in a way that obscured boundaries
- If chunks are presented sequentially without clear separators, the LLM might mis-attribute

**Current format in wwmd_ask.py:**
```python
def format_context(rows):
    evidence = ""
    for i, row in enumerate(rows, 1):
        cid, anchor_id, locator, content = row
        clean_content = content.replace("\\n", " ").strip()
        evidence += f"[ID:{i}] [Source:{anchor_id} Loc:{locator}]\\n{clean_content}\\n\\n"
    return evidence
```

**Issue:** This IS clearly separated, but the LLM still made the error.

### 3. **Index/Retrieval Returned Wrong Locator** (Unlikely 5%)
**What happened:**
- The database query returned correct content but with wrong metadata
 
**Evidence against this:** The investigation shows the chunk WITH the quote has the correct locator (page:0021), so the database is fine.

### 4. **User Query Matched Multiple Chunks** (Partial Factor 5%)
**What happened:**
- Query for "unity" matched 15 chunks
- Model had to synthesize from multiple sources
- More chunks = harder to maintain citation accuracy

## Recommendations to Fix

### Immediate Fixes

#### 1. **Stricter Citation Prompting**
Update the system prompt in `wwmd_ask.py` to be MORE explicit:

```python
SYSTEM_PROMPT_TEMPLATE = \"\"\"You are the Voice of the Marcus Garvey ARK.
You are provided with a set of Reference Chunks (EVIDENCE BOARD).

CORE DIRECTIVES ("The Prosecutor's Standard"):
1. Answer using **ONLY** the provided Reference Chunks.
2. **CRITICAL**: When citing, you MUST copy the EXACT [Source: X, Locator: Y] 
   from the chunk you're quoting. DO NOT invent or mix locators.
3. Each claim needs its own citation with the EXACT locator from that specific chunk.
4. If uncertain which chunk a fact came from, state: "Multiple sources mention..."
   
CITATION RULE:
For each fact, copy the [Source: X, Locator: Y] EXACTLY as shown in the Evidence Board.

EVIDENCE BOARD:
{context}
\"\"\"
```

#### 2. **Add Chunk IDs to Citations**
Modify the citation format to include chunk IDs for traceability:

```python
evidence += f"[ID:{i}] [ChunkID:{cid[:8]}] [Source:{anchor_id} Loc:{locator}]\\n{clean_content}\\n\\n"
```

Then prompt the model to include `[ID:X]` in citations.

#### 3. **Post-Processing Citation Validation**
Add a validation step that checks if the cited locator actually contains the quoted text:

```python
def validate_citation(answer, chunks):
    # Extract citations from answer
    # Check if quoted text appears in the cited chunk
    # Flag mismatches
    pass
```

### Long-Term Fixes

#### 4. **Use Structured Output** (Best Solution)
Use Gemini's structured output mode to force citations in a specific format:

```python
schema = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "citations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "chunk_id": {"type": "string"},
                    "source": {"type": "string"},
                    "locator": {"type": "string"}
                }
            }
        }
    }
}
```

This forces the model to explicitly map each claim to a specific chunk.

#### 5. **Citation-Tuned Model**
Fine-tune a smaller model specifically for citation accuracy on your ARK corpus.

## Summary

**Most likely cause:** The LLM **hallucinated the citation locator** by mixing up which chunk the information came from, even though the correct chunk (page 21) was in the retrieved context.

**Why it's partially correct:** Page 10 IS about Marcus Garvey and IS from the correct document `marcus_garvey_selected_writings`, so the model got the source document right but picked the wrong page within that document.

**Bottom line:** This is a known limitation of RAG systems - even with strict prompting, LLMs can misattribute citations when synthesizing from multiple chunks. The fix requires either:
- Stricter prompting with explicit examples
- Structured output to force chunk-to-citation mapping
- Post-processing validation

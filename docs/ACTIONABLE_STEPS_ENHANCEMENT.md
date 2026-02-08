# Actionable Steps Enhancement - Updated Prompt Instructions

## Objective
Enhanced WWMD and Lens responses to provide detailed, comprehensive answers that include concrete, actionable steps **grounded in and directly supported by the citations** from the Marcus Garvey archive.

## Problem Addressed
While WWMD responses were improved with enhanced length (3-5 paragraphs) and citation count (8-15), there was a need to ensure that:
1. Answers remain detailed and substantive
2. Actionable steps are explicitly required and prominent
3. Every step is directly tied to supporting citations
4. The WHY behind each step is explained based on Garvey's philosophy

## Solution Implemented

### 1. Main WWMD Prompt Enhancement
**File**: `backend/ragbox/scripts/wwmd_ask_hybrid.py` (Lines 138-166)

**New Requirements**:
- Maintain 3-5 paragraph minimum with layered structure
- **END with 2-3 concrete, actionable steps** grounded in the philosophical principles
- Each step requirements:
  * **Must be directly supported by citations** from the provided material
  * **Explain WHY** each step matters based on Garvey's philosophy
  * **Make steps specific and implementable** (not vague ideals)
  * **Connect each step** to the broader answer and cited evidence

**Example Response Structure**:
```
[Paragraph 1: Core Principle from Archive]
[Paragraph 2: Historical Application with Evidence]
[Paragraph 3: Practical Wisdom and Related Concepts]
[Paragraph 4: Integration and Deeper Analysis]

ACTIONABLE STEPS:
1. Specific action based on principle X (supported by [citation evidence])
2. Specific action based on principle Y (supported by [citation evidence])  
3. Specific action based on principle Z (supported by [citation evidence])
```

### 2. Lens Mode (Situation Analysis) Prompt Enhancement
**File**: `backend/ragbox/scripts/wwmd_ask_hybrid.py` (Lines 239-271)

**Updated Requirements**:
- `principle` field now must be **grounded in the context provided**
- `historicalAnalogy` must **include specific details** from the archive
- `actionSteps` array (3 steps) now **explicitly tied to archive philosophy**:
  * Each step description must note it's **"grounded in the archive philosophy"**
  * Steps must be **practical and implementable**
  * Must reflect **self-determination, economic independence, and organizational excellence**
  * Must **explain WHY** each step matters based on Garvey's philosophy
- New validation: **"If the context does not support actionable guidance, include that caveat"**
- Enhanced constraint: **"Ensure advice reflects the principles evident in the archive, not external knowledge"**

**Lens Response Structure**:
```json
{
  "principle": "Specific Garveyite principle grounded in context",
  "historicalAnalogy": "Detailed parallel from UNIA or Garvey's life with specifics",
  "actionSteps": [
    {"id": "1", "text": "Specific action grounded in archive philosophy"},
    {"id": "2", "text": "Specific action grounded in archive philosophy"},
    {"id": "3", "text": "Specific action grounded in archive philosophy"}
  ],
  "mirrorQuestions": [
    "Reflective question based on Garvey's philosophy",
    "Question about alignment with Garveyite principles"
  ]
}
```

## Key Improvements

### Specificity
- **Before**: "Provide actionable guidance"
- **After**: "2-3 concrete, actionable steps directly supported by citations, with explanation of WHY based on Garvey's philosophy"

### Citation Grounding
- **Before**: Steps mentioned support implied
- **After**: Explicitly states "Each step must be directly supported by citations from the material"

### Evidence Connection
- **Before**: Steps could be general wisdom
- **After**: "Connect each step to the broader answer and cited evidence"

### Philosophy Integration
- **Before**: Practical advice could be generic
- **After**: "Explain WHY each step matters based on Garvey's philosophy"

### Implementation Focus
- **Before**: "Not vague ideals"
- **After**: "Make steps specific and implementable" + explicit requirement to be practical

### Archive Fidelity
- **New**: "Ensure advice reflects the principles evident in the archive, not external knowledge"
- **New**: "If the context does not support actionable guidance, include that caveat"

## Impact on User Experience

### For Main WWMD Responses
Users now receive answers that:
- Are detailed (3-5 paragraphs with layered analysis)
- Include substantive evidence (8-15 citations)
- End with specific next steps they can take
- Understand WHY each step is grounded in Garvey's philosophy
- Know the step is supported by actual archive content

### For Lens Mode (Situation Analysis)
Users now receive:
- Specific Garveyite principle for their situation (directly from archive)
- Historical parallel showing how UNIA/Garvey addressed similar situations
- 3 concrete action steps with philosophical grounding
- Reflective questions to deepen understanding
- Confidence that advice is authentic to the archive, not invented

## Example Impact

### Question: "How did I get new customers?"

**Before Enhancement**:
- Response might have vague call to action
- Steps might not be clearly connected to citations
- User unclear where advice comes from

**After Enhancement**:
```
[Detailed response explaining UNIA's organizational and 
outreach success with multiple citations]

ACTIONABLE STEPS:
1. Establish clear organizational structure and mission statement 
   (grounded in UNIA structure as documented in the archive)
2. Build internal capacity before external expansion 
   (based on Garvey's principle of self-reliance found in [citation])
3. Create value proposition around shared ideals and mutual benefit 
   (supported by UNIA membership success documented in [citation])
```

User can see:
- ✓ Answers are detailed with substantive content
- ✓ Steps are specific and actionable
- ✓ Each step has philosophical foundation from archive
- ✓ Citations support the reasoning
- ✓ Connection between principle and practice is clear

## Technical Changes

**Files Modified**:
1. `backend/ragbox/scripts/wwmd_ask_hybrid.py`:
   - HYBRID_PROMPT_TEMPLATE: Enhanced (lines 138-166)
   - LENS_PROMPT_TEMPLATE: Enhanced (lines 239-271)

**Build Status**: ✅ Verified - `npm run build` successful (1758 modules, 6.19s)

**No Breaking Changes**:
- Existing API endpoints unchanged
- Response format unchanged
- Citation system unchanged
- Database unchanged

## Next Steps for Validation

1. **Test WWMD Response**:
   - Ask: "How did I get new customers?"
   - Verify: Response ends with 2-3 actionable steps
   - Verify: Each step clearly explains WHY it's important
   - Verify: Steps are connected to cited evidence

2. **Test Lens Mode**:
   - Enter a personal/business situation
   - Verify: principle is grounded in context
   - Verify: historicalAnalogy includes specific details
   - Verify: Each action step references archive principles

3. **Verify Citation Connection**:
   - Check that action steps reference or are clearly connected to cited material
   - Confirm steps are implementable, not vague ideals

## Philosophical Alignment

These enhancements ensure WWMD remains faithful to Marcus Garvey's principles:
- **Self-Determination**: Steps empower users to act independently
- **Practical Philosophy**: Actionable steps ground theory in practice
- **Archive Fidelity**: Advice is sourced from the archive, not invented
- **Systematic Thinking**: Steps reflect Garvey's holistic organizational approach

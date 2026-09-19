import json
from typing import Any
import logging

_log = logging.getLogger(__name__)

def expand_rejection_query(rejection_text: str) -> str:
    """
    Expands a raw rejection reason into a rich set of keywords 
    to improve lexical TF-IDF retrieval of policy clauses.
    """
    if not rejection_text:
        return rejection_text
        
    try:
        from app.extraction.evidence_extraction import _client, GROQ_MODEL
        if _client is None:
            return rejection_text
            
        prompt = f"""
Analyze the following insurance claim rejection reason.
Identify the core concept (e.g. notification delay, waiting period, room rent, exclusion, pre-existing disease).
Generate a list of 10-15 highly relevant keywords, synonyms, and typical policy terms that an insurance policy might use to describe this concept.
For example, if it's 'delay in notification', generate terms like 'notification', 'intimation', 'claim notification', 'hours', 'admission', 'discharge', 'delay', 'reimbursement', 'cashless'.

Rejection Reason:
"{rejection_text}"

Return exactly ONE JSON object with this schema:
{{
  "concept": "string",
  "issue": "string",
  "keywords": ["string", "string"]
}}
"""
        response = _client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        res = json.loads(response.choices[0].message.content)
        keywords = res.get("keywords", [])
        if keywords:
            expanded = rejection_text + " " + " ".join(keywords)
            _log.info(f"Expanded retrieval query: {expanded}")
            return expanded
    except Exception as e:
        _log.warning(f"Query expansion failed: {e}")
        pass
    
    return rejection_text

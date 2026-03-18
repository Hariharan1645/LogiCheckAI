import re

def rewrite_claim(claim: str) -> str:
    # A simple mock/heuristic claim rewriter to make spoken claims more declarative 
    # since no LLM is currently loaded for generation. 
    rewritten = claim
    # Example hardcoded heuristic from instructions
    if "lots of sugar" in rewritten.lower():
        rewritten = re.sub(r'(?i)lots of sugar', 'high sugar content', rewritten)
    
    # Capitalize first letter and ensure it ends with period
    if len(rewritten) > 0:
        rewritten = rewritten[0].upper() + rewritten[1:]
    if not rewritten.endswith('.'):
        rewritten += '.'
        
    return rewritten

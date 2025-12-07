import re
from typing import List, Dict, Any
from langchain.tools import tool
from src.tools.code_parser import CodeParser

# Initialize global parser instance
parser = CodeParser()

@tool
def check_hardcoded_secrets(code: str) -> List[Dict[str, Any]]:
    """
    Scans code for potential hardcoded secrets like API keys, passwords, and tokens.
    Returns a list of findings with line_number, issue, and severity.
    """
    findings = []
    lines = code.split('\n')
    
    # Regex patterns for common secrets
    patterns = [
        (r"(?i)(api_?key|access_?token|secret_?key|password|passwd|pwd)\s*=\s*['\"][a-zA-Z0-9_\-]{20,}['\"]", "Possible hardcoded secret"),
        (r"(?i)Authorization:\s*Bearer\s+[a-zA-Z0-9_\-\.]+", "Hardcoded Bearer token"),
        (r"(?i)AWS_ACCESS_KEY_ID\s*=\s*['\"]AKIA[0-9A-Z]{16}['\"]", "Hardcoded AWS Access Key"),
    ]
    
    for i, line in enumerate(lines, 1):
        for pattern, msg in patterns:
            if re.search(pattern, line):
                findings.append({
                    "line_number": i,
                    "issue": f"{msg} detected",
                    "severity": "critical"
                })
                
    return findings

@tool
def check_sql_injection(code: str) -> List[Dict[str, Any]]:
    """
    Detects potential SQL injection vulnerabilities by looking for string concatenation in SQL queries.
    Returns a list of findings.
    """
    findings = []
    lines = code.split('\n')
    
    # Patterns for insecure SQL construction (string concat or f-strings)
    # This is a heuristic approach
    sql_keywords = r"(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER)"
    
    # Look for: "SELECT ... " + variable
    concat_pattern = re.compile(fr'{sql_keywords}.*["\']\s*\+.*', re.IGNORECASE)
    
    # Look for: f"SELECT ... {variable}"
    fstring_pattern = re.compile(fr'f["\'].*{sql_keywords}.*\{{.*\}}.*["\']', re.IGNORECASE)
    
    # Look for: "SELECT ... %s" % variable (old style python, often insecure if not careful)
    # ignoring valid parameterized queries for now, assuming % usage might be risky in raw context
    
    for i, line in enumerate(lines, 1):
        if concat_pattern.search(line) or fstring_pattern.search(line):
            findings.append({
                "line_number": i,
                "issue": "Potential SQL Injection: detected dynamic string construction in SQL query",
                "severity": "critical"
            })
            
    return findings

@tool
def check_complexity(code: str, language: str) -> List[Dict[str, Any]]:
    """
    Calculates Cyclomatic Complexity per function and flags those with score > 10.
    Args:
        code: The source code.
        language: 'python' or 'javascript'.
    """
    findings = []
    ast = parser.parse(code, language)
    if not ast:
        return []
    
    metrics = parser.get_complexity_metrics(ast) # returns {func_name: score}
    # We need line numbers, so we might need to re-correlate or update parser.
    # For now, let's extract functions again to get line numbers and map them.
    
    functions = parser.extract_functions(ast)
    
    for func in functions:
        name = func['name']
        score = metrics.get(name, 0)
        
        if score > 10:
            findings.append({
                "line_number": func['start_line'],
                "issue": f"High Cyclomatic Complexity ({score} > 10) in function '{name}'",
                "severity": "warning"
            })
            
    return findings

@tool
def check_code_smells(code: str, language: str = 'python') -> List[Dict[str, Any]]:
    """
    Detects code smells:
    - Long functions (> 50 lines)
    - Too many parameters (> 5)
    - Deep nesting (> 4 levels)
    """
    findings = []
    ast = parser.parse(code, language)
    if not ast:
        return []
        
    functions = parser.extract_functions(ast)
    
    for func in functions:
        # Check Length
        length = func['end_line'] - func['start_line']
        if length > 50:
            findings.append({
                "line_number": func['start_line'],
                "issue": f"Function '{func['name']}' is too long ({length} lines > 50)",
                "severity": "warning"
            })
            
        # Check Parameters
        if len(func['args']) > 5:
            findings.append({
                "line_number": func['start_line'],
                "issue": f"Function '{func['name']}' has too many parameters ({len(func['args'])} > 5)",
                "severity": "warning"
            })
            
    # Check Nesting Depth
    # Helper to calculate max depth
    def get_max_depth(node, current_depth=0):
        max_d = current_depth
        
        # Nodes that increase nesting level
        nesting_types = [
            'if_statement', 'for_statement', 'while_statement', 'function_definition', 
            'class_definition', 'try_statement', 'with_statement',
            'arrow_function', 'function_declaration'
        ]
        
        is_nesting = node.type in nesting_types
        next_depth = current_depth + (1 if is_nesting else 0)
        
        if is_nesting and next_depth > 4:
            # We found a violation, we could record it here or just bubble up max
            pass 

        for child in node.children:
            max_d = max(max_d, get_max_depth(child, next_depth))
            
        return max_d

    # Since we want to flag specific lines, we should traverse and yield findings
    def find_deep_nesting(node, current_depth=0):
        nesting_types = [
            'if_statement', 'for_statement', 'while_statement', 
            'catch_clause', 'except_clause'
        ]
        
        if node.type in nesting_types:
            current_depth += 1
            
        if current_depth > 4 and node.type in nesting_types:
             findings.append({
                "line_number": node.start_point.row + 1,
                "issue": f"Deep nesting detected (Level {current_depth} > 4)",
                "severity": "warning"
            })
            # Don't report children to avoid spamming for the same block
             return

        for child in node.children:
            find_deep_nesting(child, current_depth)
            
    find_deep_nesting(ast)
            
    return findings

@tool
def check_naming_conventions(code: str, language: str) -> List[Dict[str, Any]]:
    """
    Checks naming conventions:
    - Python: PEP8 (snake_case for functions/vars)
    - JavaScript: camelCase for functions/vars
    """
    findings = []
    ast = parser.parse(code, language)
    if not ast:
        return []
        
    functions = parser.extract_functions(ast)
    
    snake_case_regex = re.compile(r"^[a-z_][a-z0-9_]*$")
    camel_case_regex = re.compile(r"^[a-z][a-zA-Z0-9]*$")
    
    for func in functions:
        name = func['name']
        if name == "anonymous":
            continue
            
        if language.lower() == 'python':
            if not snake_case_regex.match(name) and not (name.startswith('__') and name.endswith('__')):
                 findings.append({
                    "line_number": func['start_line'],
                    "issue": f"Function '{name}' does not follow PEP8 snake_case convention",
                    "severity": "info"
                })
        elif language.lower() in ['javascript', 'typescript']:
            if not camel_case_regex.match(name):
                 findings.append({
                    "line_number": func['start_line'],
                    "issue": f"Function '{name}' does not follow camelCase convention",
                    "severity": "info"
                })
                
    return findings

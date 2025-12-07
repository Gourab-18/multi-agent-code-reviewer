import os
import tree_sitter_python
import tree_sitter_javascript
from tree_sitter import Language, Parser, Node
from typing import List, Dict, Any, Optional, Tuple

class CodeParser:
    """
    A utility class to parse Python and JavaScript/TypeScript code using Tree-sitter.
    Extracts structure, metrics, and metadata.
    """
    
    def __init__(self):
        """Initialize parsers for supported languages."""
        self.parsers = {}
        self.languages = {}
        
        # Initialize Python
        try:
            py_lang = Language(tree_sitter_python.language())
            self.languages['python'] = py_lang
            parser = Parser(py_lang)
            self.parsers['python'] = parser
        except Exception as e:
            print(f"Warning: Could not load Python parser: {e}")

        # Initialize JavaScript
        try:
            js_lang = Language(tree_sitter_javascript.language())
            self.languages['javascript'] = js_lang
            parser = Parser(js_lang)
            self.parsers['javascript'] = parser
             # Map typescript to javascript parser for now as a fallback
            self.parsers['typescript'] = parser
            self.languages['typescript'] = js_lang
        except Exception as e:
            print(f"Warning: Could not load JavaScript parser: {e}")

    def parse(self, code: str, language: str) -> Optional[Any]:
        """
        Parse the given code into an AST.
        
        Args:
            code: The source code string.
            language: The programming language ('python', 'javascript', 'typescript').
            
        Returns:
            The root node of the AST, or None if parsing fails/language not supported.
        """
        parser = self.parsers.get(language.lower())
        if not parser:
            print(f"No parser found for language: {language}")
            return None
        
        try:
            # tree-sitter parse method expects bytes
            tree = parser.parse(bytes(code, "utf8"))
            return tree.root_node
        except Exception as e:
            print(f"Error parsing code: {e}")
            return None

    def extract_functions(self, ast_root: Node) -> List[Dict[str, Any]]:
        """
        Extract function definitions from the AST.
        
        Returns:
            List of dicts with 'name', 'args', 'start_line', 'end_line'.
        """
        if not ast_root:
            return []
            
        functions = []
        
        # Define queries based on language
        # Note: This is a simplified approach using node traversal for broader compatibility 
        # instead of raw S-expression queries which can be brittle if language grammar versions change.
        
        # We will walk the tree to find function definitions
        # This works for both Python and JS if we look for specific node types
        
        def traverse(node: Node):
            if node.type in ['function_definition', 'function_declaration', 'method_definition']:
                func_name = "anonymous"
                # Try to find name node
                name_node = node.child_by_field_name('name')
                if name_node:
                    func_name = name_node.text.decode('utf8')
                
                # Try to find parameters
                params_node = node.child_by_field_name('parameters')
                args = []
                if params_node:
                    args = [child.text.decode('utf8') for child in params_node.children 
                            if child.type in ['identifier', 'typed_parameter', 'default_parameter']]
                
                functions.append({
                    "name": func_name,
                    "args": args,
                    "start_line": node.start_point.row + 1,
                    "end_line": node.end_point.row + 1
                })
            
            # recursive traversal
            for child in node.children:
                traverse(child)

        traverse(ast_root)
        return functions

    def extract_classes(self, ast_root: Node) -> List[Dict[str, Any]]:
        """Extract class definitions from the AST."""
        if not ast_root:
            return []
            
        classes = []
        
        def traverse(node: Node):
            if node.type in ['class_definition', 'class_declaration']:
                class_name = "anonymous"
                name_node = node.child_by_field_name('name')
                if name_node:
                    class_name = name_node.text.decode('utf8')
                
                classes.append({
                    "name": class_name,
                    "start_line": node.start_point.row + 1,
                    "end_line": node.end_point.row + 1
                })
            
            for child in node.children:
                traverse(child)

        traverse(ast_root)
        return classes

    def extract_imports(self, ast_root: Node) -> List[str]:
        """Extract imported modules/libraries."""
        if not ast_root:
            return []
            
        imports = []
        
        def traverse(node: Node):
            # Python
            if node.type == 'import_statement':
                 imports.append(node.text.decode('utf8'))
            elif node.type == 'import_from_statement':
                 imports.append(node.text.decode('utf8'))
            
            # JavaScript
            elif node.type == 'import_statement': # ES6
                 imports.append(node.text.decode('utf8'))
            
            # Common JS require is a bit harder as it's a function call, skipping for simplicity unless strict
            
            for child in node.children:
                traverse(child)

        traverse(ast_root)
        return imports

    def get_complexity_metrics(self, ast_root: Node) -> Dict[str, int]:
        """
        Calculate Cyclomatic Complexity for each function in the AST.
        Returns a dict mapping function names to complexity score.
        """
        if not ast_root:
            return {}
            
        complexity_map = {}
        
        # Complexity increasing node types
        # This is a heuristic list
        complexity_node_types = {
            # Python
            'if_statement', 'elif_clause', 'for_statement', 'while_statement', 
            'except_clause', 'with_statement', 'assert_statement',
            'boolean_operator', # and, or
            
            # JS
            'if_statement', 'for_statement', 'while_statement', 'do_statement',
            'case_clause', 'catch_clause', 'ternary_expression',
            'binary_expression', # Check for && || manually if needed, or assume broad
        }
        
        def calculate_complexity(node: Node) -> int:
            score = 1 # Base complexity
            
            def walk(n: Node):
                nonlocal score
                if n.type in complexity_node_types:
                    # For binary expressions in JS, we only care about && and ||
                    if n.type == 'binary_expression':
                        operator = n.child_by_field_name('operator')
                        if operator and operator.text.decode('utf8') in ['&&', '||']:
                            score += 1
                    else:
                        score += 1
                
                for child in n.children:
                    walk(child)
                    
            walk(node)
            return score

        # Find functions and calc complexity for each
        # We reuse the logic from extract_functions effectively but need nodes
        def find_funcs(node: Node):
            if node.type in ['function_definition', 'function_declaration', 'method_definition']:
                name_node = node.child_by_field_name('name')
                name = name_node.text.decode('utf8') if name_node else "anonymous"
                complexity = calculate_complexity(node)
                complexity_map[name] = complexity
            
            for child in node.children:
                find_funcs(child)
                
        find_funcs(ast_root)
        return complexity_map

# CLI Test
if __name__ == "__main__":
    parser = CodeParser()
    
    # Test Python
    print("--- Testing Python Parsing ---")
    py_code = """
import os

class Reviewer:
    def review(self, code):
        if not code:
            return None
        elif len(code) > 1000:
            print("Too long")
        else:
            print("OK")
        
        for i in range(10):
            pass
            
def main():
    reviewer = Reviewer()
    reviewer.review("print('hello')")
"""
    ast = parser.parse(py_code, "python")
    if ast:
        print("Functions:", parser.extract_functions(ast))
        print("Classes:", parser.extract_classes(ast))
        print("Imports:", parser.extract_imports(ast))
        print("Complexity:", parser.get_complexity_metrics(ast))
        # Expected complexity for review: 1 (base) + 1 (if) + 1 (elif) + 1 (for) = 4 approx
    
    # Test JS
    print("\n--- Testing JavaScript Parsing ---")
    js_code = """
import React from 'react';

class Component {
    render() {
        if (this.props.show) {
            return <div>Hello</div>;
        } else {
             return null;
        }
    }
}

function helper(a, b) {
    return a && b ? a : b;
}
"""
    ast_js = parser.parse(js_code, "javascript")
    if ast_js:
        print("Functions/Methods:", parser.extract_functions(ast_js))
        print("Classes:", parser.extract_classes(ast_js))
        print("Imports:", parser.extract_imports(ast_js))
        print("Complexity:", parser.get_complexity_metrics(ast_js))

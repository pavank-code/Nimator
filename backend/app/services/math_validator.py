from sympy import sympify, SympifyError, symbols, latex
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from typing import Dict, Any, Optional, Tuple
import re


# Define common symbols
x, y, z, t, n, k = symbols('x y z t n k')


def validate_math_expression(expression: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a mathematical expression using SymPy.
    Returns (is_valid, error_message).
    """
    if not expression:
        return True, None  # Empty expression is valid (not required)
    
    try:
        # Clean up the expression
        cleaned = clean_expression(expression)
        
        # Try to parse with SymPy
        transformations = standard_transformations + (implicit_multiplication_application,)
        parsed = parse_expr(cleaned, transformations=transformations)
        
        # Additional check: can we evaluate it?
        # Try substituting a test value
        try:
            test_result = parsed.subs(x, 1)
        except:
            pass  # Some expressions can't be evaluated, that's okay
        
        return True, None
        
    except (SympifyError, SyntaxError, TypeError) as e:
        return False, f"Invalid expression: {str(e)}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def clean_expression(expr: str) -> str:
    """Clean and normalize a math expression for SymPy parsing."""
    # Replace common notation with SymPy-compatible syntax
    expr = expr.strip()
    
    # Replace ^ with ** for exponents
    expr = expr.replace('^', '**')
    
    # Handle common functions
    replacements = {
        'sin(': 'sin(',
        'cos(': 'cos(',
        'tan(': 'tan(',
        'log(': 'log(',
        'ln(': 'log(',
        'sqrt(': 'sqrt(',
        'exp(': 'exp(',
        'abs(': 'Abs(',
    }
    
    for old, new in replacements.items():
        expr = expr.replace(old, new)
    
    # Remove any LaTeX artifacts
    expr = re.sub(r'\\[a-zA-Z]+', '', expr)  # Remove \frac, \sqrt, etc.
    expr = expr.replace('{', '(').replace('}', ')')
    expr = expr.replace('[', '(').replace(']', ')')
    
    return expr


def validate_scene(scene: Dict[str, Any]) -> bool:
    """
    Validate math expressions within a scene.
    Returns True if all math is valid or no math is present.
    """
    scene_type = scene.get("scene_type", "")
    
    # Check function field for graph_2d scenes
    if scene_type == "graph_2d":
        function = scene.get("function")
        if function:
            is_valid, error = validate_math_expression(function)
            if not is_valid:
                print(f"Invalid function '{function}': {error}")
                return False
    
    # Check text field for math_mode text_labels
    if scene_type == "text_labels" and scene.get("math_mode"):
        text = scene.get("text", "")
        # For LaTeX text, we do lighter validation
        # Just check it's not empty and doesn't have obvious issues
        if not text:
            return False
    
    return True


def validate_math(prompt: str) -> bool:
    """
    Legacy function for backward compatibility.
    Validates that a prompt doesn't contain obviously invalid math.
    """
    # Extract potential math expressions from prompt
    # Look for patterns like "x^2", "f(x) = ..."
    math_patterns = re.findall(r'[a-zA-Z]\s*\([^)]+\)\s*=\s*[^,.\s]+', prompt)
    math_patterns += re.findall(r'[a-zA-Z]\^?\d+', prompt)
    
    # If no math found, that's okay
    if not math_patterns:
        return True
    
    # Validate each found expression
    for expr in math_patterns:
        # Extract just the expression part
        if '=' in expr:
            expr = expr.split('=')[1].strip()
        
        is_valid, _ = validate_math_expression(expr)
        if not is_valid:
            return False
    
    return True


def expression_to_lambda(expr_str: str) -> Optional[callable]:
    """
    Convert a string expression to a Python lambda function.
    Useful for plotting.
    """
    try:
        cleaned = clean_expression(expr_str)
        parsed = sympify(cleaned)
        return lambda val: float(parsed.subs(x, val))
    except:
        return None


def expression_to_latex(expr_str: str) -> str:
    """Convert a SymPy-style expression to LaTeX."""
    try:
        cleaned = clean_expression(expr_str)
        parsed = sympify(cleaned)
        return latex(parsed)
    except:
        return expr_str  # Return original if conversion fails
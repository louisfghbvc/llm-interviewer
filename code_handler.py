"""
Code Handler Module for AI Interview Simulator
程式碼輸入處理模組，提供驗證、格式化、安全檢查等功能
"""

import re
import ast
import logging
import subprocess
import tempfile
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import time
import hashlib

logger = logging.getLogger(__name__)

class CodeLanguage(Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CSHARP = "csharp"
    CPP = "cpp"
    C = "c"
    GO = "go"
    RUST = "rust"
    TYPESCRIPT = "typescript"
    SQL = "sql"

@dataclass
class CodeValidationResult:
    """Code validation result structure"""
    is_valid: bool
    language: str
    errors: List[str]
    warnings: List[str]
    line_count: int
    char_count: int
    complexity_score: int
    security_issues: List[str]
    suggestions: List[str]

@dataclass
class CodeSnippet:
    """Code snippet data structure"""
    snippet_id: str
    session_id: str
    code: str
    language: str
    timestamp: float
    validation_result: CodeValidationResult
    is_solution: bool = False
    problem_description: str = ""

class CodeHandler:
    """
    Code input and processing handler
    處理程式碼輸入、驗證、格式化和安全檢查
    """
    
    def __init__(self):
        """Initialize code handler"""
        self.code_snippets: Dict[str, CodeSnippet] = {}
        
        # Configuration limits
        self.max_code_length = 10000  # Maximum characters
        self.max_lines = 500          # Maximum lines
        self.min_code_length = 5      # Minimum characters
        
        # Security patterns to check
        self.security_patterns = {
            'file_operations': [
                r'open\s*\(',
                r'file\s*\(',
                r'with\s+open',
                r'\.read\s*\(',
                r'\.write\s*\(',
                r'import\s+os',
                r'os\.',
                r'subprocess',
                r'eval\s*\(',
                r'exec\s*\(',
                r'fopen\s*\(',
                r'fstream',
                r'ifstream',
                r'ofstream'
            ],
            'network_operations': [
                r'import\s+requests',
                r'import\s+urllib',
                r'import\s+socket',
                r'socket\.',
                r'requests\.',
                r'urllib\.',
                r'http\.',
                r'fetch\s*\(',
                r'#include\s*<socket',
                r'#include\s*<netinet'
            ],
            'system_calls': [
                r'system\s*\(',
                r'shell_exec',
                r'passthru',
                r'__import__',
                r'importlib',
                r'exec\s*\(',
                r'popen\s*\(',
                r'#include\s*<cstdlib>'
            ]
        }
        
        # Check if clang is available for C++ validation
        self.clang_available = self._check_clang_availability()
        
        # Language-specific validation patterns
        self.language_patterns = {
            CodeLanguage.PYTHON: {
                'file_extensions': ['.py'],
                'keywords': ['def', 'class', 'import', 'from', 'if', 'for', 'while', 'try', 'except'],
                'syntax_patterns': [
                    r'def\s+\w+\s*\(',
                    r'class\s+\w+',
                    r'import\s+\w+',
                    r'from\s+\w+\s+import'
                ]
            },
            CodeLanguage.JAVASCRIPT: {
                'file_extensions': ['.js'],
                'keywords': ['function', 'var', 'let', 'const', 'if', 'for', 'while', 'try', 'catch'],
                'syntax_patterns': [
                    r'function\s+\w+\s*\(',
                    r'(var|let|const)\s+\w+',
                    r'=>',
                    r'console\.log'
                ]
            },
            CodeLanguage.JAVA: {
                'file_extensions': ['.java'],
                'keywords': ['public', 'private', 'class', 'interface', 'if', 'for', 'while', 'try', 'catch'],
                'syntax_patterns': [
                    r'public\s+class\s+\w+',
                    r'public\s+static\s+void\s+main',
                    r'System\.out\.print'
                ]
            },
            CodeLanguage.CPP: {
                'file_extensions': ['.cpp', '.cc', '.cxx', '.h', '.hpp'],
                'keywords': ['class', 'struct', 'namespace', 'template', 'public', 'private', 'protected', 
                           'virtual', 'const', 'static', 'if', 'for', 'while', 'try', 'catch'],
                'syntax_patterns': [
                    r'#include\s*<[^>]+>',
                    r'#include\s*"[^"]+"',
                    r'class\s+\w+',
                    r'struct\s+\w+',
                    r'namespace\s+\w+',
                    r'template\s*<',
                    r'std::\w+',
                    r'cout\s*<<',
                    r'cin\s*>>'
                ]
            }
        }
        
        logger.info("Code Handler initialized")
    
    def validate_code(self, code: str, language: str) -> CodeValidationResult:
        """
        Comprehensive code validation
        
        Args:
            code: Source code to validate
            language: Programming language
            
        Returns:
            Validation result with detailed analysis
        """
        try:
            errors = []
            warnings = []
            security_issues = []
            suggestions = []
            
            # Basic length and structure validation
            char_count = len(code)
            line_count = len(code.splitlines())
            
            # Check length limits
            if char_count < self.min_code_length:
                errors.append(f"程式碼太短，至少需要 {self.min_code_length} 個字元")
            
            if char_count > self.max_code_length:
                errors.append(f"程式碼太長，最多允許 {self.max_code_length} 個字元")
            
            if line_count > self.max_lines:
                errors.append(f"程式碼行數太多，最多允許 {self.max_lines} 行")
            
            # Check for empty or whitespace-only code
            if not code.strip():
                errors.append("程式碼不能為空")
                return CodeValidationResult(
                    is_valid=False,
                    language=language,
                    errors=errors,
                    warnings=warnings,
                    line_count=line_count,
                    char_count=char_count,
                    complexity_score=0,
                    security_issues=security_issues,
                    suggestions=suggestions
                )
            
            # Language-specific validation
            language_enum = self._get_language_enum(language)
            if language_enum:
                lang_errors, lang_warnings = self._validate_language_syntax(code, language_enum)
                errors.extend(lang_errors)
                warnings.extend(lang_warnings)
            
            # Security checks
            security_issues = self._check_security_issues(code)
            
            # Complexity analysis
            complexity_score = self._calculate_complexity(code, language)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(code, language, complexity_score)
            
            # Determine if code is valid
            is_valid = len(errors) == 0
            
            return CodeValidationResult(
                is_valid=is_valid,
                language=language,
                errors=errors,
                warnings=warnings,
                line_count=line_count,
                char_count=char_count,
                complexity_score=complexity_score,
                security_issues=security_issues,
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Error validating code: {e}")
            return CodeValidationResult(
                is_valid=False,
                language=language,
                errors=[f"驗證過程發生錯誤: {str(e)}"],
                warnings=[],
                line_count=0,
                char_count=0,
                complexity_score=0,
                security_issues=[],
                suggestions=[]
            )
    
    def store_code_snippet(self, 
                          session_id: str, 
                          code: str, 
                          language: str,
                          problem_description: str = "",
                          is_solution: bool = False) -> str:
        """
        Store code snippet with validation
        
        Args:
            session_id: Interview session ID
            code: Source code
            language: Programming language
            problem_description: Description of the problem
            is_solution: Whether this is a solution attempt
            
        Returns:
            Snippet ID
        """
        try:
            # Validate code first
            validation_result = self.validate_code(code, language)
            
            # Generate unique snippet ID
            snippet_id = self._generate_snippet_id(session_id, code)
            
            # Create snippet object
            snippet = CodeSnippet(
                snippet_id=snippet_id,
                session_id=session_id,
                code=code,
                language=language,
                timestamp=time.time(),
                validation_result=validation_result,
                is_solution=is_solution,
                problem_description=problem_description
            )
            
            # Store snippet
            self.code_snippets[snippet_id] = snippet
            
            logger.info(f"Stored code snippet {snippet_id} for session {session_id}")
            return snippet_id
            
        except Exception as e:
            logger.error(f"Error storing code snippet: {e}")
            raise
    
    def get_code_snippet(self, snippet_id: str) -> Optional[CodeSnippet]:
        """
        Retrieve code snippet by ID
        
        Args:
            snippet_id: Snippet identifier
            
        Returns:
            Code snippet or None if not found
        """
        return self.code_snippets.get(snippet_id)
    
    def get_session_snippets(self, session_id: str) -> List[CodeSnippet]:
        """
        Get all code snippets for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of code snippets
        """
        return [
            snippet for snippet in self.code_snippets.values()
            if snippet.session_id == session_id
        ]
    
    def format_code(self, code: str, language: str) -> str:
        """
        Basic code formatting
        
        Args:
            code: Source code to format
            language: Programming language
            
        Returns:
            Formatted code
        """
        try:
            # Basic formatting for Python
            if language.lower() == 'python':
                return self._format_python_code(code)
            
            # For other languages, just clean up whitespace
            lines = code.splitlines()
            formatted_lines = []
            
            for line in lines:
                # Remove trailing whitespace
                cleaned_line = line.rstrip()
                if cleaned_line:  # Skip empty lines
                    formatted_lines.append(cleaned_line)
            
            return '\n'.join(formatted_lines)
            
        except Exception as e:
            logger.warning(f"Error formatting code: {e}")
            return code  # Return original if formatting fails
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported programming languages
        
        Returns:
            List of language names
        """
        return [lang.value for lang in CodeLanguage]
    
    def _get_language_enum(self, language: str) -> Optional[CodeLanguage]:
        """Convert string to language enum"""
        try:
            return CodeLanguage(language.lower())
        except ValueError:
            return None
    
    def _validate_language_syntax(self, code: str, language: CodeLanguage) -> Tuple[List[str], List[str]]:
        """
        Language-specific syntax validation
        
        Args:
            code: Source code
            language: Programming language enum
            
        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []
        
        try:
            if language == CodeLanguage.PYTHON:
                errors, warnings = self._validate_python_syntax(code)
            elif language == CodeLanguage.JAVASCRIPT:
                errors, warnings = self._validate_javascript_syntax(code)
            elif language == CodeLanguage.CPP:
                errors, warnings = self._validate_cpp_syntax_with_clang(code)
            # Add more language validations as needed
            
        except Exception as e:
            logger.warning(f"Error in language validation: {e}")
            warnings.append("語法檢查過程中發生問題")
        
        return errors, warnings
    
    def _validate_python_syntax(self, code: str) -> Tuple[List[str], List[str]]:
        """Validate Python syntax"""
        errors = []
        warnings = []
        
        try:
            # Try to parse the code
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Python 語法錯誤: {e.msg} (第 {e.lineno} 行)")
        except Exception as e:
            warnings.append(f"Python 程式碼分析警告: {str(e)}")
        
        return errors, warnings
    
    def _validate_javascript_syntax(self, code: str) -> Tuple[List[str], List[str]]:
        """Basic JavaScript syntax validation"""
        errors = []
        warnings = []
        
        # Basic bracket matching
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []
        
        for char in code:
            if char in brackets:
                stack.append(brackets[char])
            elif char in brackets.values():
                if not stack or stack.pop() != char:
                    errors.append("JavaScript 括號不匹配")
                    break
        
        if stack:
            errors.append("JavaScript 括號未閉合")
        
        return errors, warnings
    
    def _check_security_issues(self, code: str) -> List[str]:
        """Check for potential security issues"""
        security_issues = []
        
        for category, patterns in self.security_patterns.items():
            for pattern in patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    security_issues.append(f"檢測到潛在的安全風險: {category}")
                    break  # Only report once per category
        
        return security_issues
    
    def _calculate_complexity(self, code: str, language: str) -> int:
        """Calculate basic code complexity score"""
        try:
            lines = code.splitlines()
            complexity = 0
            
            # Count different complexity indicators
            complexity += len([line for line in lines if line.strip()])  # Non-empty lines
            complexity += code.count('if') * 2  # Conditional statements
            complexity += code.count('for') * 2  # Loops
            complexity += code.count('while') * 2
            
            # Language-specific complexity calculations
            if language.lower() == 'python':
                complexity += code.count('def') * 3  # Function definitions
                complexity += code.count('class') * 4  # Class definitions
            elif language.lower() == 'cpp':
                complexity += len([line for line in lines if 'int ' in line or 'void ' in line or 'double ' in line]) * 3
                complexity += code.count('class') * 4
                complexity += code.count('struct') * 3
                complexity += code.count('template') * 5
                complexity += code.count('namespace') * 2
            elif language.lower() in ['javascript', 'typescript']:
                complexity += code.count('function') * 3
                complexity += code.count('class') * 4
                complexity += code.count('=>') * 2  # Arrow functions
            elif language.lower() == 'java':
                complexity += len([line for line in lines if 'public ' in line or 'private ' in line]) * 3
                complexity += code.count('class') * 4
                complexity += code.count('interface') * 4
            
            # Common complexity indicators for all languages
            complexity += code.count('switch') * 3
            complexity += code.count('case') * 1
            complexity += code.count('try') * 2
            complexity += code.count('catch') * 2
            
            # Normalize to 0-100 scale
            return min(complexity, 100)
            
        except Exception:
            return 0
    
    def _generate_suggestions(self, code: str, language: str, complexity: int) -> List[str]:
        """Generate code improvement suggestions"""
        suggestions = []
        
        try:
            lines = code.splitlines()
            
            # Check for very long lines
            long_lines = [i for i, line in enumerate(lines, 1) if len(line) > 100]
            if long_lines:
                suggestions.append("考慮將過長的程式碼行拆分（建議每行不超過100字元）")
            
            # Check for lack of comments
            comment_count = sum(1 for line in lines if '#' in line or '//' in line)
            if len(lines) > 10 and comment_count == 0:
                suggestions.append("建議增加註解說明程式碼邏輯")
            
            # Complexity suggestions
            if complexity > 50:
                suggestions.append("程式碼複雜度較高，考慮拆分為更小的函數")
            
            # Language-specific suggestions
            if language.lower() == 'python':
                if 'print(' in code and code.count('print(') > 3:
                    suggestions.append("考慮使用 logging 模組取代過多的 print 語句")
            elif language.lower() == 'cpp':
                if 'using namespace std' in code:
                    suggestions.append("考慮使用 std:: 前綴而非 'using namespace std' 以避免命名空間污染")
                if 'cout' in code and '#include <iostream>' not in code:
                    suggestions.append("使用 cout 需要 #include <iostream>")
                if code.count('new ') > 0 and code.count('delete ') == 0:
                    suggestions.append("使用 new 分配記憶體後記得使用 delete 釋放，或考慮使用智慧指標")
                if 'malloc' in code or 'free' in code:
                    suggestions.append("C++ 中建議使用 new/delete 或智慧指標，而非 malloc/free")
            
        except Exception as e:
            logger.warning(f"Error generating suggestions: {e}")
        
        return suggestions
    
    def _format_python_code(self, code: str) -> str:
        """Basic Python code formatting"""
        try:
            lines = code.splitlines()
            formatted_lines = []
            indent_level = 0
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    formatted_lines.append('')
                    continue
                
                # Adjust indent level for closing statements
                if stripped.startswith(('except', 'elif', 'else', 'finally')):
                    indent_level = max(0, indent_level - 1)
                elif stripped.startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'with ')):
                    pass  # Keep current indent
                elif stripped.endswith(':'):
                    pass  # Keep current indent, will increase after
                
                # Apply indentation
                formatted_line = '    ' * indent_level + stripped
                formatted_lines.append(formatted_line)
                
                # Increase indent for next line if needed
                if stripped.endswith(':'):
                    indent_level += 1
            
            return '\n'.join(formatted_lines)
            
        except Exception:
            return code  # Return original if formatting fails
    
    def _check_clang_availability(self) -> bool:
        """Check if clang is available on the system"""
        try:
            result = subprocess.run(['clang++', '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _validate_cpp_syntax_with_clang(self, code: str) -> Tuple[List[str], List[str]]:
        """Validate C++ syntax using clang compiler"""
        errors = []
        warnings = []
        
        # If clang is not available, fall back to basic validation
        if not self.clang_available:
            return self._validate_cpp_syntax_basic(code)
        
        try:
            # Create a temporary file with C++ code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            try:
                # Run clang++ to check syntax
                result = subprocess.run([
                    'clang++', 
                    '-fsyntax-only',  # Only check syntax, don't compile
                    '-std=c++17',     # Use C++17 standard
                    '-Wall',          # Enable warnings
                    temp_file_path
                ], capture_output=True, text=True, timeout=10)
                
                if result.stderr:
                    # Parse clang error messages
                    stderr_lines = result.stderr.strip().split('\n')
                    for line in stderr_lines:
                        if 'error:' in line:
                            # Extract error message
                            error_msg = line.split('error:')[-1].strip()
                            errors.append(f"C++ 語法錯誤: {error_msg}")
                        elif 'warning:' in line:
                            # Extract warning message
                            warning_msg = line.split('warning:')[-1].strip()
                            warnings.append(f"C++ 警告: {warning_msg}")
                
                # If no errors from clang, but return code is not 0
                if result.returncode != 0 and not errors:
                    errors.append("C++ 程式碼包含語法錯誤")
                    
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass
                    
        except subprocess.TimeoutExpired:
            warnings.append("C++ 語法檢查超時")
        except Exception as e:
            logger.warning(f"Error using clang for C++ validation: {e}")
            warnings.append("C++ 語法檢查過程中發生問題")
        
        return errors, warnings
    
    def _validate_cpp_syntax_basic(self, code: str) -> Tuple[List[str], List[str]]:
        """Basic C++ syntax validation (fallback when clang is not available)"""
        errors = []
        warnings = []
        
        try:
            lines = code.splitlines()
            
            # Basic bracket matching for C++
            brackets = {'(': ')', '[': ']', '{': '}'}
            stack = []
            line_num = 0
            
            for line in lines:
                line_num += 1
                # Skip comments
                if '//' in line:
                    line = line[:line.index('//')]
                
                for char in line:
                    if char in brackets:
                        stack.append((brackets[char], line_num))
                    elif char in brackets.values():
                        if not stack:
                            errors.append(f"C++ 第 {line_num} 行: 多餘的 '{char}'")
                            break
                        expected_char, _ = stack.pop()
                        if expected_char != char:
                            errors.append(f"C++ 第 {line_num} 行: 括號不匹配，期望 '{expected_char}' 但找到 '{char}'")
                            break
            
            # Check for unclosed brackets
            if stack:
                for char, line_num in stack:
                    errors.append(f"C++ 第 {line_num} 行: 未閉合的括號 '{char}'")
            
            # Check for basic C++ syntax patterns
            code_lower = code.lower()
            
            # Check for main function
            if 'int main' not in code and 'void main' not in code and len(lines) > 5:
                warnings.append("C++ 程式通常需要 main 函數作為程式入口點")
            
            # Check for missing includes
            has_includes = any(line.strip().startswith('#include') for line in lines)
            has_std_usage = 'std::' in code or 'cout' in code or 'cin' in code
            
            if has_std_usage and not has_includes:
                warnings.append("使用了標準函式庫但未發現 #include 指令")
            
            # Check for missing semicolons (basic check)
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped and not stripped.startswith(('#', '//', '}')):
                    # Lines that typically should end with semicolon
                    if (any(keyword in stripped for keyword in ['int ', 'char ', 'double ', 'float ', 'bool ']) 
                        or 'cout' in stripped or 'cin' in stripped
                        or stripped.startswith('return')):
                        if not stripped.endswith((';', '{', '}')):
                            warnings.append(f"第 {i} 行可能缺少分號")
            
            # Check for namespace usage
            if 'using namespace std' not in code and 'std::' not in code and ('cout' in code or 'cin' in code):
                warnings.append("使用了 cout/cin 但未指定 std 命名空間")
                
        except Exception as e:
            logger.warning(f"Error in basic C++ syntax validation: {e}")
            warnings.append("C++ 語法檢查過程中發生問題")
        
        return errors, warnings

    def _generate_snippet_id(self, session_id: str, code: str) -> str:
        """Generate unique snippet ID"""
        content = f"{session_id}_{code}_{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()[:12] 
import re

# Read the entire file
with open('research_agent/manager.py', 'r', encoding='utf-8') as file:
    content = file.read()

# Find and fix the problematic section
# Pattern matches an unescaped single closing brace in the JavaScript code
fixed_content = re.sub(r'if \(confirm\([^)]+\)\) \{\{[^}]+\n[^}]+\n[^}]+\n                    }(\n                \}\);)',
                      r'if (confirm(\'Would you like to search for this follow-up question?\')) {{\n                        // You could implement this in various ways depending on your setup\n                        // For example, posting to a server endpoint or opening in new tab\n                        console.log(\'User wants to search for:\', this.textContent);\n                    }}\1',
                      content)

# Write the fixed content back to the file
with open('research_agent/manager.py', 'w', encoding='utf-8') as file:
    file.write(fixed_content)

print("Fixed the syntax error in manager.py")

#!/usr/bin/env python3
"""
ShellOS Scripting Language (SSL) Interpreter
A simple scripting language for ShellOS
"""

import sys
import os
import subprocess

class SSLInterpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}

    def execute_file(self, filename):
        """Execute a .ssl file"""
        if not os.path.exists(filename):
            print(f"Error: File '{filename}' not found.")
            return

        with open(filename, 'r') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # Skip empty lines and comments

            try:
                self.execute_line(line)
            except Exception as e:
                print(f"Error on line {line_num}: {e}")

    def execute_line(self, line):
        """Execute a single line of SSL code"""
        tokens = self.tokenize(line)

        if not tokens:
            return

        command = tokens[0].lower()

        if command == 'print':
            self.cmd_print(tokens[1:])
        elif command == 'var' or command == 'set':
            self.cmd_var(tokens[1:])
        elif command == 'run':
            self.cmd_run(tokens[1:])
        elif command == 'input':
            self.cmd_input(tokens[1:])
        else:
            raise ValueError(f"Unknown command: {command}")

    def tokenize(self, line):
        """Simple tokenizer - splits on spaces but handles quoted strings"""
        tokens = []
        current_token = ""
        in_quotes = False
        quote_char = None

        for char in line:
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
                current_token += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                current_token += char
                tokens.append(current_token)
                current_token = ""
                quote_char = None
            elif char == ' ' and not in_quotes:
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
            else:
                current_token += char

        if current_token:
            tokens.append(current_token)

        return tokens

    def evaluate_expression(self, expr):
        """Evaluate a simple expression"""
        expr = expr.strip()

        # Check if it's a variable
        if expr in self.variables:
            return self.variables[expr]

        # Check if it's a quoted string
        if (expr.startswith('"') and expr.endswith('"')) or \
           (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]

        # Try to evaluate as number
        try:
            return int(expr)
        except ValueError:
            try:
                return float(expr)
            except ValueError:
                pass

        # Check for string concatenation with +
        if '+' in expr:
            parts = expr.split('+', 1)
            left = self.evaluate_expression(parts[0])
            right = self.evaluate_expression(parts[1])
            return str(left) + str(right)

        return expr

    def cmd_print(self, args):
        """Print command: print message or print variable"""
        if not args:
            print()
            return

        message = ""
        for arg in args:
            if message:
                message += " "
            message += str(self.evaluate_expression(arg))

        print(message)

    def cmd_var(self, args):
        """Variable assignment: var name = value"""
        if len(args) < 3 or args[1] != '=':
            raise ValueError("Variable syntax: var name = value")

        var_name = args[0]
        value = self.evaluate_expression(' '.join(args[2:]))
        self.variables[var_name] = value

    def cmd_run(self, args):
        """Run Python script: run filename.py [args...]"""
        if not args:
            raise ValueError("Run command requires a filename")

        filename = args[0]

        # Remove quotes if present
        if (filename.startswith('"') and filename.endswith('"')) or \
           (filename.startswith("'") and filename.endswith("'")):
            filename = filename[1:-1]

        if not os.path.exists(filename):
            raise ValueError(f"File '{filename}' not found")

        # Prepare arguments for subprocess
        cmd_args = [sys.executable, filename] + args[1:]

        try:
            result = subprocess.run(cmd_args, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout, end='')
            if result.stderr:
                print(result.stderr, end='')
        except Exception as e:
            raise ValueError(f"Failed to run {filename}: {e}")

    def cmd_input(self, args):
        """Input command: input variable_name"""
        if not args:
            raise ValueError("Input command requires a variable name")

        var_name = args[0]
        value = input()
        self.variables[var_name] = value

def main():
    if len(sys.argv) != 2:
        print("Usage: python ssl.py <filename.ssl>")
        sys.exit(1)

    filename = sys.argv[1]
    if not filename.endswith('.ssl'):
        print("Error: File must have .ssl extension")
        sys.exit(1)

    interpreter = SSLInterpreter()
    interpreter.execute_file(filename)

if __name__ == "__main__":
    main()

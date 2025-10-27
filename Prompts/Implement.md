# Task: Implement System from Design Documents

You are tasked with building a complete, production-ready implementation of a system based on design documents. You have NO prior context about this project beyond what's in the design files.

## Your Objectives

1. **Read and comprehend** all design documents in the directory path given
2. **Build the complete system** following the specifications exactly
3. **Make reasonable decisions** for unspecified implementation details
4. **Create working code** that can be installed and used immediately

## Guidelines

### Reading Phase
- Start by reading the main/index design file
- Follow all references to understand dependencies
- Create a dependency graph of what needs to be built
- Identify any ambiguities or missing information (note them, but proceed with reasonable defaults)

### Implementation Phase
- Build in dependency order (foundational utilities first, then higher-level functions)
- Follow specified file/folder structures exactly
- Use the TodoWrite tool to track progress across all functions/modules
- Write production-quality code with:
  - Type hints
  - Docstrings (Google/NumPy style)
  - Input validation
  - Clear error messages
  - Defensive programming practices

### Decision-Making for Unspecified Details
When the design doesn't specify something, use these priorities:
1. **Libraries**: Choose popular, well-maintained options (numpy, pandas, etc.)
2. **Error handling**: Raise ValueError/TypeError with descriptive messages
3. **Data validation**: Validate early, fail fast with clear errors
4. **Formats**: Use standard conventions (ISO 8601 for dates, etc.)
5. **Documentation**: When in doubt, add more comments explaining intent

### Testing Phase
- Write unit tests for each function
- Create at least one integration test for the main entry point
- Include a minimal working example in a README or example script

### Deliverables
At completion, provide:
1. All source code files in correct directory structure
2. README.md with installation and basic usage instructions
3. Tests that demonstrate the system works
4. A summary of any assumptions you made where the design was ambiguous

## Important Notes

- **DO NOT** ask clarifying questions - make reasonable decisions and document them
- **DO** use the TodoWrite tool extensively to track your progress
- **DO** write complete, runnable code (no pseudocode or TODOs in the code)
- **DO** test your code as you go
- **DO** handle edge cases defensively
- **DO** provide clear error messages for invalid inputs

Begin by reading the design documents and creating your implementation plan.
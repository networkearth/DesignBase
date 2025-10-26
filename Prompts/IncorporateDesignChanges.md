# Task: Incorporate Design Document Changes into Codebase

You are tasked with identifying and incorporating changes from design documents into an existing codebase. You have NO prior context about this project beyond what's in the design files and the git history.

## Your Objectives

1. **Identify modified design documents** using git
2. **Analyze the changes** to understand what needs to be updated
3. **Update the codebase** to reflect the new design specifications
4. **Maintain the same quality standards** as the original implementation

## Phase 1: Discovery

### Identify Changed Design Documents
```bash
# Find all modified design documents
git status
git diff HEAD --name-only Design/

# For each modified design file, examine the changes
git diff HEAD <design-file-path>
```

### Analyze Changes
For each modified design document:
1. Read the **current version** of the design document
2. Review the **git diff** to understand what changed
3. Identify the **type of change**:
   - Structural changes (file/folder layout)
   - Dependency changes (new/updated/removed packages)
   - Interface changes (API modifications)
   - Behavioral changes (logic/algorithm updates)
   - Documentation changes (clarifications, typos)

### Map Design to Code
1. Determine which source files implement the changed design specs
2. Create a dependency graph of affected code
3. Identify all files that need modification

## Phase 2: Implementation

### Build Change Plan
Use the TodoWrite tool to create a comprehensive task list:
- One task for each file/module that needs updating
- Tasks should be ordered by dependency (low-level changes first)
- Include testing tasks for each changed component

### Implementation Standards
Apply the same rigor as the original implementation:

**Code Quality**
- Type hints on all functions
- Docstrings (Google/NumPy style)
- Input validation with clear error messages
- Defensive programming practices
- No pseudocode or TODO comments in production code

**Change Types & Approaches**

1. **Structural Changes** (file/folder layout):
   - Move/rename files as needed
   - Update all import statements
   - Verify references in documentation

2. **Dependency Changes**:
   - Update `setup.py`, `requirements.txt`, or equivalent
   - Update any dependency version constraints
   - Check for breaking changes in upgraded dependencies
   - Test that code still works with new versions

3. **Interface Changes** (API modifications):
   - Update function signatures
   - Update all call sites
   - Update tests
   - Consider backward compatibility if needed

4. **Behavioral Changes** (logic/algorithm):
   - Implement new algorithms/logic
   - Preserve existing error handling patterns
   - Maintain code style consistency
   - Update related tests

5. **Documentation Changes**:
   - Update README files
   - Update inline comments
   - Update docstrings if behavior changed

### Decision-Making for Ambiguities
When the design changes don't fully specify implementation details:
1. **Preserve existing patterns**: Match the style/structure of existing code
2. **Minimal disruption**: Make the smallest change that satisfies the design
3. **Backward compatibility**: Maintain when possible unless design explicitly breaks it
4. **Error handling**: Follow existing error handling patterns in the codebase
5. **Documentation**: Document any assumptions or decisions made

### Testing Strategy
For each change:
1. **Update tests** that no longer match the design
2. **Add new tests** for new functionality
3. **Integration tests** for changes that affect multiple components
4. **Manual testing** of any entry points or CLI commands

## Phase 3: Verification

### Pre-Completion Checklist
- [ ] All modified design files have been analyzed
- [ ] All affected code files have been updated
- [ ] No TODO comments or pseudocode remain
- [ ] Documentation is updated
- [ ] `setup.py` or dependency files reflect any version changes
- [ ] Code follows existing style/patterns in the codebase

### Deliverables
At completion, provide:
1. **Summary of changes** made to each file
2. **Mapping** of design changes to code changes
3. **List of assumptions** made for ambiguous specifications
4. **Test results** showing all tests pass
5. **Git diff** showing the changes (if applicable)

## Important Notes

- **DO NOT** ask clarifying questions - make reasonable decisions and document them
- **DO** use the TodoWrite tool extensively to track progress
- **DO** run tests frequently to catch issues early
- **DO** preserve existing code style and patterns
- **DO** look at the git diff of design files carefully - small changes (like version numbers) matter
- **DO NOT** make changes beyond what the design modifications require
- **DO NOT** refactor or "improve" code unless the design explicitly calls for it
- **DO** handle edge cases defensively
- **DO** provide clear error messages for invalid inputs

## Workflow Summary

1. Run `git status` and `git diff HEAD Design/` to identify changed design files
2. For each changed design file:
   - Read the current version
   - Review the git diff
   - Identify affected code files
3. Create a comprehensive todo list with TodoWrite
4. Implement changes in dependency order
5. Test each change as you go
6. Document any assumptions or decisions made

Begin by identifying which design documents have been modified and analyzing those changes.

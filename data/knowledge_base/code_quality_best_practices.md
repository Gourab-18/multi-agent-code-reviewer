# Code Quality & Clean Code Best Practices

## SOLID Principles
These 5 principles facilitate robust and maintainable object-oriented design.

### 1. Single Responsibility Principle (SRP)
- **Concept**: A class or function should have one, and only one, reason to change.
- **Review Check**: Does this class handle both database operations AND business logic? Split it.

### 2. Open/Closed Principle (OCP)
- **Concept**: Software entities should be open for extension but closed for modification.
- **Review Check**: Can we add new behavior by adding a new class instead of modifying existing `if/else` statements?

### 3. Liskov Substitution Principle (LSP)
- **Concept**: Objects of a superclass should be replaceable with objects of its subclasses without breaking the application.
- **Review Check**: Does the subclass throw an exception for a method defined in the parent? (e.g., `Square` inheriting from `Rectangle` and breaking `setWidth`).

### 4. Interface Segregation Principle (ISP)
- **Concept**: Many client-specific interfaces are better than one general-purpose interface.
- **Review Check**: Are we forcing a class to implement methods it doesn't use?

### 5. Dependency Inversion Principle (DIP)
- **Concept**: Depend upon abstractions, not concretions.
- **Review Check**: injecting dependencies (e.g., passing a database interface) rather than instantiating them inside the class.

## DRY (Don't Repeat Yourself)
- **Rule**: Every piece of knowledge must have a single, unambiguous, authoritative representation within a system.
- **Application**: Modularize code. If you copy-paste code more than once, refactor it into a function or component.

## KISS (Keep It Simple, Stupid)
- **Rule**: Simplicity should be a key goal in design and unnecessary complexity should be avoided.
- **Application**: Prefer readable, simple code over clever, "one-liner" solutions that are hard to debug.

## Readability & Naming conventions

### Meaningful Names
- **Variables**: Use intent-revealing names. `days_since_creation` is better than `d`.
- **Functions**: Should be verbs or verb phrases. `calculate_total()` is better than `total()`.
- **Booleans**: Should sound like questions. `is_valid`, `has_permission`.

### Magic Numbers/Strings
- **Avoid**: `if status == 2:`
- **Prefer**: `if status == STATUS_COMPLETED:` (Use constants or Enums).

## Code Structure

### Function Length
- **Guideline**: Functions should be small (ideally < 20-30 lines).
- **Benefit**: Easier to test, understand, and reuse.

### Nesting
- **Guideline**: Avoid deep nesting (arrows code).
- **Fix**: Use guard clauses (return early) to flatten the structure.
  ```python
  # Bad
  def process(item):
      if item:
          if item.active:
              do_something(item)
  
  # Good
  def process(item):
      if not item or not item.active:
          return
      do_something(item)
  ```

## Commenting & Documentation
- **Why vs What**: Comments should explain *why* something is done, not *what* the code is doing (the code should explain that).
- **Docstrings**: Public functions and classes must have docstrings explaining arguments, return values, and exceptions.
- **Todo**: Use `# TODO:` to mark technical debt or future improvements, but valid code should not rely on them.

## Testing
- **Unit Tests**: Test individual components in isolation.
- **Coverage**: Aim for high test coverage, but value assertion quality over raw percentage.
- **TDD**: Consider Test Driven Development (write tests before implementation).

# Performance Best Practices

## Algorithmic Efficiency

### Big O Notation
- **Review Requirement**: Analyze loops and recursion for time complexity.
- **O(N^2) Warning**: Nested loops over large datasets are a major red flag.
- **O(N) Expectation**: Aim for linear time complexity for data processing tasks where possible.
- **Space Complexity**: Watch for algorithms creating large intermediate data structures.

### Data Structures
- **Lookups**: Use Hash Maps (Dictionaries in Python, Objects/Maps in JS) for O(1) lookups instead of iterating lists O(N).
- **Sets**: Use Sets for membership testing and duplicate removal.

## Database Optimization

### Query Optimization
- **N+1 Problem**: Identifying code that executes N queries for N parent items (e.g., fetching comments for every post in a loop).
  - *Fix*: Use `JOIN`s or eager loading (e.g., `select_related` / `prefetch_related` in Django).
- **Indexing**: Ensure columns used in `WHERE`, `ORDER BY`, and `JOIN` clauses are indexed.
- **Selectivity**: Avoid `SELECT *`. Retrieve only necessary columns to reduce network load and memory usage.

### Connections
- **Pooling**: Ensure database connection pooling is used (e.g., SQLAlchemy default pool) to avoid overhead of opening/closing connections.

## Memory Management

### Python Specifics
- **Generators**: Use generators (`yield`) instead of returning large lists for memory-efficient iteration.
  ```python
  # Memory heavy
  def get_lines():
      return file.readlines() 
  
  # Memory efficient
  def get_lines_gen():
      for line in file:
          yield line
  ```
- **Context Managers**: Always use `with` statements for file I/O to ensure resources are released immediately.

### JavaScript Specifics
- **Event Listeners**: Ensure event listeners are removed when components unmount to prevent memory leaks.
- **Closures**: Be mindful of closures retaining references to large objects unnecessarily.

## Network & I/O

### Asynchronous Operations
- **Non-blocking**: Use `async`/`await` for I/O bound operations (DB, network requests) to prevent blocking the main thread.
- **Parallelism**: Use `asyncio.gather` (Python) or `Promise.all` (JS) to execute independent tasks concurrently.

### Caching Strategies
- **Memoization**: Cache results of expensive function calls.
- **Application Cache**: Use Redis or Memcached for frequently accessed data that changes rarely.
- **HTTP Caching**: properly utilize `Cache-Control` headers.

## Frontend Performance (JS/React)

### Rendering
- **Virtual DOM**: Minimize direct DOM manipulation; let the framework handle it.
- **Re-renders**: Use `React.memo`, `useMemo`, and `useCallback` to prevent unnecessary re-renders of child components.
- **Large Lists**: Use virtualization (windowing) for rendering long lists (e.g., `react-window`).

### Bundle Size
- **Code Splitting**: Use lazy loading (`React.lazy`) for routes/components not needed immediately.
- **Tree Shaking**: Ensure build tools (Webpack/Vite) are configured to remove unused code.
- **Dependencies**: Audit imports. Don't import a whole library (e.g., `lodash`) when a single utility function is needed.

## General profiling
- **Premature Optimization**: "Premature optimization is the root of all evil". Profile first, then optimize. Identify bottlenecks using tools like `cProfile` (Python) or Chrome DevTools (JS).

# Security Best Practices for Code Review

## OWASP Top 10 High-Level Summary
Code reviews must prioritize the identification of vulnerabilities listed in the OWASP Top 10.

### 1. Broken Access Control
- **Description**: Users acting outside of their intended permissions.
- **Checklist**:
  - Verify that every endpoint checks for appropriate roles/permissions.
  - Look for Insecure Direct Object References (IDOR). E.g., `user_id` passed in URL without verification that the logged-in user owns that `user_id`.
  - Ensure failure defaults to "deny".
- **Example Fix**:
  ```python
  # BAD
  @app.route('/data/<user_id>')
  def get_data(user_id):
      return db.get_user_data(user_id)

  # GOOD
  @app.route('/data/<user_id>')
  @require_auth
  def get_data(user_id):
      if current_user.id != user_id:
          raise Forbidden()
      return db.get_user_data(user_id)
  ```

### 2. Cryptographic Failures
- **Description**: Failures related to cryptography, often leading to sensitive data exposure.
- **Checklist**:
  - **NEVER** hardcode keys or passwords.
  - Ensure passwords are hashed using strong algorithms (Argon2, bcrypt), not MD5 or SHA1.
  - Ensure TLS/SSL is used for all data in transit.
  - Don't store sensitive data (PII, Credit Cards) unless absolutely necessary.

### 3. Injection
- **Description**: User-supplied data is not validated, filtered, or sanitized by the application.
- **Types**: SQL Injection, Command Injection, LDAP Injection.
- **Checklist**:
  - Verify use of Parameterized Queries or ORMs for all database interactions.
  - Flag any use of `eval()`, `exec()`, or `os.system()` with user input.
  - Sanitize input at the boundary.

### 4. Insecure Design
- **Description**: Risks related to design flaws and architecture.
- **Checklist**:
  - Check if rate limiting is implemented on sensitive endpoints (login, password reset).
  - Verify business logic assumes "unknown" state is unsafe.

### 5. Security Misconfiguration
- **Description**: Missing security hardening across the application stack.
- **Checklist**:
  - Debug mode must be disabled in production.
  - Detailed error messages should not be exposed to end users (stack traces).

### 6. Vulnerable and Outdated Components
- **Description**: Using libraries with known vulnerabilities.
- **Checklist**:
  - Check `requirements.txt` or `package.json` for old versions.
  - Recommend tools like `dependabot` or `snyk`.

### 7. Identification and Authentication Failures
- **Description**: Confirmation of user's identity, session management.
- **Checklist**:
  - Ensure session IDs are not in the URL.
  - Check for strong password policies.
  - Ensure session timeout is implemented.

### 8. Software and Data Integrity Failures
- **Description**: Code and infrastructure that does not protect against integrity violations.
- **Checklist**:
  - CI/CD pipelines should sign artifacts.
  - Deserialization of untrusted data (e.g. `pickle.loads` in Python) is critical.

### 9. Security Logging and Monitoring Failures
- **Description**: Insufficient logging and detection.
- **Checklist**:
  - Critical actions (login, payment, access control failures) must be logged.
  - Logs should not contain sensitive info (PII, tokens).

### 10. Server-Side Request Forgery (SSRF)
- **Description**: Web application fetching a remote resource without validating the user-supplied URL.
- **Checklist**:
  - Validate and whitelist target domains for any outbound HTTP requests initiated by user input.

## Secure Coding Principles (General)

### Input Validation
- **Whitelisting vs Blacklisting**: Always prefer whitelisting allowed characters/inputs over blacklisting bad ones.
- **Type Checking**: Ensure input data is of the expected type (int vs string).

### Output Encoding
- **XSS Prevention**: Context-aware encoding when rendering user input in HTML, JavaScript, or CSS.
- **React/Vue**: Most modern frameworks handle this, but watch out for `dangerouslySetInnerHTML` or `v-html`.

### Error Handling
- **Fail Safe**: Systems should fail in a secure manner. If an error occurs during an auth check, the user should not be logged in.
- **Information Leakage**: Do not reveal implementation details in error messages.

### Secrets Management
- **Environment Variables**: Use `.env` files and environment variables.
- **Vaults**: Use secrets management services (AWS Secrets Manager, HashiCorp Vault) for production.

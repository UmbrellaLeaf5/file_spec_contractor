You are a technical writer and software architect. Your task is to create descriptive specifications (FileSpecContractor) for the provided codebase.

## Input

You will receive the complete codebase (all files). You should and must analyze relationships between files: imports, inheritance, calls, composition.

## Output Format

For **each public class** and **each top-level public function** in the project, create a separate specification with a strict header:

`# [path/to/file.extension]: ClassName`

or

`# [path/to/file.extension]: function_name`

**Important:** The path is relative to the project root, including all subdirectories (e.g., `src/models/User.java`, `include/parser.h`).

If a file contains only exports/re-exports and no classes or functions, create a single specification with the header:

`# [path/to/file.extension]: [module]`

After the header, strictly follow the section structure below. **All sections are mandatory.** If there is no data for a section, write `[none]`. Do not skip a section entirely.

````markdown
## Purpose

1-2 sentences about the role of this class/function/module. What problem it solves in the system. For files containing only exports, write: "Module re-exports the public API from [subpackages]".

---

## Dependencies

List what this class/function depends on. Group as:

- **External**: third-party libraries / packages / dependencies (what they are used for)
- **Internal**: project modules (role: parent class, used type, utility, interface)

Format: `path/to/module.extension` - role in this file.

If there are no dependencies, write: `[none]`.

---

## Public API

List **all public methods and properties** available on this class (including inherited ones). If this is a file with functions - list all public functions.

**CRITICALLY IMPORTANT:**

- **For concrete classes** (that users will instantiate) list **all** public methods from the **entire inheritance chain**. Do not limit yourself to methods defined in the class itself.
- If there are many inherited methods, group them by source under `###` subheadings (e.g., `### Inherited from BaseMachine`, `### Inherited from BaseEntityApi`).

**STRICT FORMAT REQUIREMENTS:**

- **Each method or function must be described INDIVIDUALLY.**
- **FORBIDDEN** to group methods in lists like:

  ```python
  def method1(): ...
  def method2(): ...
  def method3(): ...
  ```

- **Inherited methods require the SAME FULL DESCRIPTION** as own methods. The only difference - add `(inherited from ParentClass)` after the signature or at the end of the description.

**For EACH public element, specify:**

1. **Declarative signature** in a code block. Use the syntax of the project's language:

   Python:

   ```python
   def method_name(param1: Type1, param2: Type2 = default) -> ReturnType:
       ...
   ```

   Kotlin:

   ```kotlin
   fun methodName(param1: Type1, param2: Type2 = default): ReturnType { ... }
   ```

   Java:

   ```java
   public ReturnType methodName(Type1 param1, Type2 param2) { ... }
   ```

   C++:

   ```cpp
   ReturnType methodName(Type1 param1, Type2 param2 = default);
   ```

   TypeScript:

   ```typescript
   methodName(param1: Type1, param2?: Type2): ReturnType { ... }
   ```

   Go:

   ```go
   func (r *Receiver) MethodName(param1 Type1, param2 Type2) ReturnType { ... }
   ```

   Rust:

   ```rust
   fn method_name(&self, param1: Type1, param2: Type2) -> ReturnType { ... }
   ```

   For properties, use the language-specific syntax:
   - Python: `@property`
   - Kotlin: `val prop: Type` / `var prop: Type`
   - Java/C++: `getProp()` / `setProp()` methods
   - TypeScript: `get prop(): Type` / `set prop(value: Type)`

2. **Brief description** (1-2 sentences): what the method/function does.

3. **Important notes** (if any): side effects, what it does NOT do, non-obvious behavior, possible exceptions (`Raises`/`throws`).
   - If the note is short (a word or phrase), it may be included in the description.
   - If there are multiple notes or they require explanation - put them in a separate `**Important notes:**` block.
   - If there are no notes, write: `[no notes]`.

4. **Source** (if the method is inherited or overridden):
   - `(inherited from ParentClass)` - if the method has not been overridden.
   - `(overridden from ParentClass)` - if the method is overridden in the current class.
   - `(implements InterfaceName)` - if the method implements an interface.

**Do NOT include** private methods in this list. Signs of private visibility depend on the language:

- Python: starts with `_` or `__`
- Java/Kotlin: `private` modifier
- C++: `private:` or `protected:` section
- TypeScript/JavaScript: `private` keyword / `#` (private field)
- Go: unexported (starts with lowercase letter)
- Rust: no `pub` / with `pub(crate)` or `pub(super)`

If there are no public methods/functions, write: `[none]`.

---

## Implementation Notes

Non-obvious implementation details: sentinels (special marker values), parameter forwarding, global state, unconventional patterns, decorators/annotations, threads/goroutines, async/coroutines, RAII, smart pointers, lifetimes (Rust).

If a private method is critically important for understanding the architecture - briefly mention it here (without signature or details).

If there are no such details, write: `[none]`.

---

## Handle with Care

What is easy to break:

- **When using:** contracts or invariants that must not be violated (e.g., "transitions must target existing states", "method requires prior call to `is_ready()`", "after calling `close()` the object is unusable", "not thread-safe").
- **When editing this file:** implicit dependencies, coupling with other modules, magic constants, critical code sections, ABI compatibility (C++), database migrations.

If there are no such concerns, write: `[none]`.

---

## Code Style

Conventions used in this file:

- Typing / static analysis (strict, generics/templates, protocols/interfaces/traits)
- Documentation format (Javadoc, Google-style, Sphinx, Doxygen, reST)
- Naming (camelCase, PascalCase, snake_case, kebab-case, UPPER_CASE)
- Visibility (prefixes `_`, `m_`, `private`/`protected` keywords, unexported names)
- Visual separators (e.g., `# ---`, `// MARK:`, comment separators)
- Formatting (indentation, line length, brace placement)

If the file contains no code, write: `[not applicable]`.
````

## Rules

- **Analyze the ENTIRE codebase.** To understand the full list of a class's public methods, trace the entire chain of its parents and interfaces. Do not limit yourself to methods defined in the file itself.
- **Do NOT include private methods in Public API.** Even if they are overridden. Their place is in `Implementation Notes`, if they are important for the architecture.
- **Declarative signatures.** In the code block, write `...` (or `pass`, or `{}`, or `;` - depending on the language) instead of the body. Preserve all type annotations and default values.
- **Pay attention to style.** In the `Code Style` section, reflect not only general language conventions but also project-specific techniques (e.g., long separators, special marker comments).
- **Do not skip methods.** Even if there are many - describe each one individually. This is fundamental for FileSpecContractor.
- **All sections are mandatory.** If a section is empty - write `[none]`. Do not skip a section entirely.
- Be concise. A specification is a map for an LLM agent, not full documentation.
- Specification language: **English** (unless the project's documentation is in another language). Keep class, method, and file names as in the original code.

Now process the provided codebase and output specifications for all files, strictly following the format.

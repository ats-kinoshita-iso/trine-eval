# CLI Tool Evaluation Rubric

## Dimensions and Weights

### Functionality (35%)

| Score | Description |
|-------|-------------|
| 5 | All commands work correctly. Arguments and flags parse as specified. Output format matches spec. Exit codes correct (0 success, non-zero error). |
| 4 | All core commands work. Minor flag combinations may have issues. Output format correct. |
| 3 | Most commands work. One or two have bugs. Some output formatting issues. |
| 2 | Several commands broken. Incorrect exit codes. Output format inconsistent. |
| 1 | Most commands fail. Basic functionality missing. |

### Usability (25%)

| Score | Description |
|-------|-------------|
| 5 | `--help` is comprehensive and accurate. Error messages are actionable. JSON output mode available if specified. Progress indicators for long operations. |
| 4 | Good help text. Most error messages helpful. Output is parseable. |
| 3 | Basic help text. Some error messages vague. Output mostly parseable. |
| 2 | Incomplete help. Error messages unhelpful ("Error occurred"). Output hard to parse. |
| 1 | No help text. Cryptic or missing error messages. Unparseable output. |

### Error Handling (25%)

| Score | Description |
|-------|-------------|
| 5 | Invalid input produces clear errors, not stack traces. Missing required args show usage. File-not-found and permission errors caught. Ctrl+C exits cleanly. |
| 4 | Good error handling. Most invalid inputs caught. Clean exit on interrupt. |
| 3 | Basic error handling. Some invalid inputs produce stack traces. Interrupt handling works. |
| 2 | Many inputs produce stack traces. Missing args cause crashes. |
| 1 | Most errors produce stack traces. The tool crashes on any unexpected input. |

### Code Quality (15%)

| Score | Description |
|-------|-------------|
| 5 | Modular command structure. Shared utilities not duplicated. Config externalized. Tests exist for each command. |
| 4 | Good structure. Minor duplication. Most commands tested. |
| 3 | Reasonable structure. Some duplication. Partial test coverage. |
| 2 | Poor structure. Significant duplication. Few tests. |
| 1 | Monolithic. No separation of concerns. No tests. |

## Hard Thresholds

- **Functionality below 3/5 blocks.** Core commands must work.
- **Any command that produces a stack trace on invalid input is automatic FAIL** for the Error Handling dimension (score capped at 2).

## Testing Tools

- **Command execution:** Run each command with valid and invalid arguments
- **Exit codes:** Check `$?` after each command
- **Help text:** Run `--help` and `-h` for every command and subcommand
- **Error cases:** Pass missing args, invalid files, bad formats, empty input
- **Output parsing:** Pipe output to `jq` (JSON) or `grep` (text) to verify structure
- **Interrupt:** Send SIGINT during long-running operations

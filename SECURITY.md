# Security and privacy

This repository is public, but parking registration details are private.

## Keep private

Never commit:

- property search terms or result labels
- unit or apartment identifiers
- vehicle makes, models, or license plates
- confirmation email addresses
- browser profiles, cookies, screenshots, or registration receipts

Store those values only in `config.toml`, which is ignored by Git.

## Responsible use

Run the workflow only for registrations you are authorized to submit. Review mode is the default so that selector changes or incorrect search results can be caught before an external side effect.

## Reporting a problem

For a privacy or security issue, contact the repository owner privately rather than opening an issue containing real registration data.

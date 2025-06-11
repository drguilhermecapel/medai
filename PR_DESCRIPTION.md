# Remove obsolete Windows installer and fix tests

This update removes the outdated `windows-installer` directory and all related documentation. The installer was no longer functional and caused conflicts during automated test collection. The repository now relies on Docker-based deployment and manual installation guides.

Additionally, the test suite was executed after installing missing dependencies to ensure all remaining tests pass successfully.

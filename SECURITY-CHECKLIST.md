# Security checklist

## A. Account (once)

- [ ] Strong, unique password stored in a password manager
- [ ] Two-factor authentication with an authenticator app (no SMS)
- [ ] Recovery codes downloaded and stored offline
- [ ] Passkey added on a personal device
- [ ] Email kept private and command-line pushes exposing it blocked
- [ ] Push protection and Dependabot enabled for new repositories
- [ ] Public profile limited to professional information
- [ ] Sessions, authorized apps and SSH/GPG keys reviewed
- [ ] Dedicated browser profile for GitHub, separate from personal browsing
- [ ] GitHub signed out of the personal browser profile after authorizing apps

## B. Each new repository

- [ ] Created as **Private**
- [ ] `.gitignore`, `PRINCIPLES.md`, `SECURITY-CHECKLIST.md` and `.githooks/` copied in
- [ ] `git config core.hooksPath .githooks`
- [ ] Commits use the GitHub noreply email
- [ ] Claude GitHub App limited to **selected repositories** only

## C. Before making a repository public (showcase)

- [ ] The project is original work (see `PRINCIPLES.md`)
- [ ] Every file in `examples/` is fictitious
- [ ] The **entire** commit history was reviewed (`git log -p`), not only the latest version
- [ ] Commit messages and pull requests contain nothing personal or professional
- [ ] README explains problem → solution → result → technologies
- [ ] When in doubt about any item: **do not publish**

> If something sensitive was ever committed, deleting the file is not enough: it stays in the history.
> The safest fix is to start a new, clean repository.

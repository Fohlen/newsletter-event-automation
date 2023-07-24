# newsletter-event-automation
Create events from newsletters

### Tasks

- [x] read MBOX file
    - [x] adjust preprocessing (remove footer)
- [x] train classifier for "contains event"
  - [x] store in LFS
- [x] read multiple ICS files and merge them (+ test)
- [x] pass to prompt
- [x] central main.py
  - [x] configuration file
  - [ ] logging config
    - log success rate!
  - [ ] write discarded messages to artifacts
- [ ] update README
  - rename package!
- [ ] update GitHub action
- [ ] add online calendar via GH pages

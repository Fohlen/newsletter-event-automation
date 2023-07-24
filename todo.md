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
  - [x] logging config
    - [x] log success rate!
  - [ ] write discarded messages to artifacts
- [ ] update README
  - [x] rename package!
- [x] update GitHub action
  - [ ] update GH secret
- [ ] add online calendar via GH pages

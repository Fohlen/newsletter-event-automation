# newsletter-event-automation
Create events from newsletters

### Tasks

- [x] read MBOX file
    - [x] adjust preprocessing (remove footer)
- [x] train classifier for "contains event"
  - [x] store in LFS
- [x] filter messages with classifier
  - [ ] retrain model
- [x] filter messages with moderations API
- [x] create iCal file from completion per message
  - [x] fix times
  - [ ] improve prompt for higher coverage
- [x] create cronjob
    - [x] use ~/.mpoprc for fetching mail
    - [x] combine iCals and update / create main iCal file
- [x] add README
    - [x] add mpop example
    - [x] add screenshot
    - [x] "how to add this to your calendar" :)

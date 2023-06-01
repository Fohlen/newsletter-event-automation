newsletter-event-automation
------------------------

This project automatically reads a newsletter to create a calendar feed from it.
In such a way I can focus on the things that are important to me without having to spend 20 minutes out of my day to read emails 🙂

## Add to your own calendar

You can subscribe to this calendar by adding a regular subscription to the following URL:

```
https://raw.githubusercontent.com/Fohlen/newsletter-event-automation/main/schoener-wohnen-verteiler.ics
```

## Architecture

This project is a pipeline powered by [GitHub Actions](https://github.com/features/actions).
The following flowchart, created with [yEd Live](https://www.yworks.com/yed-live/), outlines how it works:

![Architecture picture](data/architecture.svg "Architecture")

### Training the event classifier

Since we pay inference per token, we want to avoid sending emails that do not contain events.
To this end, we use [fasttext](https://fasttext.cc) to build a simple binary classification model.
Using the `make_event_model_dataset` script and then following the steps outlined in the `fasttext` documentation.

### Bias and privacy

As with any modelling process, both `fasttext` and `ChatGPT` contain bias. 
Thus, some events may not be properly recognised or mis-represented. This will give you an overview of your newsletter, but a more thorough system would be necessary to validate that all events are represented correctly.

This project is deliberately kept simple (using only a cronjob and a standard email account), such that we do not rely on cloud services where necessary.
However, at the given point in time, inference can't be done locally. Thus, a select amount of your emails will be processed through ChatGPT.
If you (or the newsletter owner) feel like this is an unbearable violation of privacy, you should not use this project.

## Adapting to your own newsletter

I recognise that this may be beneficial outside the scope of this repository.
If you find newsletter automation useful, take a look at [read_mbox.py](src/read_mbox.py), it is already generic.

HearTheBayes
============

Using Bayes learning from uploaded songs to generate new songs beat-by-beat based on probability.

Two prominent classes:

Learner
-------
Makes heavy use of the EchoNest Remix package and API, which is super awesome. Generates and analyzes an audio file looking for rhythms and pitches, attempting to map the file to what would basically be sheet music.

After mapping out to sheet music treats it the same as a word-babbling algorithm would a page of sentences and words, learning the probabilities by bigram. 

Generator
---------
Writes out audio files given a length, also using the remix package.  This uses the knowledge base of the associated Learner to connect the most probabalistic notes and assigns rhythms in the same manner. The goal for this app is to be able to take in a number of audio files, process them with the learner, and generate audio that combines some of the aspects from all of the input and still sounds decent at the same time.
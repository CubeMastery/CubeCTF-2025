# Nation State Hacking

Author: @B00TK1D

What was the password for the computer used to run the U.S. Air Force Academy's public address system Sound Scheduler in 2019?

Note: This challenge does not require interacting with any US Government systems; do not attempt to gain unauthorized access to any systems. Guessing or contacting people will not solve this challenge, please do not spam submit.

Hint (Released at 24-hour mark): You should commit to searching for acronyms. Don't guess anything, the answer will be extremely clear once you find it.

Flag format: cube{insert_password_here}

# Solution

Googling `USAFA Sound Scheduler` shows the first two results in a repo at https://github.com/USAFA-HAVOC/CWOC-Sound-Scheduler.

Reading through this repo carefully shows that it does not contain any passwords, and also was first created in 2023, but the question asks for the password in 2019.

The next step is to search for earlier versions of this system.  Using the name of the first repo we found, we can search GithHub for `CWOC Sound Scheduler`.

Selecting `Code` as the search target returns 308 results, but the third result (without scrolling) is a repo at https://github.com/sears-s/audio-scheduler.

This preview in the search results page shows the file `Manual/Manual.md`, with instructions for `Logging in to the Laptop`.  Clicking on this file reveals that it contains the full username and password:

```markdown
## CWOC Audio Scheduler Instructions

### Logging in to the Laptop

At all times, the laptop should already by logged in and unlocked with the screen on.

If it is not, you will probably first need to press Ctrl+Alt+Del.

If it asks for a username, use `.\CWOCSoundSys`.

The password for this account is `!QAZ@WSX3edc4rfv`.
```

Therefore, the flag is `cube{!QAZ@WSX3edc4rfv}`.

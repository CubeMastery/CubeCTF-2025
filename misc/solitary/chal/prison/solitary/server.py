import re
import subprocess

print("Welcome to solitary.")
print("Since you're all alone, you might as well do some curls.")
print("Here's a dumbell. What do you want to curl?")

weight = input()

weight = weight.split("\n")[0]

if not re.match(r'[a-z0-9\.\@\-/\: ]+$', weight):
    print("You tried to curl something sharp. That's dangerous.")
    exit(1)

if subprocess.run(["curl"] + weight.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0:
    print("Good job. You're getting stronger.")
else:
    print("You dropped the dumbell. Try again.")

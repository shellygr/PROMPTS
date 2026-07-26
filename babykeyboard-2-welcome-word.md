# Baby keyboard revamped

I want to create a new game based on the current game in the repo.
Let's call the original game Shapes-and-Surprises.
The second game will be called Welcome-Word.
The idea of Welcome-Word is as follows:
1. Each key in the keyboard except for "Esc" is associated with a word in Hebrew. I will attach the list at the end.
2. upon hitting the key, other key strokes are disabled and a sequence is shown on the screen.
2.1. play a sound that I'll record called "3, 4, and", about 2 seconds
2.2. a beat with dots appearing one after the other
2.3. after the sound ends, we see a picture/emoji representing the word plus we play the sound of me saying the word (I'll record later)
2.4. the picture of the word shows for max 5 seconds and then disappears
2.5. after the picture disappears we allow other keystrokes; while it shows other keystrokes are rejected and don't do anything.
3. Mouse should be disabled. Exiting via 5 times hitting "Esc"

Here is a list of required hebrew words:
1. חתול
2. בקבוק
3. מחשב
4. כפית
5. בננה
6. כוס
7. כיסא
8. טלוויזיה
9. משרוקית
10. כלב
11. זאב
12. אופנוע
13. מפתחות
14. אדום
15. צהוב
16. ירוק
17. כחול
18. כתום
19. לבן
20. שחור
22. כובע
23. משקפיים
24. מכנסיים
25. חולצה
26. עט
27. עיפרון

the file structure should be easy to maintain. we can use the numbers above for identification plus an english one-word translation.
then it's my role to add 1. picture files, OR emoji and it's unicode as text; 2. an audio file

there should be a folder for "3, 4 and" files; I'll make several recordings that you can pick randomly for variation.

so overall:
1. start by refactoring the baby-keyboard repo to allow for multiple games each with their own run foler.
2. create shared infrastructure since the games share a lot
3. adjust tests for the original baby-keyboard game
4. implement the new game



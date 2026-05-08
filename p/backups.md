<!-- feature-loop: dee319f2 -->

=== /plan data-management-extended ===
You are now a senior software architect.
we have a script called compare_folders_by_content.py that tells us whether all files from old folder are in the new folder by building hashing indices of each folder.
this script works very well but I would like to generalize it and superpower it in several ways.
1. I would like to make sure we can deal with nested folders properly. Currently it rglobs for cache filenames. This can get tricky if there are many directory levels or potential collisions with CACHE_FILENAME. My idea is that in the root folder we keep a sqlite database mapping each file's hash. the goal here is to check 'set equivalence' not whether the folder structure is the same. sometimes it does matter that files are together in the same directory but for our current concern it does not matter.
2. I do not want to keep a file per subfolder. the database I proposed above should sit at my home folder.
3. I want to be able to deal with remote files on SMB (I am using MacOS everywhere)
4. I would like to get an html report that shows additions and removals clearly and where I can collapse per type of change (addition/removal), filter by filetypes, search by filename/path, and get an rsync command when I click on a file in order to properly sync it.

Do not change compare_folders_by_content.py, but plan a new python project, let's call it backup_helper, using https://github.com/cookiecutter/cookiecutter.

In addition, plan a testing suite that will use DOCKER exclusively! You MUST NOT run it on real files.

--------------------
# Task Manager for Claude and Shelly

## Preliminary question
Suppose I gave you a local web API to submit tasks to, based on a current conversation/session you are in. would you be able to use that to make sure that you have addressed all the relevant tasks? i.e. I would tell you to make sure to exhaust all tasks/notes you were writing there or I was giving you.

## Initial [todo]

I want to build a task manager for you and I.
The idea is that when you detect me giving you a task or I give you one explicitly with /shelly-asks you record it in the task manager.
We will also add a stop-hook for you to make sure that all tasks tied to the current session are handled before moving on.

Here's an inventory of what we need to build:
- a simple webserver with a database, sqlite should suffice, but we need to periodically back it up (i.e. every hour if there were changes).
- an API that can be called by various clients: me on the browser, you from the agent. It should look something like:
POST /tasks           {text, source: "user"|"claude", session}
GET  /tasks?status=open
PATCH /tasks/{id}     {status: done|blocked, result: "..."}
source matters: tasks I gave you should be harder to close than notes I wrote myself, and I should never silently drop a user one.

- a cli tool that you would actually use, I don't want you to call the API directly.
- a web browser frontend that I can access via localhost on port 9999 or some other port number. From there I should be able to see all sessions with tasks within, open new ones (using my own source, not claude source), all sorted in various ways (default: last update, descending newest to oldest), in tabular form with subtasks. it should fully support english and hebrew. there should be a priority tag attached to each. there is an optional repository tag too so we can associated relevant code repos. there should also be a category tag attachable. pleasant coloring. show last backup date of the db and where db backups are stored. I suggest to keep them on git too. note that the web requirements affect also the db schema and the API form. 
- the stop hook that checks for tasks on the current conversation

the repo for this project should be called TaskManagerForAgents, be hosted on shellygr, and there should also be a repo for dbs called TaskManagerForAgentsBackups.

I also want to add an option to put not just tasks but also "Notes". those notes can be useful for you to record memory relevant to a specific conversation and export those into your memory.
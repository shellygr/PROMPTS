<!-- feature-loop: a37c6ca1 -->

=== /plan #1 ===
This is a big project called 'Journey'. The Journey as reflected in my photos which I have taken over many many years. The problem is that the photos are disorganized. First, for every file, different people show up and some of them I do not know. Some I do know very well, but I am curious in particular times where we got together and knowing by the people I would recognize the occassion. 
The other kind of challenge is that sometimes I was taking pictures of a wardrobe/closet. I cannot imagine an LLM will detect what's in the closet, but just by knowing a closet was pictured then I can later tag in greater detail.

What I need is a framework that will do the following:
1. Build a spreadsheet/database from all my image files with columns for filepath, date, location (from picture itself if exists), tags, generated description, and human description. I think it's better if it's sqlite!
2. A preliminary construction of metadata for #1 that can be constructed by classifying the pictures using a local running llm. It could be the case that we sometimes need to run a model good for recognizing people and faces, and sometimes a model good for recognizing what appears. It's an ABSOLUTE MUST that the model runs locally on my machine, an Apple M1 Max, but not sending ANY data outside.
3. It should detect video files metadata but not classify them.
4. A basic GUI tool for macos that shows a gallery with reasonably-sized thumbnails where I can click on a picture and start filling in the columns described in #1. 
5. A RAG database that would then allow a local LLM to answer questions I have (in Hebrew!) about the pictures.

The source of the pictures is potentially a remote-located directory on the local network (on a Mac machine, and we're also running on a Mac). You MUST ONLY USE READ-ONLY access.

This is a complex project with many separate components.
You need to write a large plan file detailing each and every step with maximal detail. There are multiple components here.
Think about my user experience from the moment I select the collections, add new ones to update the database, manually fix or craft additional information, face detection, integrating into the RAG DB (continuously updating with new photos and info on them), and the user facing application of answering questions, with Hebrew support too. Spend as much time as needed on it to make the plan as comprehensive as possible. I will not be available to answer your questions, so please state them directly in the plan, and tomorrow I will respond to you.
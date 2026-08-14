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

----

let's add more words. numbers should be on the numbers row of course.
also, let's support the full sized mac keyboard.
I also want to support multiple recordings per each word if exists, and they can be chosen at random.
finally, add a utility for recording from the command line where i see the word, hit enter, record, then enter again to stop it and you trim accordingly the recording and file it.

so new words:
- 0,1,2,...,9
- ורוד
- לב
- כבשה
- פרה
- תפוח
- אטב
- מחברת
- עץ

i added _some_ images to images folder, rename them accordingly and make sure they render nicely on the screen

----

more words. in case we are overflowing keys, we can move to new "chapters". we can have a transition after 120 keystrokes where we say "פרק הבא" (I'll record it) and then the layout changes to words that belong to that chapter. then we go back to the original chapter 1 even if we have 10 chapters.
- משקפי שמש
- צעצוע
- מפוחית
- אורגנית
- פסנתר
- גיטרה
- כינור
- ספר
- תיק
- עגלה
- חלב
- בייגלה
- לחם
- שולחן
- מיטה
- לול
- תרנגול
- מזלג
- מקרר
- ארון
- מגירה
- מגבת
- סינר
- יוגורט
- מחית
- אגס
- תות
- מנורה
- מתג
- אפרסק
- אמבטיה
- ברז
- מים
- סבון
- ספוג
- עוגיה

--- 

please add the word מאמא

please add וולקי and צב

----

here are some findings from an AI Auditor.
Please fix the first 2 highs for sure.
I would love if there were a way to make the exit keyboard pattern more reliable. I give the kid just the keyboard, so mouse-only may make sense here.

# AI Auditor Report

## Audit Context

- **Repository:** https://github.com/shellygr/baby-keyboard
- **Commit:** `8ac9a35f98339cd9a850b6020ae97d11d10548aa`

### Context
- `BabyKeyboard.swift`
- `BabyKeyboardTests.swift`
- `README.md`

## Summary

- **Total findings:** 15
- **High:** 2
- **Medium:** 1
- **Low:** 12
- **Informational:** 0

## High Severity

### [H-01] Cosmetic lockdown that captures no input — keystrokes and clicks silently reach background applications (combines compiled M-07 + compiled H-03 + compiled H-05)

**Severity:** High

**Locations:**
- [/BabyKeyboard.swift#L970-L978](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L970-L978)
- [/BabyKeyboard.swift#L1204-L1209](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1204-L1209)
- [/BabyKeyboard.swift#L584-L588](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L584-L588)
- [/BabyKeyboard.swift#L695-L703](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L695-L703)
- [/BabyKeyboard.swift#L1015-L1055](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1015-L1055)
- [/BabyKeyboard.swift#L694-L707](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L694-L707)

If the process fails to become the active/frontmost app (absorbed compiled finding M-07: no explicit `.regular` activation policy for an unbundled, shell-launched binary) AND it cannot observe events out of process (absorbed compiled finding H-03: Accessibility is never requested or verified, and/or absorbed compiled finding H-05: the global-monitor token is deallocated), then no input is captured at all — local monitoring requires the app to be active, and global monitoring requires both Accessibility and a retained token. Because `NSApp.presentationOptions` only take effect while the app is frontmost, the dock and menu bar also remain live. The result is a fullscreen black window that *looks* locked but is completely inert: every key the child presses and every click is delivered to whatever real application is behind or beside it (Terminal, Mail, Finder, a browser). A baby mashing the keyboard can execute destructive shell commands, send messages, or delete files while the caregiver believes containment succeeded. This is strictly worse than each constituent: with Accessibility granted, absorbed compiled finding M-07 alone still permits global capture; with the app active, absorbed compiled finding H-03/absorbed compiled finding H-05 alone still permit local capture. Only the combination yields a total, silent containment bypass with integrity impact on unrelated applications.

### Absorbed compiled findings
- Absorbed compiled finding M-07: Shell-launched builds may be unable to become the active application
- Absorbed compiled finding H-03: System-level, firmware, and cursor-triggered inputs bypass containment
- Absorbed compiled finding H-05: Event monitor observer tokens are instantly discarded, breaking background key monitoring and focus recovery

#### Recommendation

Set `.regular` activation policy and confirm frontmost status before declaring the session "locked"; request and verify Accessibility at startup, failing visibly if absent; retain monitor tokens; and refuse to run (or display a warning overlay) whenever input capture cannot be positively confirmed.

### [H-02] Sustained infant key-mashing exhausts main-thread/GPU/audio resources and renders the timing-based exit unreliable (combines compiled M-05 + compiled M-11 + compiled M-06 + compiled H-01)

**Severity:** High

**Locations:**
- [/BabyKeyboard.swift#L790-L855](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L790-L855)
- [/BabyKeyboard.swift#L856-L862](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L856-L862)
- [/BabyKeyboard.swift#L420-L424](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L420-L424)
- [/BabyKeyboard.swift#L604-L607](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L604-L607)
- [/BabyKeyboard.swift#L186-L193](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L186-L193)
- [/BabyKeyboard.swift#L221-L279](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L221-L279)
- [/BabyKeyboard.swift#L799-L813](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L799-L813)
- [/BabyKeyboard.swift#L1078-L1094](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1078-L1094)

The app's intended workload — a baby continuously mashing keys, amplified by unfiltered auto-repeat (absorbed compiled finding H-01) — is precisely what triggers all three resource defects at once: unbounded `milestoneLayers` growth with O(N²) removal scans on the main thread (absorbed compiled finding M-05), per-frame offscreen shadow-blur recomputation on dozens of mutating layers lacking `shadowPath` (compiled finding M-11), and priority-inverting `NSLock` contention inside the real-time audio render callback (compiled finding M-06). Together they saturate the main run loop and GPU under exactly the conditions the app is built to sustain, driving the process into unresponsiveness. The ESC×5 exit depends on the main thread timestamping five key events within a 3-second sliding window (absorbed compiled finding H-01); when event delivery is delayed, coalesced, or dropped under this load, the caregiver's exit attempts become unreliable at the worst possible time. Three individually "performance-grade" issues thus compound into a safety-relevant availability failure — the containment becomes hardest to exit exactly when it is most out of control — which is strictly more severe than any constituent alone.

### Absorbed compiled findings
- Absorbed compiled finding M-05: Unbounded milestone effects growth and O(N²) cleanup exhaust UI resources
- Absorbed compiled finding H-01: Ordinary child input (auto-repeat, key mashing, mouse clicks) can easily terminate the containment session

#### Recommendation

Hard-cap and time-throttle all effect and milestone layers; use container-layer or index-based cleanup instead of repeated array scans; assign an explicit `shadowPath` to animated layers; replace the audio `NSLock` with a lock-free SPSC/atomic mechanism; ignore `event.isARepeat`; and make the exit path independent of main-thread load.


## Medium Severity

### [M-01] Input-driven resource exhaustion can make hazardous flashing impossible to stop promptly (combines compiled H-02 + compiled H-07 + compiled M-05)

**Severity:** Medium

**Locations:**
- [/BabyKeyboard.swift#L317-L509](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L317-L509)
- [/BabyKeyboard.swift#L619-L862](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L619-L862)
- [/BabyKeyboard.swift#L979-L1078](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L979-L1078)
- [/BabyKeyboard.swift#L1082-L1098](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1082-L1098)

absorbed compiled finding H-07 allows an unrestricted key stream, including auto-repeat, to generate overlapping high-contrast fullscreen animations. The same stream triggers milestone effects every 20 events; under absorbed compiled finding M-05, these add uncapped layers and increasingly expensive array scans on the main thread. Once the main event loop is saturated, mouse-click and ESC×5 exits cannot be processed promptly, while already-committed Core Animation effects may continue rendering. compiled finding H-02 then prevents ordinary external termination and repeatedly interferes with attempts to recover through another application. This turns a stoppable visual hazard and an application-level resource issue into a safety-critical incident where a caregiver may be unable to halt flashing without a forced hardware action.

### Absorbed compiled findings
- Absorbed compiled finding H-07: Unthrottled high-contrast animations create a photosensitive-seizure hazard
- Absorbed compiled finding M-05: Unbounded milestone effects growth and O(N²) cleanup exhaust UI resources

#### Recommendation

Apply a centralized input and visual-output rate limit, reject auto-repeat events, cap milestone layers, and replace scan-based cleanup with bounded container removal. Preserve an emergency termination mechanism that remains available during main-thread or rendering overload, and respect Reduce Motion and photosensitivity limits.


## Low Severity

### [L-01] Global event monitor forwards out-of-focus keystrokes to visual/audio and exit logic

**Severity:** Low

**Locations:**
- [/BabyKeyboard.swift#L695-L703](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L695-L703)
- [/BabyKeyboard.swift#L735-L749](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L735-L749)
- [/BabyKeyboard.swift#L1035-L1051](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1035-L1051)
- [/BabyKeyboard.swift#L1054-L1076](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1054-L1076)
- [/BabyKeyboard.swift#L1078-L1098](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1078-L1098)
- [/BabyKeyboard.swift#L1078-L1114](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1078-L1114)
- [/BabyKeyboard.swift#L1106-L1148](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1106-L1148)
- [/BabyKeyboard.swift#L1166-L1188](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1166-L1188)
- [/BabyKeyboard.swift#L1200-L1224](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1200-L1224)

The application uses an observational global event monitor to catch keystrokes when it loses focus. However, the global monitor forwards every observed keyboard event into the same `handleKeyEvent` function used for application-local input. When a child (or parent) types into another active application, the global monitor routes these events through internal logic, triggering visual animations, audio feedback, and privileged exit logic like the 5-press Escape sequence. This allows an observational API to make a privileged control-flow decision, falsely reinforces the child's actions outside containment, and visually discloses potentially sensitive keystrokes typed elsewhere.

#### Recommendation

Separate local and global event processing. The global monitor should only attempt focus recovery and should never invoke visual, audio, counter, or exit logic. Invoke `checkEscExit` and animation generation exclusively from the local event path after confirming `NSApp.isActive` and that the configured window is key.

### [L-02] Invalid presentation options raise an uncatchable Objective-C exception

**Severity:** Low

**Locations:**
- [/BabyKeyboard.swift#L671-L688](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L671-L688)
- [/BabyKeyboard.swift#L1011-L1033](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1011-L1033)

The code attempts to handle presentation option failures using a Swift `do` block. However, invalid presentation options raise an Objective-C `NSException`, which Swift cannot catch natively. If the app fails to apply its initial constraints (e.g., because it hasn't fully gained active status), it crashes immediately on startup rather than gracefully executing its intended fallback configuration.

#### Recommendation

Use a small Objective-C wrapper to safely `@try/@catch` the `presentationOptions` assignment, or only apply the constraints after explicitly confirming that the application is truly active and frontmost.

### [L-03] Debug mode acts as a system-wide keylogger

**Severity:** Low

**Locations:**
- [/BabyKeyboard.swift#L755-L757](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L755-L757)
- [/BabyKeyboard.swift#L1044-L1050](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1044-L1050)
- [/BabyKeyboard.swift#L1046-L1054](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1046-L1054)
- [/BabyKeyboard.swift#L1107-L1109](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1107-L1109)
- [/BabyKeyboard.swift#L1112-L1114](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1112-L1114)
- [/README.md#L19-L21](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/README.md#L19-L21)

When run with `--debug`, the application writes raw key codes and modifiers to `NSLog`. Because it processes events via a global event monitor, it also receives and logs keystrokes typed into other applications whenever the application loses focus. `NSLog` writes directly to the macOS unified logging system, which is persistent, meaning user passwords and sensitive messages from other apps may be recorded in plaintext.

#### Recommendation

Do not log keystrokes obtained from the global monitor. If diagnostic logging is necessary, explicitly check that the application holds primary focus (`NSApp.isActive`), securely redact sensitive key codes, and write to an isolated local file instead of the unified system log.

### [L-04] Display topology changes can strand the window or crash the application

**Severity:** Low

**Locations:**
- [/BabyKeyboard.swift#L873-L875](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L873-L875)
- [/BabyKeyboard.swift#L984-L986](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L984-L986)
- [/BabyKeyboard.swift#L988-L1012](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L988-L1012)
- [/BabyKeyboard.swift#L1189-L1198](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1189-L1198)
- [/BabyKeyboard.swift#L1194-L1202](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1194-L1202)

The application resolves a target screen index once from `NSScreen.screens` at launch but accesses the array directly later without re-validating bounds. Disconnecting a display can cause a fatal out-of-bounds crash. Furthermore, the application fails to monitor for subsequent screen topology changes; if displays are reconfigured, the protective window can be stranded off-screen while the lockdown and refocus blocks remain active.

#### Recommendation

Re-validate indices against current display array boundaries. Subscribe to `NSApplication.didChangeScreenParametersNotification` to listen for screen changes, dynamically updating or relocating lockdown windows whenever hardware displays change.

### [L-05] Concurrent application instances create competing lockdown sessions

**Severity:** Low

**Locations:**
- [/BabyKeyboard.swift#L970-L1074](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L970-L1074)
- [/BabyKeyboard.swift#L1160-L1164](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1160-L1164)
- [/BabyKeyboard.swift#L1204-L1209](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1204-L1209)

There is no process-wide singleton enforcement. Invoking the executable multiple times creates independent processes that compete for foreground ownership. Each creates windows, hides cursors, disables system presentation features, and starts refocus timers. Multiple instances multiply audio engines, and exiting one instance only exposes another beneath it, significantly complicating recovery.

#### Recommendation

Acquire a per-user, process-wide lock (e.g., a file lock) before activating the application or applying any system-wide side effects to prevent concurrent instances.

### [L-06] Notifications and focus-stealing system interruptions are not suppressed

**Severity:** Low

**Locations:**
- [/BabyKeyboard.swift#L989-L1014](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L989-L1014)
- [/BabyKeyboard.swift#L1016-L1039](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1016-L1039)

The application never enables a Focus / Do-Not-Disturb mode and does not use native full-screen presentation. Consequently, macOS continues to deliver notification banners, incoming call alerts, and focus-stealing system prompts (e.g., permission requests, low battery). When these surface on top of the containment window, the child can interact with them, open other apps, and breach containment.

#### Recommendation

Enable a Focus/Do-Not-Disturb session or present the containment surface via native full-screen to suppress notification banners. Explicitly re-assert key-window status when focus-stealing panels appear.

### [L-07] Audio engine is not restarted on configuration changes

**Severity:** Low

**Locations:**
- [/BabyKeyboard.swift#L217-L292](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L217-L292)

The `AVAudioEngine` is started once during initialization but does not listen for `AVAudioEngineConfigurationChangeNotification`. Hardware changes, such as unplugging headphones, stop the engine. Because it never restarts automatically, the application permanently loses audio feedback capabilities.

#### Recommendation

Observe the `AVAudioEngineConfigurationChangeNotification` and restart the `AVAudioEngine` upon detection of hardware route changes.

### [L-08] Display-sleep prevention can fail silently

**Severity:** Low

**Locations:**
- [/BabyKeyboard.swift#L1053-L1063](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1053-L1063)

The application attempts to prevent display sleep by calling `IOPMAssertionCreateWithName` but ignores the return result. If the assertion fails due to resource pressure or IOKit errors, the display may unexpectedly sleep or lock during a containment session without any notification.

#### Recommendation

Check the return value of `IOPMAssertionCreateWithName` against `kIOReturnSuccess`. Retry with a backoff or use a `ProcessInfo` activity fallback if it fails.

### [L-09] Safety-critical exit logic is untested due to duplicated re-implementation

**Severity:** Low

**Locations:**
- [/BabyKeyboardTests.swift#L9-L32](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboardTests.swift#L9-L32)
- [/BabyKeyboard.swift#L799-L813](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L799-L813)
- [/BabyKeyboard.swift#L826-L845](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L826-L845)

The automated tests validate a duplicated `EscExitTracker` class rather than the real exit logic in `AppDelegate.checkEscExit`. This leaves the real safety-critical exit mechanism unverified and susceptible to regressions, while creating false confidence via tests that can diverge from the shipping code.

#### Recommendation

Extract the exit state machine into a distinct, importable type that does not depend on AppKit or top-level side effects. Consume this single implementation in both the application and the test suite.

### [L-10] Unclosed subpath and incorrect curve generation in the heart shape creates a prominent visual artifact

**Severity:** Low

**Locations:**
- [/BabyKeyboard.swift#L145-L155](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L145-L155)

In the `createShapePath` generation logic for the `.heart` shape, `path.move(to:)` is called between the two lobes. Because `closeSubpath()` only closes the most recently opened subpath, Core Graphics draws a straight line connecting the end of the right lobe back to the top-middle, dividing the shape in half with a prominent white stroke.

#### Recommendation

Draw the heart as a single continuous path without interrupting it with `move(to:)`.

### [L-11] The "Layer 2" local event monitor is redundant with the sendEvent override

**Severity:** Low

**Locations:**
- [/BabyKeyboard.swift#L881-L911](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L881-L911)
- [/BabyKeyboard.swift#L1041-L1057](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1041-L1057)

The event-handling code includes a local `NSEvent` monitor ("Layer 2") that never executes. Because the `sendEvent` override ("Layer 1") catches keyboard events and returns without calling `super.sendEvent`, the local monitor's handler is never invoked. This dead code presents a false sense of defense-in-depth.

#### Recommendation

Remove the redundant local monitor or make it the single authoritative interception point, rather than maintaining a non-functional parallel path.

### [L-12] Parent silently misdirected to lock the wrong monitor while the child's screen stays fully interactive (combines compiled L-02 + compiled M-01)

**Severity:** Low

**Locations:**
- [/BabyKeyboard.swift#L8-L41](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L8-L41)
- [/BabyKeyboard.swift#L1194-L1202](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L1194-L1202)
- [/BabyKeyboard.swift#L649-L668](https://github.com/shellygr/baby-keyboard/blob/8ac9a35f98339cd9a850b6020ae97d11d10548aa/BabyKeyboard.swift#L649-L668)

absorbed compiled finding L-02 causes an invalid or mistyped `--screen` argument to silently fall back to the main screen instead of erroring, and absorbed compiled finding M-01 leaves every non-covered display completely unprotected (the hidden cursor moves there freely and clicks land on the live desktop). Chained, a caregiver who intends to lock the child onto screen 2 but mistypes the index gets the app locked onto screen 1 (their own screen), while screen 2 — the display physically in front of the child — remains a fully interactive desktop with keyboard and mouse. Because the caregiver sees a "locked" screen and reasonably concludes containment worked, the deception makes this strictly worse than either finding alone: absorbed compiled finding L-02 by itself might still land on a covered display, and absorbed compiled finding M-01 by itself assumes the correct primary was selected; together they guarantee the child's specific display is unprotected under a false sense of safety.

### Absorbed compiled findings
- Absorbed compiled finding L-02: Invalid screen arguments silently fall back to a different display
- Absorbed compiled finding M-01: Secondary displays are neither covered nor monitored

#### Recommendation

Strictly validate `--screen` and refuse to launch with a clear terminal error on invalid input; cover every screen in `NSScreen.screens` with a shield window (or route/deny pointer and key events originating from uncovered displays).


-----


can we disable function keys completely? they let the baby turn off sound or brightness freely


# SCIO clone plan

This is the plan I’d hand the team before anyone opens an empty repo. Not a clone of every toggle in the current product. A clone of the job the product actually does: take a screen in a real place, tell it what to play, and not make the manager think about the player OS all day.

I spent time in the live trial (`app.optisigns.com`) and the help center, not just the marketing site. What follows is scoped like we’d have to ship it.

## What I’d actually build

One web CMS (the thing they call SCIO) plus **one** player. The player is a first-class product, not a webview we bolt on in month five.

**In for MVP**

- Login, one org, invite a couple of teammates with admin vs editor
- Pair a screen with a short code the device shows
- Heartbeat so the CMS knows the box is online
- Upload images and video, store on object storage + CDN
- Assign **one** thing to a screen: an asset, a playlist, or a schedule
- Playlists with duration
- A simple schedule (time of day + the device’s timezone)
- One player: Android **or** a web player we can demo in a browser. Pick Android if the first customers are firesticks/cheap boxes; pick web player if we need a demo Friday. I’d pick **web player first**, Android second. Same assignment API.

**Out on purpose**

- Power BI / Tableau / “secured dashboard” login-on-the-TV stuff
- The designer with a thousand templates (that’s a different product)
- Kiosk / Engage / touch
- Wireless presentation
- Roku, tvOS, ChromeOS, Fire, Windows, Mac as day-one targets
- Sync Play, content tags, campaign rules
- Fancy analytics
- Split screen except maybe a dumb 2-zone layout at the end if we have slack. Help center even says split screen is missing on Roku and Apple TV, so “it works on any screen” is already a lie if we promise feature parity.

If someone asks why we aren’t cloning the app store: because the core loop is pair → show one file. Apps are how they sell. We can add YouTube / website / weather **after** playlists exist.

## Team and calendar

Four people, sixteen weeks to an MVP a restaurant could actually use on one TV.

That’s 64 person-weeks. Not three months of “full OptiSigns.” I’d staff it as:

- 2 on CMS (screens, assets, playlists, schedule UI + API)
- 1 on player + pairing + offline cache
- 1 on media pipeline (upload, transcode a reasonable 1080p, CDN) and glue

One person for eight weeks only gets a spike: web player, images, no real schedule, no team invite. I’d say that out loud rather than pretend.

## Order, and why that order

The only demo that matters is: pair a device, upload a picture, see it on the screen. Playlist without that is an admin UI for a product that doesn’t exist.

| When | What | Why this before the next thing |
| --- | --- | --- |
| Weeks 1–2 | Auth, org, empty Screens list | Need a place to land the pair code |
| Weeks 3–5 | Pairing, heartbeat, assign one asset, web player | This **is** the product |
| Weeks 6–7 | S3/CDN, video transcode that’s “good enough” | Raw 4K will melt a cheap stick |
| Weeks 8–9 | Playlists | Nobody runs a store on one still image |
| Weeks 10–11 | Schedule + timezone on the device | Lunch menu vs dinner menu is the first real customer ask |
| Weeks 12–13 | Invite + roles | Second location, intern who shouldn’t delete everything |
| Weeks 14–16 | YouTube / website / weather as apps, buffer for pairing bugs | Sales-facing, not foundation |

I would not build split screen before playlists. The help center pushes it because it screenshots well. Nested split-screen-inside-playlist can loop; they even warn you. v1 either forbids nesting or skips split screen.

## How the system is shaped

Two programs, not one:

- CMS in the browser talks to an API and a database
- The player is a box that **pulls** an assignment and then pulls media. We are not Chromecast and we are not Netflix.

Rough pieces: Postgres, a boring REST API, object storage, a player that polls or holds a websocket for “your assignment changed.” Offline: keep the last package and keep playing. Don’t gold-plate sync in v1.

Screen assignment is a tagged union: `asset | playlist | schedule`. That matches how the live UI actually works (Edit Screen → Type). Composition lives **inside** playlist/split-screen assets, not as a tree of layouts hanging off every TV. I would keep that model. It’s simpler than a general scene graph and it’s what operators already understand.

## One thing I did not expect

I expected the TV to log in. It doesn’t.

The player shows a pair code. You type that code in the CMS. The screen is a device; the human lives in the browser. Once I saw that, a bunch of “smart TV app with username/password” designs went in the trash.

It also locked the sequencing: weeks 3–5 are pairing and assignment, not a content designer. And it locked the device matrix: if we chase eight OS ports before pairing is boringly reliable, we’ll ship eight half-dead players. Roku/Apple TV already don’t do split screen in the real product. MVP is one player that pairs every time, not a compatibility spreadsheet.

There’s a second surprise sitting next to that: the help center still documents **two** portals (1.0 and 2.0). I would not clone both. One IA, closer to the current Screens / Files / Playlists / Schedules tabs. No migration story in v1 because we have no v0 customers.

## Numbers I’d defend in a room

- Pairing + one-asset playback: 3 weeks for the player person plus CMS help, because the failure modes are dumb (clock, network, TV sleep, code expired) and that’s where support tickets come from.
- Playlist 2 weeks: ordered list, duration, preview. Nested playlists slip to later; nested anything is how you get loops.
- Schedule 2 weeks: recurrence and overlap are the part people underestimate. v1 is “this block on these weekdays,” last-write-wins if two blocks overlap, default fallback asset. I am not building a timezone product for a global airline in v1 — we use the device local time, which is what OptiSigns already documents.
- Apps 3 weeks at the end: three web-ish apps, not fifty integrations.

If we slip, I cut apps and roles first, not pairing.

## What I’d say on day 0

We’re building a CMS and a player that can run a shop’s TV from a laptop. We’re not rebuilding the app marketplace, the designer, or every set-top OS. The unexpected bit — pairing, not login-on-the-TV — is why the first milestone is a code on a screen and a JPEG, not a Figma file.

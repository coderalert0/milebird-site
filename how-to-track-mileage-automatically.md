# How to track mileage for taxes automatically on iPhone

> Use a mileage app that detects drives in the background, and give it Location set to Always with Precise Location on, plus Motion & Fitness and Background App Refresh. Leave it running, then once a week mark each drive business or personal and add the business purpose, so your log is kept at or near the time, as the IRS expects.

Source page: https://coderalert0.github.io/milebird-site/how-to-track-mileage-automatically.html
Checked against its sources on November 11, 2026. Published by Milebird, an automatic mileage tracker for iPhone. Not tax advice.

## Why automatic beats remembering

The IRS asks you to record each business use of your car "at or near the time," and it won't accept miles you "approximate or estimate" ([IRS Publication 463](https://www.irs.gov/publications/p463)). A weekly log counts as timely; a year's drives pieced together in April from memory and a map does not hold up as well.

An automatic tracker writes the parts that are hard to remember (the date, where each drive started and ended, and the miles) as you drive. What's left for you is the part only you know: whether the drive was for business, and why. See [what an IRS mileage log must show](https://coderalert0.github.io/milebird-site/irs-mileage-log-requirements.md).

## How an iPhone knows you're driving

A mileage app can't keep the GPS on all day without draining the battery, so a well-made tracker works in two modes:

- **Between drives,** it asks iOS to wake it when you've moved, for example when you leave a place you've stopped at, and it reads the iPhone's motion activity (walking, still, or in a vehicle) from Motion & Fitness. The GPS stays off.
- **During a drive,** it turns the GPS on and records the route, so the miles come from the road you actually drove.

That only works if the app is allowed to use your location in the background. iOS asks for that permission separately, and once you've allowed it, Apple explains, "your device will remind you from time to time that an app is using your location," shows those locations on a map and asks whether to keep allowing it. If you want drives logged with the app closed, keep allowing it.

## The settings that keep it logging

| Setting | Where on the iPhone | Why it matters |
|---|---|---|
| Location: **Always** | Settings › Privacy & Security › Location Services › the app | With While Using, drives are logged only while the app is open |
| **Precise Location** on | The same screen | Turned off, the app gets only your approximate location, which is too coarse to measure a drive's miles |
| **Motion & Fitness** on | Settings › Privacy & Security › Motion & Fitness | Tells walking from driving, so drives start and end at the right moment |
| **Background App Refresh** on | Settings › General › Background App Refresh | Lets iOS run the app in the background |
| **Low Power Mode** off, when you can | Settings › Battery | Apple lists it as turning off Background App Refresh, among other things |

Two habits matter as much as the switches:

- **Don't force-quit the app.** Swiping a tracker away in the app switcher stops it, which can cut off a drive in progress. There's no battery to save by closing it.
- **Open it now and then.** A good tracker tells you on screen when a permission is off; you'll only see that if you look.

## A weekly five-minute routine

1. **Sort the week's drives.** Mark each one business or personal, and add a short business purpose ("site visit, Acme", "client meeting"). Publication 463 counts a log kept weekly as timely.
2. **Check what the app flagged.** Train rides, rides as a passenger and anything that doesn't look like your driving should be marked as not a drive.
3. **Look for gaps.** Compare against your calendar. If a business drive is missing, add it now, while you remember it, rather than at tax time.
4. **Keep commuting out.** Driving between home and your regular workplace is personal commuting, even if you take work calls on the way. See [the commuting rules](https://coderalert0.github.io/milebird-site/irs-mileage-log-requirements.md).
5. **Export a copy now and then.** Save a CSV or the app's report somewhere other than the phone, such as iCloud Drive or your email.

## Check the rate by date

The IRS raised its rates in the middle of 2026: business miles driven from January 1 to June 30, 2026 are worth 72.5 cents each, and miles from July 1, 2026 are worth 76 cents ([IRS standard mileage rates](https://www.irs.gov/tax-professionals/standard-mileage-rates)). A tracker should value each drive at the rate in force on its date, not apply one rate to the whole year.

## At year end

- **Total miles for the year.** The IRS wants the car's total miles, not just the business ones, and Schedule C asks you to split them into business, commuting and other. An odometer reading at the start and end of the year gives you the total.
- **Export the full log** with every drive's date, places, miles and purpose, and keep it with your tax records for at least 3 years after you file.

## Frequently asked questions

### Do mileage tracking apps drain the battery?

It depends on how they use the GPS. A tracker that keeps GPS on all day uses far more power than one that waits for iOS to wake it when you move and runs GPS only while you drive. Settings › Battery on your iPhone shows how much each app has used.

### Why does my iPhone keep asking whether to allow location in the background?

iOS reminds you from time to time when an app uses your location in the background, shows where it was used, and asks whether to keep allowing it. A mileage tracker needs that permission to log drives with the app closed, so choose to keep allowing it.

### Does Low Power Mode stop mileage tracking?

Apple says Low Power Mode turns off Background App Refresh, among other things. How much that affects a tracker depends on the app: some keep logging but may notice the start of a drive later. Turn Low Power Mode off when you can, and check the app if drives seem to be missing.

### Is an app's log good enough for the IRS?

IRS Publication 463 says a record prepared on a computer is considered an adequate record. The log still has to show each business drive's date, destination, purpose and miles, and be kept at or near the time.

## Sources

- [IRS Publication 463 (2025), Travel, Gift, and Car Expenses](https://www.irs.gov/publications/p463)
- [IRS: Standard mileage rates](https://www.irs.gov/tax-professionals/standard-mileage-rates)
- [Apple: Control the location information you share on iPhone](https://support.apple.com/guide/iphone/control-the-location-information-you-share-iph3dd5f9be/ios)
- [Apple: About privacy and Location Services in iOS, iPadOS, and watchOS](https://support.apple.com/en-us/102515)
- [Apple: Use Low Power Mode to save battery life on your iPhone or iPad](https://support.apple.com/en-us/101604)

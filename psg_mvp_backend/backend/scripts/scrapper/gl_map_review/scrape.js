/**
 * This file is to scrape ALL reviews on Google map.
 *
 * Example:
 *      > node scrape.js 悠美診所 站前店 ChIJ15RhJXOpQjQRej72613a5ps "https://www.google.com/maps/search/?api=1&query=121.515835,25.045417&query_place_id=ChIJ15RhJXOpQjQRej72613a5ps"
 *      > node scrape.js 美麗線時尚診所 總店 ChIJw0rqwxkWaTQRPVYDjGc_Yc0 "https://www.google.com/maps/search/?api=1&query=120.6393406,24.1828851&query_place_id=ChIJw0rqwxkWaTQRPVYDjGc_Yc0"
 *
 * @type {Puppeteer}
 */

const readline = require('readline');
const fs = require('fs');
const puppeteer = require('puppeteer'); // Require the Package we need...


// return;
// for (let j = 0; j < process.argv.length; j++) {
//     console.log(j + ' -> ' + (process.argv[j]));
// }

// const readInterface = readline.createInterface({
//     input: fs.createReadStream('./urls.txt'),
//     // output: process.stdout,
//     console: false
// });

// readInterface.on('line', function (line) {
//     // console.log(line);
//     const inputArr = line.split(',');
//     const clinicName = inputArr[0];
//     const branchName = inputArr[1];
//     const placeId = inputArr[2];
//     const tmpUrl = inputArr[3];
//     // console.log(clinicName + " | " + branchName + " | " + placeId + " | "+ tmpUrl);
//
//     if (clinicName === clinicName) {
//         console.log(clinicName + " | " + branchName + " | " + placeId);
//     }


(async () => { // Prepare scrape...

    const clinicName = process.argv[2];
    const branchName = process.argv[3];
    const placeId = process.argv[4];
    const tmpUrl = process.argv[5];

    try {
        console.log("clinic:", clinicName);
        console.log("branchName:", branchName);
        console.log("placeId:", placeId);
        console.log("tmpUrl:", tmpUrl);

        if (tmpUrl == "missing") {
            throw "missing url"
        }

        let fs = require("fs")

        if (fs.existsSync(`./output/comments_${clinicName}_${branchName}_${placeId}.json`)) {
            console.log('Found file -- exiting script');
            return
        }

        if (fs.existsSync(`./output/error_comments_${clinicName}_${branchName}_${placeId}.json`)) {
            console.log('Found error file -- exiting script');
            return
        }

        //const browser = await puppeteer.launch({devtools:true,args: ['--no-sandbox', '--disabled-setuid-sandbox']}); // Prevent non-needed issues for *NIX
        //const browser = await puppeteer.launch({devtools:true,args: ['--no-sandbox', '--disabled-setuid-sandbox', '--lang=zh-tw,zh']}); // Prevent non-needed issues for *NIX

        const browser = await puppeteer.launch({args: ['--no-sandbox', '--disabled-setuid-sandbox', '--lang=zh-tw,zh']});
        const page = await browser.newPage(); // Create request for the new page to obtain...

        await page.setExtraHTTPHeaders({
            'Accept-Language': 'zh'
        });

        await page.goto(tmpUrl); // Define the Maps URL to Scrape...
        // await page.goto('https://www.google.com/maps/place/教主醫美整形外科診所+BishopClinic+台北店/@25.026861,121.523035,17z/data=!3m1!4b1!4m7!3m6!1s0x3442a99af4bb24a5:0x4724a1a3c15e614b!8m2!3d25.026861!4d121.523035!9m1!1b1'); // Define the Maps URL to Scrape...
        await page.waitFor(5000); // In case Server has JS needed to be loaded...

        //const moreReviewsBtnSelector = 'button[aria-label^="More reviews"]'
        const moreReviewsBtnSelector = 'button[aria-label^="更多评价"]'

        const linkHandlers = await page.$(moreReviewsBtnSelector);

        if (linkHandlers != null) {
            console.log("Found: " + moreReviewsBtnSelector);

            await linkHandlers.click();

            await Promise.all([
                page.waitForNavigation(),
                page.click(moreReviewsBtnSelector)
            ]);
        } else {
            console.log("There's no" + moreReviewsBtnSelector + " btn.")
            throw "No `More Reviews` button"
        }

        var result_f = [];

        var scrollEnd = false;

        // one time scroll to bottom!
        var prevScrollTop = 0;
        let scrollFailures = 0
        try {
            while (!scrollEnd) {
                let currentScrollHeight = 0
                let currentScrollTop = 0
                let afterScrollTop = 0

                try {
                    currentScrollHeight = await page.evaluate('document.querySelector(\'div.section-scrollbox\').scrollHeight');
                    currentScrollTop = await page.evaluate('document.querySelector(\'div.section-scrollbox\').scrollTop');
                    console.log("height & top", currentScrollHeight, currentScrollTop);
                    await page.evaluate(`document.querySelector('div.section-scrollbox').scrollTo(0, ${currentScrollHeight})`);
                    await page.waitFor(1000);

                    // srcollHeight is fixed, use scrollTop to see the current scroll offset.
                    afterScrollTop = await page.evaluate('document.querySelector(\'div.section-scrollbox\').scrollTop');
                    console.log("after scroll top", afterScrollTop)
                }catch(e){
                    if (scrollFailures > 5){
                        throw "Too many scroll failures!"
                    }
                    scrollFailures++
                    console.log('failure during scrolling -- continuing')
                    await page.waitFor(1000);
                    continue
                }
                scrollFailures = 0;

                if (afterScrollTop == currentScrollTop && currentScrollTop != 0){
                    debugger
                    console.log("=====seems we reached scroll end...rc2");
                    scrollEnd = true
                }

                if (afterScrollTop >= prevScrollTop) {
                    prevScrollTop = afterScrollTop;
                } else {
                    scrollEnd = true;
                    console.log("=====seems we reached scroll end...");
                }
                console.log("===============");
            }
        } catch (e) {
            console.log(e)
            console.log("no scroll");
        }

        await page.waitFor(1000); // In case Server has JS needed to be loaded...

        const result = await page.evaluate(()=>{
            // update these one day by right click element and select copy selector and change to "INDEX"; same for maxIndex && more reviews button
            userSelector  = "#pane > div > div.widget-pane-content.cYB2Ge-oHo7ed > div > div > div.section-layout.section-scrollbox.cYB2Ge-oHo7ed.cYB2Ge-ti6hGc > div:nth-last-child(2) > div:nth-child(INDEX) > div > div.ODSEW-ShBeI-content > div.ODSEW-ShBeI-RWgCYc.ODSEW-ShBeI-RWgCYc-SfQLQb-BKD3ld > div > div > a > div.ODSEW-ShBeI-title > span"
            ratingSelector = "#pane > div > div.widget-pane-content.cYB2Ge-oHo7ed > div > div > div.section-layout.section-scrollbox.cYB2Ge-oHo7ed.cYB2Ge-ti6hGc > div:nth-last-child(2) > div:nth-child(INDEX) > div > div.ODSEW-ShBeI-content > div:nth-child(3) > div.ODSEW-ShBeI-jfdpUb > span.ODSEW-ShBeI-H1e3jb"
            reviewSelector  = "#pane > div > div.widget-pane-content.cYB2Ge-oHo7ed > div > div > div.section-layout.section-scrollbox.cYB2Ge-oHo7ed.cYB2Ge-ti6hGc > div:nth-last-child(2) > div:nth-child(INDEX) > div > div.ODSEW-ShBeI-content > div:nth-child(3) > div.ODSEW-ShBeI-ShBeI-content > span.ODSEW-ShBeI-text"
            imageSelector = "#pane > div > div.widget-pane-content.cYB2Ge-oHo7ed > div > div > div.section-layout.section-scrollbox.cYB2Ge-oHo7ed.cYB2Ge-ti6hGc > div:nth-last-child(2) > div:nth-child(INDEX) > div > div.ODSEW-ShBeI-content > div:nth-child(1) > a > img"
            dateSelector  = "#pane > div > div.widget-pane-content.cYB2Ge-oHo7ed > div > div > div.section-layout.section-scrollbox.cYB2Ge-oHo7ed.cYB2Ge-ti6hGc > div:nth-last-child(2) > div:nth-child(INDEX) > div > div.ODSEW-ShBeI-content > div:nth-child(3) > div.ODSEW-ShBeI-jfdpUb > span.ODSEW-ShBeI-RgZmSc-date"
            let maxIndex
            try {
                maxIndex = document.querySelector('div[data-review-id^="C"]').parentElement.childElementCount
            }catch(e){
                console.error("no data-review-id^=\"C\"")
                throw "NO data-review-id!"
            }

            let items = []

            for (let i = 0; i <= maxIndex; i++) {
                try {
                    // change the index to the next child
                    console.log(userSelector.replace("INDEX", i))
                    let user = document.querySelector(userSelector.replace("INDEX", i)).innerText
                    console.log(user)
                    let rating = document.querySelector(ratingSelector.replace("INDEX", i)).attributes["aria-label"].value
                    console.log(rating)
                    let review = document.querySelector(reviewSelector.replace("INDEX",i)).innerText
                    console.log(review)
                    let image = document.querySelector(imageSelector.replace("INDEX",i)).src
                    console.log(image)
                    let date = document.querySelector(dateSelector.replace("INDEX",i)).innerText
                    console.log(date)

                    if (user != "" && review != "") {
                        items.push({
                            //'clinic': clinicName,
                            //'branch': branchName,
                            //'placeId': placeId,
                            'user': user,
                            'date': date,
                            'rating':rating,
                            'review': review,
                            'image': image,
                        });
                    }

                    console.log(user,rating,review,image,date)
                }
                catch(e){
                    console.log(e)
                    console.log("no item here")
                }
            }
            //console.log(items)
            debugger
            return items;
        })

        console.log(result.length);

        // Close the Browser...
        browser.close();

        var obj = {
            comments: result
        };
        var json_data = JSON.stringify(obj);
        //let fs = require('fs');

        fs.writeFile(`./output/comments_${clinicName}_${branchName}_${placeId}.json`, json_data, 'utf8', function (err) {
            if (err) {
                return console.log(err);
            }
            console.log("File saved successfully!");
        });

        // Return the results with the Review...
        return result;
    } catch (e) {
        let error_data = {
            "command":`os.system('cd gl_map_review; node scrape.js ${clinicName} ${branchName} ${placeId} "${tmpUrl}"')`,
            "clinicName":clinicName,
            "branchName":branchName,
            "placeId":placeId,
            "url":tmpUrl,
            "error":e,
        }


        let json_data = JSON.stringify(error_data)
        console.log(json_data)

        console.log("final catch block" + e);
        fs.writeFileSync(`./output/error_comments_${clinicName}_${branchName}_${placeId}.json`, json_data, 'utf8', function (err) {
            if (err) {
                console.log(err);
                return console.log(err);
            }
            console.log("Caught final error - error writing to file ",e);
        });
        console.log("Caught final error - wrote error file");
        process.exit(0)
    }

})();
